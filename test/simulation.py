import emulation.GTAEventsReader
import time
import os
import subprocess
import sys
from threading import Thread
from threading import Lock
from decimal import Decimal


# This method adds a client to the simulation.
# Input: lock: lock object for concurrency control,
# event_details: the details related to the connection of the client to the simulation.
# adjTimestamp: an adjustment on the timestamp to discount the time that took for the event to be triggered.
# Output: none.

def addClient(lock, event_details, adjTimestamp):
    time.sleep(event_details.timeStamp - Decimal(adjTimestamp))

    proc = subprocess.Popen([sys.executable, clientAppLocation, '--log-prefix', event_details.playerId])

    print("This is the playerId: " + event_details.playerId + " and this is the PID:" + str(proc.pid))

    with lock:
        processesAndPlayers[event_details.playerId] = proc.pid

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
          " - Player: " + event_details.playerId + " joining the game.")

    return

# This method removes a client to the simulation.
# Input: lock: lock object for concurrency control,
# event_details: the details related to the connection of the client to the simulation.
# adjTimestamp: an adjustment on the timestamp to discount the time that took for the event to be triggered.
# Output: none.

def removeClient(lock, event_details, adjTimestamp):

    with lock:
        numberOfPlayers = len(processesAndPlayers)

    if numberOfPlayers > 0:
        time.sleep(event_details.timeStamp - Decimal(adjTimestamp))
        if runningLinux:
            comandLine = "kill -9 " + str(processesAndPlayers[event_details.playerId])
        else:
            #Killing the process using a Windows command
            comandLine = "taskkill /f /pid " + str(processesAndPlayers[event_details.playerId])

        os.system(comandLine)

        with lock:
            processesAndPlayers[event_details.playerId] = None
            numberOfPlayers = len(processesAndPlayers)

        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
              " - Player: " + event_details.playerId + " leaving the game.")
    else:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
              " - This player currently doesn't have an active session, so no Logout action will be performed.")
        return

    if numberOfPlayers == 0:
        print("This was the last player to leave the game, end of simulation.")

if __name__ == "__main__":

    runningLinux = True
    if os.name == 'nt':
        runningLinux = False

    # Time in seconds for the simulation
    simulationElapsedTimeInSeconds = 30
    timeBetweenEvents = .5

    global processesAndPlayers
    processesAndPlayers = {}

    fileDir = os.path.dirname(os.path.realpath('__file__'))

    lock = Lock()

    if runningLinux:
        clientAppLocation = os.path.join(fileDir, '../client/app.py')
    else:
        # Windows file structure
        clientAppLocation = os.path.join(fileDir, '..\\client\\app.py')

    print("This is the location of the clientApp:" + clientAppLocation)

    listOfEvents = emulation.GTAEventsReader.LoadEventsFromFile('WoWSession_Node_Player_Fixed_Dynamic_reduced.zip')

    # Normalize the timeStamps of the Login/Logout events using the time between the the first and last login/logout events
    listOfNormalizedEvents = emulation.GTAEventsReader.NormalizeEvents(listOfEvents, simulationElapsedTimeInSeconds)

    print("Total number of Login/Logout events: " + str(len(listOfNormalizedEvents)))

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
          " - Starting the simulation.")

    listOfThreads = []
    adjustmentTimestamp = 0
    for event in listOfNormalizedEvents:

        if event.eventType == emulation.GTAEventsReader.PLAYER_LOGIN:
            thread = Thread(target=addClient, args=(lock, event, adjustmentTimestamp, ))
            thread.start()
            listOfThreads.append(thread)
        else:
            if event.eventType == emulation.GTAEventsReader.PLAYER_LOGOUT:
                thread = Thread(target=removeClient, args=(lock, event, adjustmentTimestamp, ))
                thread.start()
                listOfThreads.append(thread)

        time.sleep(timeBetweenEvents)
        adjustmentTimestamp += timeBetweenEvents

    # Waits for all threads to finish
    for single_thread in listOfThreads:
        single_thread.join()

    print ("This is the end of the simulation.")

