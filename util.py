from game_database_functions import updateTime
from game_database_functions import updateQuarter
from game_database_functions import updateGameStatus

guildID = 723390838167699508

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
Check if a string has a number, useful for determining if play call is valid

"""
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)
    
"""
Convert down to show on discord

"""
def convertDown(down):
    if down == "1":
        down = "1st"
    elif down == "2":
        down = "2nd"
    elif down == "3":
        down = "3rd"
    elif down == "4":
        down = "4th"
    return down

"""
Get the user object

"""
def getDiscordUser(client, user):
    guild = client.get_guild(guildID)
    for member in guild.members:
        if member.name == user.split("#")[0]:
            return member
    return "COULD NOT FIND"


"""
Message the defending team

"""
async def messageUser(client, discordUser, gameInfo, time):
    down = convertDown(str(gameInfo["down"]))
    
    directMessage = ("\n\n\n**" + str(gameInfo["home name"]) + ":** " + str(gameInfo["home score"]) + " | Timeouts: " + str(gameInfo["home timeouts"]) + "\n"
                     + "**" + str(gameInfo["away name"]) + ":** " + str(gameInfo["away score"]) + " | Timeouts: " + str(gameInfo["away timeouts"]) + "\n"  
                     + "Q" + str(gameInfo["quarter"])  + " | " + str(time) + " | " + down + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | " + str(gameInfo["possession"]) + " :football:\n\n"
                     + "Please submit a number between 1-1500, inclusive")
    await discordUser.send(directMessage)
    
"""
Send confirmation of the user's defensive number

"""
async def messageConfirmationUser(client, discordUser, number):
    directMessage = ("I have " + str(number) + " as your number")
    await discordUser.send(directMessage)
    
    
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
        minutes = int(time / 60)
        seconds = int(time % 60)
        finalTime = str(minutes) + ":" + str(seconds)
        updateTime(channel, finalTime)
        
    return finalTime
        