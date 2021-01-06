import re
from game_database_functions import updateTime, updatePossession, updatePlayType, updateHalftime, updateDistance, \
    updateDown, updateAwayTimeouts, updateHomeTimeouts, getGameInfo, updateClockStopped, updateQuarter, updateGameStatus

guildID = 398332149335326720

"""
Utility functions for the game that may be useful

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


def getScoreboardString(message, difference, down, possessingTeam, waitingOnUser):
    """
    Get the scoreboard string for the message on Discord

    """

    gameInfo = getGameInfo(message.channel)
    if gameInfo["clock stopped"] == "YES":
        scoreBoard = ("**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n"
                    + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n"
                    + "**Difference:** " + str(difference) + "\n\n"
                    + "==========================\n"
                    + "**Q" + str(gameInfo["quarter"]) + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                    + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + possessingTeam + "\n"
                    + "The clock is stopped\n"
                    + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                    + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                    + "==========================\n"
                    + "\n\n**Waiting on " + waitingOnUser.mention + " for a number.**\n\n")
    else:
        scoreBoard = ("**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n"
                      + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n"
                      + "**Difference:** " + str(difference) + "\n\n"
                      + "==========================\n"
                      + "**Q" + str(gameInfo["quarter"]) + " | " + str(gameInfo["time"]) + " | " + str(
                    gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(
                    gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                      + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(
                    gameInfo["yard line"]) + " | :football: " + possessingTeam + "\n"
                      + "The clock is moving\n"
                      + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                      + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                      + "==========================\n"
                      + "\n\n**Waiting on " + waitingOnUser.mention + " for a number.**\n\n")
    return scoreBoard

 
def convertYardLine(gameInfo):
    """
    Convert field position to 0-100
    
    """

    yardLine = gameInfo["yard line"]
    if gameInfo["possession"] == gameInfo["home name"]:
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

    if gameInfo["possession"] == gameInfo["home name"]:
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
        if "#" in user:
            if str(member.name.strip()) == str(user.split("#")[0].strip()):
                return member
        else:
            if member.name.strip() == user.strip():
                return member
                
    return "COULD NOT FIND"


async def messageUser(discordUser, gameInfo):
    """
    Message the defending team
    
    """

    down = convertDown(str(gameInfo["down"]))
    
    directMessage = ("**Q" + str(gameInfo["quarter"]) + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + gameInfo["possession"] + "\n\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n\n"
                     + "Please submit a number between 1-1500, inclusive")
    await discordUser.send(directMessage)
    

async def messageConfirmationUser(discordUser, number):
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

async def handleHalftime(client, message, gameInfo):
    """
    Handle halftime updates for the DB and set up the kickoff

    """

    updatePlayType(message.channel, "KICKOFF")
    updateClockStopped(message.channel, "YES")

    if gameInfo["coin toss winner"] == gameInfo["home user"] and gameInfo["coin toss decision"] == "receive":
        updatePossession(message.channel, gameInfo["away name"])  # home team is kicking off
        await message.channel.send("It is halftime, " + gameInfo["away name"] + " is kicking off")
    elif gameInfo["coin toss winner"] == gameInfo["home user"] and gameInfo["coin toss decision"] == "defer":
        updatePossession(message.channel, gameInfo["home name"])  # home team is receiving
        await message.channel.send("It is halftime, " + gameInfo["home name"] + " is kicking off")
    elif gameInfo["coin toss winner"] == gameInfo["away user"] and gameInfo["coin toss decision"] == "receive":
        updatePossession(message.channel, gameInfo["home name"])  # away team is kicking off
        await message.channel.send("It is halftime, " + gameInfo["home name"] + " is kicking off")
    elif gameInfo["coin toss winner"] == gameInfo["away user"] and gameInfo["coin toss decision"] == "defer":
        updatePossession(message.channel, gameInfo["away name"])  # away team is receiving
        await message.channel.send("It is halftime, " + gameInfo["away name"] + " is kicking off")

    gameInfo = getGameInfo(message.channel)
    if str(gameInfo["possession"]) == str(gameInfo["home name"]):
        waitingOnUser = getDiscordUser(client, str(gameInfo["home user"]))
    else:
        waitingOnUser = getDiscordUser(client, str(gameInfo["away user"]))
    await message.channel.send("Please ignore all DMs sent immediately before halftime\n"
                               + "**Waiting on " + waitingOnUser.mention + " for a message")
    await messageUser(waitingOnUser, gameInfo)

    updateHomeTimeouts(message.channel, 3)
    updateAwayTimeouts(message.channel, 3)
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    updateHalftime(message.channel, "NO")