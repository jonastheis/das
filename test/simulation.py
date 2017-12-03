import argparse
import emulation.GTAEventsReader
import time
import os
import subprocess
import sys
from threading import Thread
from threading import Lock
from decimal import Decimal
from common.constants import init_logger
import logging

SIMULATION_SERVERS_WARMUP_TIME = 3
logger = logging.getLogger("sys." + __name__.split(".")[-1])

LOCATION_CLIENT_APP_WINDOWS = '..\\client\\app.py'
LOCATION_CLIENT_APP_LINUX = '../client/app.py'

LOCATION_SERVER_APP_WINDOWS = '..\\server\\app.py'
LOCATION_SERVER_APP_LINUX = '../server/app.py'

# This method adds a client to the simulation.
# Input: lock: lock object for concurrency control,
# event_details: the details related to the connection of the client to the simulation.
# adjTimestamp: an adjustment on the timestamp to discount the time that took for the event to be triggered.
# Output: none.
def addClient(lock, event_details, clientApp, adjTimestamp):

    # If the delayed time is longer than the timestamp in which the event should be trigger, the sleep is skiped and
    # the event is triggered automatically.

    if event_details.timeStamp - Decimal(adjTimestamp) > 0:
        time.sleep(event_details.timeStamp - Decimal(adjTimestamp))

    # command line to start the client application: python ../client/app.py --log-prefix player_id
    proc = subprocess.Popen([sys.executable, clientApp, '--log-prefix', event_details.playerId])

    logger.debug("This is the playerId: " + event_details.playerId + " and this is the PID:" + str(proc.pid))

    with lock:
        playersAndProcesses[event_details.playerId] = proc.pid

    logger.info("Player: " + event_details.playerId + " joining the game.")

    return

# This method removes a client to the simulation.
# Input: lock: lock object for concurrency control,
# event_details: the details related to the connection of the client to the simulation.
# adjTimestamp: an adjustment on the timestamp to discount the time that took for the event to be triggered.
# isWindows: if the current execution is on Windows.
# Output: none.

def removeClient(lock, event_details, isWindows, adjTimestamp):

    with lock:
        numberOfPlayers = len(playersAndProcesses)

    if numberOfPlayers > 0:

        if event_details.timeStamp - Decimal(adjTimestamp) > 0:
            time.sleep(event_details.timeStamp - Decimal(adjTimestamp))

        if not isWindows:
            commandLine = "kill -9 " + str(playersAndProcesses[event_details.playerId])
        else:
            #Killing the process using a Windows command
            commandLine = "taskkill /f /pid " + str(playersAndProcesses[event_details.playerId])

        # Executing the command to kill the respective process.
        os.system(commandLine)

        with lock:
            playersAndProcesses[event_details.playerId] = None
            numberOfPlayers = len(playersAndProcesses)

        logger.info("Player: " + event_details.playerId + " leaving the game.")
    else:
        logger.info("This player currently doesn't have an active session, so no Logout action will be performed.")
        return

    if numberOfPlayers == 0:
        logger.info("This was the last player to leave the game, end of simulation.")

def triggerJoinLeaveEvents(listOfEventsToTrigger, lock, clientApp, delayBetweenEvents):
    listOfThreads = []
    adjustmentTimestamp = 0
    for event in listOfEventsToTrigger:

        if event.eventType == emulation.GTAEventsReader.PLAYER_LOGIN:
            thread = Thread(target=addClient, args=(lock, event, clientApp, adjustmentTimestamp,))
            thread.start()
            listOfThreads.append(thread)
        else:
            if event.eventType == emulation.GTAEventsReader.PLAYER_LOGOUT:
                thread = Thread(target=removeClient, args=(lock, event, runningWindows, adjustmentTimestamp,))
                thread.start()
                listOfThreads.append(thread)

        time.sleep(delayBetweenEvents)
        adjustmentTimestamp += delayBetweenEvents

    # Waits for all threads to finish
    for single_thread in listOfThreads:
        single_thread.join()

def initializeServers(serverApp, configFile, base_port, port_offset, numSlaveServers):

    # Starting the base server
    # command line to start the base server: python ../server/app.py --log-prefix player_id
    proc = subprocess.Popen([sys.executable, serverApp, '--config', configFile, '--log-prefix', 'master_node', '--port', str(base_port)])

    if proc.pid > 0:
        logger.info("Base Server successfully added. Process Id: " + str(proc.pid))
        serverProcesses.append(proc.pid)
    else:
        logger.error("Error while loading the base server. Simulation will be aborted.")
        return
    time.sleep(SIMULATION_SERVERS_WARMUP_TIME)

    # Initializing the slave servers for simulation
    i = 1
    while i <= numSlaveServers:
        proc = subprocess.Popen([sys.executable, serverApp, '--config', configFile, '--log-prefix', 'slave_' + str(i), '--port', str(base_port + port_offset)])

        if proc.pid > 0:
            logger.info("Slave Server " + str(i) + " successfully added. Process Id:" + str(proc.pid))
            serverProcesses.append(proc.pid)
        else:
            logger.error("Error while loading slave server " + str(i) + ".")
        i += 1

    time.sleep(SIMULATION_SERVERS_WARMUP_TIME)
    return

# This kills the processes used for the simulation.
# isWindows: if the current execution is on Windows.
# Output: none.

def killServers(isWindows):

    with lock:
        numberOfProcesses = len(serverProcesses)

    if numberOfProcesses > 0:

        for serverProcess in serverProcesses:
            if not isWindows:
                commandLine = "kill -9 " + str(serverProcess)
            else:
                #Killing the process using a Windows command
                commandLine = "taskkill /f /pid " + str(serverProcess)

            logger.info("Removing the server process:" + str(serverProcess))
            # Executing the command to kill the respective process.
            os.system(commandLine)

    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Simulation")

    # Parameters related to the simulation
    parser.add_argument("--elap-time", dest="simulationElapsedTimeInSeconds", default=30)
    parser.add_argument("--delayBetweenEvents", dest="timeBetweenEvents", default=0.5)
    parser.add_argument("--gta-file", dest="gtaFilename", default='WoWSession_Node_Player_Fixed_Dynamic_reduced.zip')
    # Parameters related to the servers used in the simulation
    parser.add_argument("--base-port", dest="basePort", default=7000)
    parser.add_argument("--port-offset", dest="portOffset",default=1000)
    parser.add_argument("--num-slave-servers", dest="numSlaveServers",default=2)
    parser.add_argument("--server-config", dest="serverConfig", default="das_config.json")


    args = parser.parse_args()

    init_logger("log/simulation_{}.log".format(time.time()))

    # Assigning the parameters received in the command line to the variables which will be used for the simulation
    simulationElapsedTimeInSeconds = int(args.simulationElapsedTimeInSeconds)
    timeBetweenEvents = float(args.timeBetweenEvents)
    gtaFilename = args.gtaFilename
    base_port = int(args.basePort)
    port_offset = int(args.portOffset)
    numSlaveServers = int(args.numSlaveServers)
    configurationFile = args.serverConfig

    # This list will contain pairs of players and the associated process.
    global playersAndProcesses
    playersAndProcesses = {}

    # List of processes related to the servers used in the simulation (master + slaves)
    serverProcesses = []

    # This lock is used to implement concurrency control on the list of players and processes which will be shared
    # accros multiple threads.
    lock = Lock()

    runningWindows = False
    if os.name == 'nt':
        runningWindows = True

    fileDir = os.path.dirname(os.path.realpath('__file__'))

    # Depending on the OS in which the simulation is running the way in which the client and server are invoked is
    # different.
    if not runningWindows:
        clientAppLocation = os.path.join(fileDir, LOCATION_CLIENT_APP_LINUX)
        serverAppLocation = os.path.join(fileDir, LOCATION_SERVER_APP_LINUX)
    else:
        # Windows file structure
        clientAppLocation = os.path.join(fileDir, LOCATION_CLIENT_APP_WINDOWS)
        serverAppLocation = os.path.join(fileDir, LOCATION_SERVER_APP_WINDOWS)

    # List of events still considering the timestamps read from the GTA file
    listOfEvents = emulation.GTAEventsReader.LoadEventsFromFile(gtaFilename)

    # Normalize the timeStamps of the Login/Logout events using the time between the the first and last login/logout events
    listOfNormalizedEvents = emulation.GTAEventsReader.NormalizeEvents(listOfEvents, simulationElapsedTimeInSeconds)

    logger.info("Total number of Login/Logout events: " + str(len(listOfNormalizedEvents)))

    logger.info("Starting the simulation.")
    logger.info("Initializing servers.")
    initializeServers(serverAppLocation, configurationFile, base_port, port_offset, numSlaveServers)

    logger.info("Triggering events.")
    triggerJoinLeaveEvents(listOfNormalizedEvents, lock, clientAppLocation, timeBetweenEvents)

    logger.info("Killing the processes related to the servers.")
    killServers(runningWindows)

    print("This is the end of the simulation.")

