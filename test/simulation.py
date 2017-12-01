import argparse
import emulation.GTAEventsReader
import time
import os
import subprocess
import sys
from threading import Thread
from threading import Lock
from decimal import Decimal
from common.constants import init_logger, logger


LOCATION_CLIENT_APP_WINDOWS = '..\\client\\app.py'
LOCATION_CLIENT_APP_LINUX = '../client/app.py'

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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Simulation")

    parser.add_argument("--elap-time", dest="simulationElapsedTimeInSeconds", default=30)
    parser.add_argument("--delayBetweenEvents", dest="timeBetweenEvents", default=0.5)
    parser.add_argument("--gta-file", dest="gtaFilename", default='WoWSession_Node_Player_Fixed_Dynamic_reduced.zip')

    args = parser.parse_args()

    init_logger("log/simulation_{}.log".format(time.time()))

    # Assigning the parameters received in the command line to the variables which will be used for the simulation
    simulationElapsedTimeInSeconds = int(args.simulationElapsedTimeInSeconds)
    timeBetweenEvents = float(args.timeBetweenEvents)
    gtaFilename = args.gtaFilename

    # This list will contain pairs of players and the associated process.
    global playersAndProcesses
    playersAndProcesses = {}

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
    else:
        # Windows file structure
        clientAppLocation = os.path.join(fileDir, LOCATION_CLIENT_APP_WINDOWS)

    # List of events still considering the timestamps read from the GTA file
    listOfEvents = emulation.GTAEventsReader.LoadEventsFromFile(gtaFilename)

    # Normalize the timeStamps of the Login/Logout events using the time between the the first and last login/logout events
    listOfNormalizedEvents = emulation.GTAEventsReader.NormalizeEvents(listOfEvents, simulationElapsedTimeInSeconds)

    logger.info("Total number of Login/Logout events: " + str(len(listOfNormalizedEvents)))

    logger.info("Starting the simulation.")

    triggerJoinLeaveEvents(listOfNormalizedEvents, lock, clientAppLocation, timeBetweenEvents)

    print("This is the end of the simulation.")

