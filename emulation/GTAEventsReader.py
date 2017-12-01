import itertools
import re
import common.event
import zipfile
import os
import time
from decimal import localcontext, Decimal

# This auxiliary class has methods to support the manipulation of GTA (Game Track Activity) files.
PLAYER_QUITING = " PLAYER_QUITING"
PLAYER_LOGOUT = " PLAYER_LOGOUT"
PLAYER_LOGIN = " PLAYER_LOGIN"


class GTAEventsReader:

    def __init__(self):
        self.type = type(self).__name__

# This method identifies the Login/Logout events from the GTA file and returns a list of Event objects.
# Input: a GTA file with a list of events
# Output: a list of Event objects
def IdentifyLoginLogoutEvents(onlyEvents):

    listOfLoginLogoutEvents = []
    timeOfFirstEvent = 0

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
          " - Parsing the file to extract target events (Login/Logout).")

    for contentEntry in onlyEvents:
        information = contentEntry.split(',')

        eventTime = float(information[2])

        if timeOfFirstEvent > eventTime or timeOfFirstEvent == 0:
            timeOfFirstEvent = eventTime

        if (PLAYER_LOGIN == information[3]) or (PLAYER_LOGOUT == information[3]) or (PLAYER_QUITING == information[3]):

            playerId = information[1]

            if(PLAYER_QUITING != information[3]):
                eventType = information[3]
            else:
                eventType = PLAYER_LOGOUT

            detectedEvent = common.event.Event(eventType, playerId, eventTime)

            listOfLoginLogoutEvents.append(detectedEvent)

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
          " - Parsing process is done.")

    return listOfLoginLogoutEvents

# This method loads the events contained in a GTA file.
# Assuming that the lines in the file will follow the format present in
# WoWSession_Node_Player_Fixed_Dynamic which is: RowID, PlayerID, Timestamp, Event, Category.
# Input: file location
# Output: a list of Event objects.

def LoadEventsFromFile(fileLocation):

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
          " - Extracting the zip file containing the events: " + fileLocation)

    initialZipFile = zipfile.ZipFile(fileLocation,'r')
    initialZipFile.extractall()

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
          " - File extracted successfully.")

    # Removing the extension of the zip file: '.zip' assuming that the input file has the same name as the zip file.
    extractedFileLocation = fileLocation[:-4]

    eventsFile = open(extractedFileLocation, 'r')

    listOfLoginLogoutEvents = []
    eventsExists = False

    nonContentLines = 0
    for entry in eventsFile:
        # Checking if it is not a comment line, if so skip.
        if "#" in entry:
            nonContentLines += 1
            continue
        else:
            # Checking if it is the file header, if so skip.
            if (re.match(r"[a-zA-Z]", entry) != None):
                nonContentLines += 1
                continue
            else:
                # This is the start of the file content, so iteration will start below
                eventsExists = True
                break

    eventsFile.seek(0,0)

    # Proceeds with event identification only if there are events in the input file.
    if (eventsExists):
        # Uses as input for the event extraction only the part of the input file with events (without headers).
        onlyEvents = itertools.islice(eventsFile, nonContentLines, None)

        # Now the Login/Logout events will be extracted.
        listOfLoginLogoutEvents = IdentifyLoginLogoutEvents(onlyEvents)

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
          " - Closing the extracted file: " + extractedFileLocation)

    # Closing the file extracted file
    eventsFile.close()

    #Removing the extracted file
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
          " - Removing the extracted file: " + extractedFileLocation)

    os.remove(extractedFileLocation)

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
          " - Closing the zip file: " + fileLocation)

    # Closing the file zip file
    initialZipFile.close()

    return listOfLoginLogoutEvents

# This function normalizes the events timestamps based on a given/target simulation total time.
# Complexity O(n) - iterates twice over the list of events
# Input: A list of non-normalized events
# Output: A list of normalized events
def NormalizeEvents(listOfEvents, newElapsedTimeFrame):

    normalizedEvents = []

    if len(listOfEvents) > 0:

        timeOfFirstEvent = listOfEvents[0].timeStamp
        timeOfLastEvent = listOfEvents[0].timeStamp

        # Identification of the first and last events
        for event in listOfEvents:
            if timeOfFirstEvent > event.timeStamp:
                timeOfFirstEvent = event.timeStamp
            else:
                if timeOfLastEvent < event.timeStamp:
                    timeOfLastEvent = event.timeStamp

        # Computation of the total elapsed time.
        eventsElapsedTime = timeOfLastEvent - timeOfFirstEvent

        print("Time read from the GTA file: StartTime: " +
              time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeOfFirstEvent)) + " EndTime: " +
              time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeOfLastEvent)))

        # Computes the normalized timestamp and creates a new Event object which will be added to a new list of Events
        for event in listOfEvents:

            eventTime = Decimal(event.timeStamp) - Decimal(timeOfFirstEvent)

            newTimeStamp = Decimal(newElapsedTimeFrame * (eventTime)) / Decimal(eventsElapsedTime)

            normalizedEvent = common.event.Event(event.eventType, event.playerId, newTimeStamp)

            normalizedEvents.append(normalizedEvent)

    return normalizedEvents


