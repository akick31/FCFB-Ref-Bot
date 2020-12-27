from game_database_functions import updateTime
from game_database_functions import updateQuarter
from game_database_functions import updateGameStatus

"""
Created on Wed May 13 19:38:06 2020

@author: apkick
"""

"""
Check to see if the string can be an int

"""
def representsInt(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False
     
"""
Calculate the difference

"""     
def calculateDifference(offense, defense):
    if representsInt(str(offense)) and representsInt(str(defense)):
        offense = int(offense)
        defense = int(defense)
        difference = abs(offense-defense)
        if difference > 750:
            return 1500-difference
        else:
            return difference      
    else:
        return -1
 
"""
Convert the time and take it off the clock

"""
def convertTime(channel, gameInfo, timeOff):
    minutes, seconds = gameInfo["time"].split(':')
    time = int(minutes) * 60 + int(seconds)
    previousTime = time
    time = time - timeOff
    if time < 0:
        finalTime = "7:00"
        quarter = int(gameInfo["quarter"]) + 1
        if quarter > 4 and int(gameInfo["home score"]) != int(gameInfo["away score"]) and gameInfo["game status"] != "OVERTIME":
            updateGameStatus(channel, "FINISHED")
        elif quarter > 4 and int(gameInfo["home score"]) == int(gameInfo["away score"]):
            updateGameStatus(channel, "OVERTIME")
        updateQuarter(channel, quarter)
        updateTime(channel, finalTime)
    else:
        minutes = time / 60
        seconds = time % 60
        finalTime = str(minutes) + ":" + str(seconds)
        updateTime(channel, finalTime)
        
    return finalTime
        