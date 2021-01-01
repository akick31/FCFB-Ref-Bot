import re
from game_database_functions import updateTime
from game_database_functions import updateQuarter
from game_database_functions import updateGameStatus
from game_database_functions import getGameInfo
from game_database_functions import updateClockStopped

guildID = 398332149335326720

"""
Utility functions for the game that may be usefil

@author: apkick
"""

def representsInt(string):
    """
    Check to see if the string can be an int
    
    """

    try: 
        int(string)
        return True
    except ValueError:
        return False
    
    
def hasNumbers(inputString):
    """
    Check if a string has a number, useful for determining if play call is valid
    
    """

    return any(char.isdigit() for char in inputString)

 
def convertYardLine(gameInfo):
    """
    Convert field position to 0-100
    
    """

    yardLine = gameInfo["yard line"] 
    convertedYardLine = 100
    if(gameInfo["possession"] == gameInfo["home name"]):
        if gameInfo["home name"] == yardLine.rsplit(' ', 1)[0]:
            numList = list(map(int, re.findall(r'\d+', yardLine)))
            convertedYardLine = 100-numList[0]
        else:
            numList = list(map(int, re.findall(r'\d+', yardLine)))
            convertedYardLine = numList[0]
    else:
        if gameInfo["away name"] == yardLine.rsplit(' ', 1)[0]:
            numList = list(map(int, re.findall(r'\d+', yardLine)))
            convertedYardLine = 100-numList[0]
        else:
            numList = list(map(int, re.findall(r'\d+', yardLine)))
            convertedYardLine = numList[0]
    return convertedYardLine


def convertYardLineBack(yardLine, gameInfo):
    """
    Convert field position from 0-100
    
    """

    if(gameInfo["possession"] == gameInfo["home name"]):
        if int(yardLine) > 50:
            return gameInfo["home name"] + " " + str(100-yardLine)
        elif int(yardLine) < 50:
            return gameInfo["away name"] + " " + str(yardLine)
        else:
            return "50"
    else:
        if int(yardLine) > 50:
            return gameInfo["away name"] + " " + str(100-yardLine)
        elif int(yardLine) < 50:
            return gameInfo["home name"] + " " + str(yardLine)
        else:
            return "50"
    

def convertDown(down):
    """
    Convert down to show on discord
    
    """

    if down == "1":
        down = "1st"
    elif down == "2":
        down = "2nd"
    elif down == "3":
        down = "3rd"
    elif down == "4":
        down = "4th"
    return down


def getDiscordUser(client, user):
    """
    Get the user object from Discord
    
    """

    guild = client.get_guild(guildID)
    user = user.strip()
    for member in guild.members:
        if("#" in user):
            if str(member.name.strip()) == str(user.split("#")[0].strip()):
                return member
        else:
            if member.name.strip() == user.strip():
                return member
                
    return "COULD NOT FIND"


async def messageUser(client, discordUser, gameInfo, time):
    """
    Message the defending team
    
    """

    down = convertDown(str(gameInfo["down"]))
    
    directMessage = ("**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + gameInfo["possession"] + "\n\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n\n"
                     + "Please submit a number between 1-1500, inclusive")
    await discordUser.send(directMessage)
    

async def messageConfirmationUser(client, discordUser, number):
    """
    Send confirmation of the user's defensive number
    
    """

    directMessage = ("I have " + str(number) + " as your number")
    await discordUser.send(directMessage)
    
     
def calculateDifference(offense, defense):
    """
    Calculate the difference in the numbers
    
    """    

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
 

def convertTime(channel, gameInfo, timeOff):
    """
    Convert the time and take it off the clock in the database
    
    """

    minutes, seconds = gameInfo["time"].split(':')
    time = int(minutes) * 60 + int(seconds)
    time = int(time) - int(timeOff)
    if time < 0:
        finalTime = "7:00"
        quarter = int(gameInfo["quarter"]) + 1
        if quarter > 4 and int(gameInfo["home score"]) != int(gameInfo["away score"]) and gameInfo["game status"] != "OVERTIME":
            updateGameStatus(channel, "FINISHED")
        elif quarter > 4 and int(gameInfo["home score"]) == int(gameInfo["away score"]):
            updateGameStatus(channel, "OVERTIME")
        updateQuarter(channel, quarter)
        updateTime(channel, finalTime)
        updateClockStopped(channel, "YES")
    else:
        minutes = int(time / 60)
        seconds = int(time % 60)
        if seconds < 10:
            finalTime = str(minutes) + ":0" + str(seconds)
            updateTime(channel, finalTime)
        else:
            finalTime = str(minutes) + ":" + str(seconds)
            updateTime(channel, finalTime)
        
    return finalTime


def getClockRunoff(message, offensivePlaybook, clockRunoffType):
    """
    Get the clock runoff based on the offensive playbook and return it
    
    """

    clockRunoff = 0
    gameInfo = getGameInfo(message.channel)
    clockStopped = gameInfo["clock stopped"]
    # Add clock runoff
    if clockStopped == "NO":
        if clockRunoffType == "normal":
            if offensivePlaybook == "flexbone":
                clockRunoff = 20
            if offensivePlaybook == "west coast":
                clockRunoff = 17
            if offensivePlaybook == "pro":
                clockRunoff = 15
            if offensivePlaybook == "spread":
                clockRunoff = 13
            if offensivePlaybook == "air raid":
                clockRunoff = 10
        elif clockRunoffType == "chew":
            clockRunoff = 30
        elif clockRunoffType == "hurry":
            clockRunoff = 7
        return clockRunoff
    else:
        return 0
        