import random
import re
from ranges_functions import getFinalKickoffResult
from ranges_functions import getFinalPlayResult
from game_database_functions import updateHomeTimeouts
from game_database_functions import updateAwayTimeouts
from game_database_functions import updateCoinTossWinner
from game_database_functions import updateCoinTossDecision
from game_database_functions import updatePossession
from game_database_functions import updateOffensiveNumber
from game_database_functions import updateDefensiveNumber
from game_database_functions import updateNormalKickoffBallLocation
from game_database_functions import updateSquibKickoffBallLocation
from game_database_functions import updateOnsideKickoffBallLocation
from game_database_functions import updateBallLocation
from game_database_functions import updatePlayType
from game_database_functions import updateWaitingOn
from game_database_functions import updateClockStopped
from game_database_functions import updateDown
from game_database_functions import updateDistance
from game_database_functions import updateHomeScore
from game_database_functions import updateAwayScore
from game_database_functions import getGameInfo
from game_database_functions import getGameInfoDM
from util import messageUser
from util import messageConfirmationUser
from util import getDiscordUser
from util import hasNumbers
from util import calculateDifference
from util import convertTime
from util import convertDown
from util import representsInt
from util import convertYardLine
from util import convertYardLineBack

guildID = 723390838167699508


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 19:35:49 2020

@author: apkick
"""

async def game(client, message):
    gameInfo = getGameInfo(message.channel)
    homeDiscordUser = getDiscordUser(client, gameInfo["home user"])
    awayDiscordUser = getDiscordUser(client, gameInfo["away user"])
    
    # Handle coin toss winner
    if (str(message.author) == str(gameInfo["away user"]) and ('head' in message.content or 'tail' in message.content) and gameInfo["coin toss winner"] == "NONE"):
        await coinToss(homeDiscordUser, awayDiscordUser, message, gameInfo)
    
    # Handle coin toss decision
    elif (str(message.author) == str(gameInfo["coin toss winner"]) and ('receive' in message.content or 'defer' in message.content) and gameInfo["coin toss decision"] == "NONE"):
        await coinTossDecision(client, homeDiscordUser, awayDiscordUser, message, gameInfo)  
        updateWaitingOn(message.channel)

    # Handle kickoff return response
    elif (gameInfo["play type"] == "KICKOFF" and ((str(message.author) == str(gameInfo["home user"]) and gameInfo["possession"] == gameInfo["home name"] and gameInfo["waiting on"] == gameInfo["home user"]) 
                    or (str(message.author) == str(gameInfo["away user"]) and gameInfo["possession"] == gameInfo["away name"] and gameInfo["waiting on"] == gameInfo["away user"]))):
        gameInfo = getGameInfo(message.channel)
        await kickoffReturn(client, message, homeDiscordUser, awayDiscordUser, gameInfo)
        updateWaitingOn(message.channel)
        
    # Handle a normal play type
    elif (gameInfo["play type"] == "NORMAL" and ((str(message.author) == str(gameInfo["home user"]) and gameInfo["possession"] == gameInfo["home name"] and gameInfo["waiting on"] == gameInfo["home user"]) 
                    or (str(message.author) == str(gameInfo["away user"]) and gameInfo["possession"] == gameInfo["away name"] and gameInfo["waiting on"] == gameInfo["away user"]))):
        gameInfo = getGameInfo(message.channel)
        await normalPlay(client, message, homeDiscordUser, awayDiscordUser, gameInfo)
        updateWaitingOn(message.channel)

"""
Handle DMs to the bot

"""
async def gameDM(client, message):
    
    gameInfo = getGameInfoDM(message.author)
    
    # Get the guild so you update the correct channel
    guild = client.get_guild(guildID)
    gameChannel = None
    for channel in guild.channels:
        homeTeam = str(gameInfo["home name"])
        awayTeam = str(gameInfo["away name"])
        name = homeTeam.lower() + " vs " + awayTeam.lower()
        channelName = name.replace(" ", "-")
        if channel.name == channelName:
            gameChannel = channel
            break
        
    gameInfo = getGameInfoDM(message.author)
    homeDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
    awayDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
    
    if(homeDiscordUser != "COULD NOT FIND" and awayDiscordUser != "COULD NOT FIND"):
        # Check if numbers are in the message
        if hasNumbers(message.content) == False:
            if gameInfo["possession"] == gameInfo["home name"]:
                await awayDiscordUser.send("I could not find a number in your message, please try again and submit a number between 1-1500")
            if gameInfo["possession"] == gameInfo["away name"]:
                await homeDiscordUser.send("I could not find a number in your message, please try again and submit a number between 1-1500")
        elif len(list(map(int, re.findall(r'\d+', message.content)))) > 1:
            if gameInfo["possession"] == gameInfo["home name"]:
               await awayDiscordUser.send("I found multiple numbers in your message, please try again and submit a number between 1-1500")
            if gameInfo["possession"] == gameInfo["away name"]:
               await homeDiscordUser.send("I found multiple numbers in your message, please try again and submit a number between 1-1500")
        else:
            numList = list(map(int, re.findall(r'\d+', message.content)))
            number = numList[0]
            if number < 1 or number > 1500:
                 await message.author.send("Your number is not valid, please try again and submit a number between 1-1500")
            else:
                # If valid numbers, update the information in the DB
                updateDefensiveNumber(gameChannel.id, number)
                gameInfo = getGameInfo(gameChannel)
                
                if("timeout" in message.content.lower()):
                    if gameInfo["possession"] == gameInfo["home name"] and gameInfo["home timeouts"] > 0 and gameInfo["clock stopped"] == "NO": 
                        numTimeouts = gameInfo["home timeouts"]
                        updateHomeTimeouts(message.channel, numTimeouts - 1)
                        updateClockStopped(message.channel, "YES")
                        await gameChannel.send("The defense has called a timeout")
                    elif gameInfo["possession"] == gameInfo["away name"] and gameInfo["away timeouts"] > 0 and gameInfo["clock stopped"] == "NO": 
                        numTimeouts = gameInfo["away timeouts"]
                        updateAwayTimeouts(message.channel, numTimeouts - 1)
                        updateClockStopped(message.channel, "YES")
                        await gameChannel.send("The defense has called a timeout")
                    else:
                        await gameChannel.send("The defense has called a timeout but it was not used")
                
                    
                # Send response to the game channel
                if(gameInfo["possession"] == gameInfo["home name"] and gameInfo["play type"] == "KICKOFF"):
                    await gameChannel.send("The opposing team has submitted their number, " + awayDiscordUser.mention + "you're up!\n\n"
                                                + "Please submit either **normal**, **onside**, or **squib** and your number")
                    await messageConfirmationUser(client, awayDiscordUser, number)
                elif(gameInfo["possession"] == gameInfo["away name"] and gameInfo["play type"] == "KICKOFF"):
                    await gameChannel.send("The opposing team has submitted their number, " + homeDiscordUser.mention + "you're up!\n\n"
                                                + "Please submit either **normal**, **onside**, or **squib** and your number")
                    await messageConfirmationUser(client, homeDiscordUser, number)
                elif(gameInfo["possession"] == gameInfo["home name"] and gameInfo["play type"] == "NORMAL"):
                    await gameChannel.send("The opposing team has submitted their number, " + awayDiscordUser.mention + "you're up!\n\n"
                                                + "Please submit either **run**, **pass**, **punt**, **field goal**, **kneel**, or **spike** and your number")
                    await messageConfirmationUser(client, awayDiscordUser, number)
                elif(gameInfo["possession"] == gameInfo["away name"] and gameInfo["play type"] == "NORMAL"):
                    await gameChannel.send("The opposing team has submitted their number, " + homeDiscordUser.mention + "you're up!\n\n"
                                                + "Please submit either **run**, **pass**, **punt**, **field goal**, **kneel**, or **spike** and your number")
                    await messageConfirmationUser(client, homeDiscordUser, number)
                elif(gameInfo["possession"] == gameInfo["home name"] and gameInfo["play type"] == "TOUCHDOWN"):
                    await gameChannel.send("The opposing team has submitted their number, " + awayDiscordUser.mention + "you're up!\n\n"
                                                + "Please submit either **PAT** or **Two Point** and your number")
                    await messageConfirmationUser(client, awayDiscordUser, number)
                elif(gameInfo["possession"] == gameInfo["away name"] and gameInfo["play type"] == "TOUCHDOWN"):
                    await gameChannel.send("The opposing team has submitted their number, " + homeDiscordUser.mention + "you're up!\n\n"
                                                + "Please submit either **PAT** or **Two Point** and your number")
                    await messageConfirmationUser(client, homeDiscordUser, number)
                
                updateWaitingOn(gameChannel)
    
    
"""
Handle normal plays (not PATs or kickoffs)

"""
async def normalPlay(client, message, homeDiscordUser, awayDiscordUser, gameInfo):
    # Handle invalid messages
    if ("pass" not in message.content.lower() and "run" not in message.content.lower() and "punt" not in message.content.lower() and "field goal" not in message.content.lower() 
    and "spike" not in message.content.lower() and "kneel" not in message.content.lower()):
        await message.channel.send("I could not find a play in your message, please try again and submit **run**, **pass**, **punt**, **field goal**, **kneel**, or **spike**")
    elif hasNumbers(message.content) == False:
        await message.channel.send("I could not find a number in your message, please try again and submit a number between 1-1500")
    elif len(list(map(int, re.findall(r'\d+', message.content)))) > 1:
        await message.channel.send("I found multiple numbers in your message, please try again and submit a number between 1-1500")
    # Valid message, get the play and number
    else:
        numList = list(map(int, re.findall(r'\d+', message.content)))
        number = numList[0]
        # Ensure number is valid
        if number < 1 or number > 1500:
             await message.channel.send("Your number is not valid, please try again and submit a number between 1-1500")
        else:
            offensiveNumber = number
            updateOffensiveNumber(message.channel, offensiveNumber)
            defensiveNumber = gameInfo["defensive number"]
            difference = calculateDifference(offensiveNumber, defensiveNumber)
            playType = ""
            clockRunoffType = ""
            timeout = 0
            
            # Get the play type
            if("run" in message.content.lower()):
                playType = "run"
            elif("pass" in message.content.lower()):
                playType = "pass"
            elif("punt" in message.content.lower()):
                playType = "punt"
            elif("field goal" in message.content.lower()):
                playType = "field goal"
            elif("kneel" in message.content.lower()):
                playType = "kneel"
            elif("spike" in message.content.lower()):
                playType = "spike"
            
            # Get the clock runoff
            if("chew" in message.content.lower()):
                clockRunoffType = "chew"
            elif("hurry" in message.content.lower()):
                clockRunoffType = "hurry"
            elif("final play" in message.content.lower()):
                clockRunoffType = "final play"
            else:
                clockRunoffType = "normal"
                
            # See if there's a timeout
            if("timeout" in message.content.lower()):
                if gameInfo["possession"] == gameInfo["home name"] and gameInfo["home timeouts"] > 0 and gameInfo["clock stopped"] == "NO": 
                    timeout = 1
                    numTimeouts = gameInfo["home timeouts"]
                    updateHomeTimeouts(message.channel, numTimeouts - 1)
                    updateClockStopped(message.channel, "YES")
                elif gameInfo["possession"] == gameInfo["away name"] and gameInfo["away timeouts"] > 0 and gameInfo["clock stopped"] == "NO": 
                    timeout = 1
                    numTimeouts = gameInfo["away timeouts"]
                    updateAwayTimeouts(message.channel, numTimeouts - 1)
                    updateClockStopped(message.channel, "YES")
                else:
                    await message.channel.send("The offense has called a timeout but it was not used")
                
             
            # Invalid difference
            if difference == -1:
                await message.channel.send("There was an issue calculating the difference, please contact Dick")
            else:
                offensivePlaybook = ""
                defensivePlaybook = ""
                
                if gameInfo["possession"] == gameInfo["home name"]:
                    offensivePlaybook = gameInfo["home offensive playbook"]
                    defensivePlaybook = gameInfo["away defensive playbook"]
                else:
                    offensivePlaybook = gameInfo["away offensive playbook"]
                    defensivePlaybook = gameInfo["home defensive playbook"]
                    
                # Get the result from the play
                if timeout == 0:
                    clockStopped = gameInfo["clock stopped"]
                else:
                    clockStopped = "YES"
                result = getFinalPlayResult(message, offensivePlaybook, defensivePlaybook, playType, difference, clockRunoffType, clockStopped)
               
                # Update the time and game information
                convertTime(message.channel, gameInfo, result[1])
                
                offenseTeam = ""
                defenseTeam = ""
                
                if(gameInfo["possession"] == gameInfo["home name"]):
                    offenseTeam = gameInfo["home name"]
                    defenseTeam = gameInfo["away name"]
                else:
                    offenseTeam = gameInfo["away name"]
                    defenseTeam = gameInfo["home name"]
                
                if(playType == "run"):
                    await playResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference)
                elif(playType == "pass"):
                    await playResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference)
                elif(playType == "punt"):
                    playType = "punt"
                elif(playType == "field goal"):
                    playType = "field goal"
                elif(playType == "kneel"):
                    playType = "kneel"
                elif(playType == "spike"):
                    playType = "spike"

"""
Update everything based on the play result

"""                
async def playResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference):
    if(str(gameInfo["possession"]) == str(gameInfo["home name"])):
        offenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
    else:
        offenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        
    # If it's not a standard gain
    if(representsInt(result[0]) == False):
        if str(result[0]) == "Pick/Fumble 6":
            await defensiveTouchdown(client, message, gameInfo, result, playType, offenseDiscordUser, offenseTeam, defenseTeam, difference)
        elif "TO + " in str(result[0]) or "TO - " in str(result[0]) or "Turnover" in str(result[0]):
            await turnover(client, message, gameInfo, result, playType, offenseDiscordUser, offenseTeam, defenseTeam, difference)
        elif str(result[0]) == "No Gain" or str(result[0]) == "Incompletion" or str(result[0]) == "Touchdown":
            await play(client, message, gameInfo, result, playType, offenseDiscordUser, defenseDiscordUser, offenseTeam, defenseTeam, difference)
    else:
        await play(client, message, gameInfo, result, playType, offenseDiscordUser, defenseDiscordUser, offenseTeam, defenseTeam, difference)


"""
Go through all the play scenarios

"""
async def play(client, message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference):
    if(representsInt(result[0]) == False):
        if(str(result[0]) == "No Gain"):
            await normalPlayType(client, message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference, 0)
            updateClockStopped(message.channel, "NO")
        elif(str(result[0]) == "Incompletion"):
            await normalPlayType(client, message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference, 0)
            updateClockStopped(message.channel, "YES")
        elif(str(result[0]) == "Touchdown"):
            await normalPlayType(client, message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference, 110)
            updateClockStopped(message.channel, "YES")
    else:
        await normalPlayType(client, message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference, int(result[0]))
        
"""
Handle play specifics

""" 
async def normalPlayType(client, message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference, yards):
    finalResult = offenseTeam + " gains " + str(yards) + " yards."
    yardLine = convertYardLine(gameInfo)
    updatedYardLine = yardLine - yards
    
    # Handle touchdown
    if(updatedYardLine <= 0):
        updateBallLocation(message.channel, offenseTeam + " 3")
        updatePlayType(message.channel, "TOUCHDOWN")
        if offenseTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)
        elif offenseTeam == gameInfo["away name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
        updateClockStopped(message.channel, "YES")
        
        convertTime(message.channel, gameInfo, result[1])
        updateDown(message.channel, 1)
        updateDistance(message.channel, 10)
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        
        await message.channel.send(offenseTeam + " breaks free for a touchdown!\n"
                                   + "**Result:** Touchdown\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseUser.mention + " for a number.\n\n")
        await messageUser(client, defenseUser, gameInfo, gameInfo["time"])
        
    # Handle safety
    elif(updatedYardLine > 100):
        updateBallLocation(message.channel, offenseTeam + " 20")
        updatePlayType(message.channel, "KICKOFF")
        if offenseTeam == gameInfo["home name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 2)
        elif offenseTeam == gameInfo["away name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 2)
        updateClockStopped(message.channel, "YES")
        
        convertTime(message.channel, gameInfo, result[1])
                
        updateDown(message.channel, 1)
        updateDistance(message.channel, 10)
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        
        await message.channel.send(offenseTeam + " gets tackled in their endzone for a safety!\n"
                                   + "**Result:** Safety\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseUser.mention + " for a number.\n\n")
        
        await messageUser(client, defenseUser, gameInfo, gameInfo["time"])
    
    # Handle a standard play
    else:
        down = int(gameInfo["down"])
        distance = int(gameInfo["distance"])
        
        distanceToGo = distance - yards
        if distanceToGo <= 0:
            finalResult = finalResult + " It is good enough for a first down!\n"
            updateDown(message.channel, 1)
            updateDistance(message.channel, 10)
        else:
            # Handle turnover on downs
            if(down + 1 > 4):
                finalResult = finalResult + " It won't be good enough for a first down! Turnover on downs\n"
                updateDown(message.channel, 1)
                updateDistance(message.channel, 10)
                updatePossession(message.channel, defenseTeam)
                updateClockStopped(message.channel, "YES")
                newYardLine = convertYardLineBack(100-updatedYardLine, gameInfo)
                updateBallLocation(message.channel, newYardLine)
            # Update the distance and down
            else:
                finalResult = finalResult + " \n"
                updateDown(message.channel, down + 1)
                updateDistance(message.channel, distanceToGo)
                
        newYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, newYardLine)
        
        gameInfo = getGameInfo(message.channel)
        convertTime(message.channel, gameInfo, result[1])
        
        incompleteFlag = False
        if(representsInt(result[0]) == False):
            if(result[0] == "Incompletion"):
                incompleteFlag = True
        
        down = convertDown(str(gameInfo["down"]))
        
        if(incompleteFlag == True): 
            updateClockStopped(message.channel, "YES")
            await message.channel.send(offenseTeam + " gets a " + str(yards) + " yard gain.\n\n\n"
                                       + "**Result:** " + finalResult
                                       + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                       + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                       + "**Difference:** " + str(difference) + "\n\n\n" 
                                       + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                       + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"
                                       + "The clock is stopped\n\n"
                                       + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                       + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                       + "\n\nWaiting on " + defenseUser.mention + " for a number.\n\n") 
        else:
            updateClockStopped(message.channel, "NO")
            await message.channel.send(offenseTeam + " gets a " + str(yards) + " yard gain.\n\n\n"
                                       + "**Result:** " + finalResult
                                       + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                       + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                       + "**Difference:** " + str(difference) + "\n\n\n" 
                                       + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                       + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"
                                       + "The clock is moving\n\n"
                                       + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                       + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                       + "\n\nWaiting on " + defenseUser.mention + " for a number.\n\n")
            
        
        await messageUser(client, defenseUser, gameInfo, gameInfo["time"])


"""
Go through all the turnover scenarios

"""
async def turnover(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference):
    if(str(result[0]) == "TO + 20 YDs"):
        await turnoverType(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, 20)
    elif(str(result[0]) == "TO + 15 YDs"):
        await turnoverType(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, 15)
    elif(str(result[0]) == "TO + 10 YDs"):
        await turnoverType(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, 10)
    elif(str(result[0]) == "TO + 5 YDs"):
        await turnoverType(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, 5)
    elif(str(result[0]) == "Turnover"):
        await turnoverType(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, 0)
    elif(str(result[0]) == "TO - 5 YDs"):
        await turnoverType(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, -5)
    elif(str(result[0]) == "TO - 10 YDs"):
        await turnoverType(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, -10)
    elif(str(result[0]) == "TO - 15 YDs"):
        await turnoverType(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, -15)
    elif(str(result[0]) == "TO - 20 YDs"):
        await turnoverType(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, -20)
       
"""
Handle turnovers of specific yardages

""" 
async def turnoverType(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, turnoverDistance):
    finalResult = defenseTeam + " gets a turnover of " + str(turnoverDistance) + " yards\n"
    yardLine = convertYardLine(gameInfo)
    updatedYardLine = 100-yardLine
    updatedYardLine = updatedYardLine - turnoverDistance
    
    # Handle touchdown
    if(updatedYardLine <= 0):
        updateBallLocation(message.channel, offenseTeam + " 3")
        updatePlayType(message.channel, "TOUCHDOWN")
        if offenseTeam == gameInfo["home name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
        elif offenseTeam == gameInfo["away name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)
        
    # Handle touchback
    elif(updatedYardLine > 100):
        updateBallLocation(message.channel, defenseTeam + " 20")
        updatePlayType(message.channel, "NORMAL")

    else:
        newYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, newYardLine)
        
    updateClockStopped(message.channel, "YES")
    updatePossession(message.channel, defenseTeam)
    updateDown(message.channel, "1")
    updateDistance(message.channel, "10")
    convertTime(message.channel, gameInfo, result[1])
    
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send("OH NO! " + offenseTeam.upper() + " GIVES UP THE BALL! " + defenseTeam.upper() + "HAS IT!!!\n"
                               + "**Result:** " + finalResult
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"
                               + "The clock is stopped\n\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + offenseUser.mention + " for a number.\n\n")
    
    await messageUser(client, offenseUser, gameInfo, gameInfo["time"])

            
"""
Handle defensive touchdowns

"""       
async def defensiveTouchdown(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference):
    if playType == "pass":
        finalResult = defenseTeam + " takes it back for a Pick Six\n"
    else:
        finalResult = defenseTeam + " takes it back for a Scoop 'N Score\n"
    updateClockStopped(message.channel, "YES")
    updatePossession(message.channel, defenseTeam)
    updateDown(message.channel, "1")
    updateDistance(message.channel, "10")
    updateBallLocation(message.channel, offenseTeam + " 3")
    updatePlayType(message.channel, "TOUCHDOWN")
    if offenseTeam == gameInfo["home name"]:
        updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
    elif offenseTeam == gameInfo["away name"]:
        updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)
    
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send("OH NO! " + offenseTeam.upper() + " GIVES UP THE BALL! " + defenseTeam.upper() + "HAS IT AND THEY'RE WEAVING DOWNFIELD AND THEY TAKE IT TO THE HOUSE! TOUCHDOWN " + defenseTeam.upper() + "!!!\n"
                               + "**Result:** " + finalResult
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"
                               + "The clock is stopped\n\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + offenseUser.mention + " for a number.\n\n")
    
    await messageUser(client, offenseUser, gameInfo, gameInfo["time"]) 
            
"""
Handle kickoff returns

"""
async def kickoffReturn(client, message, homeDiscordUser, awayDiscordUser, gameInfo):
    # Handle invalid messages
    if "normal" not in message.content.lower() and "squib" not in message.content.lower() and "onside" not in message.content.lower():
        await message.channel.send("I could not find a play in your message, please try again and submit **normal**, **squib**, or **onside**")
    elif hasNumbers(message.content) == False:
        await message.channel.send("I could not find a number in your message, please try again and submit a number between 1-1500")
    elif len(list(map(int, re.findall(r'\d+', message.content)))) > 1:
        await message.channel.send("I found multiple numbers in your message, please try again and submit a number between 1-1500")
    # Valid message, get the play and number
    else:
        numList = list(map(int, re.findall(r'\d+', message.content)))
        number = numList[0]
        # Ensure number is valid
        if number < 1 or number > 1500:
             await message.channel.send("Your number is not valid, please try again and submit a number between 1-1500")
        else:
            offensiveNumber = number
            updateOffensiveNumber(message.channel, offensiveNumber)
            defensiveNumber = gameInfo["defensive number"]
            difference = calculateDifference(offensiveNumber, defensiveNumber)
            playType = ""
            if("normal" in message.content.lower()):
                playType = "normal"
            elif("onside" in message.content.lower()):
                playType = "onside"
            elif("squib" in message.content.lower()):
                playType = "squib"

            # Invalid difference
            if difference == -1:
                await message.channel.send("There was an issue calculating the difference, please contact Dick")
            else:
                # Get the result from the play
                result = getFinalKickoffResult(playType, difference)
                # Update the time and game information
                time = convertTime(message.channel, gameInfo, result[1])
                gameInfo = getGameInfo(message.channel)
                if str(result[0]) != "Fumble" and str(result[0]) != "Touchdown":
                    if gameInfo["possession"] == gameInfo["home name"]:
                        await normalKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["away name"]), homeDiscordUser)              
                    if gameInfo["possession"] == gameInfo["away name"]:
                        await normalKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["home name"]), awayDiscordUser)              
                if str(result[0]) == "Fumble":
                    if gameInfo["possession"] == gameInfo["home name"]:
                        await fumbleKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["home name"]), str(gameInfo["away name"]), homeDiscordUser)
                    if gameInfo["possession"] == gameInfo["away name"]:
                        await fumbleKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["away name"]), str(gameInfo["home name"]), awayDiscordUser)
                if str(result[0]) == "Touchdown":
                    if gameInfo["possession"] == gameInfo["home name"]:
                        await fumbleReturnKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["home name"]), str(gameInfo["away name"]), homeDiscordUser)
                    if gameInfo["possession"] == gameInfo["away name"]:
                        await fumbleReturnKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["away name"]), str(gameInfo["home name"]), awayDiscordUser)


"""
Handle a fumble returned for a touchdown on the kickoff

"""
async def fumbleReturnKickoff(client, message, gameInfo, result, playType, difference, time, kickingTeam, returnTeam, returnUser):
    updatePossession(message.channel, kickingTeam)
    if(playType == "normal"): 
        updateNormalKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
    elif(playType == "squib"): 
        updateSquibKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
    elif(playType == "onside"): 
        updateOnsideKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
    
    updateDown(message.channel, "1")
    updateDistance(message.channel, "10")
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send("OH NO! " + returnTeam.upper() + " FUMBLES THE BALL ON THE 20 AND " + kickingTeam.upper() + "TAKES IT TO THE HOUSE!\n"
                               + "**Result:** Fumble Touchdown by the Kicking Team\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + kickingTeam + "\n"
                               + "The clock is stopped\n\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + returnUser.mention + " for a number.\n\n")
    await messageUser(client, returnUser, gameInfo, time) 
    if kickingTeam == gameInfo["home name"]:
        updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)
    elif kickingTeam == gameInfo["away name"]:
        updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
    updatePlayType(message.channel, "TOUCHDOWN")

"""
Handle a fumble on a kickoff

"""
async def fumbleKickoff(client, message, gameInfo, result, playType, difference, time, kickingTeam, returnTeam, returnUser):
    updatePossession(message.channel, kickingTeam)
    if(playType == "normal"): 
        updateNormalKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
    elif(playType == "squib"): 
        updateSquibKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
    elif(playType == "onside"): 
        updateOnsideKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
   
    gameInfo = getGameInfo(message.channel)
    updateDown(message.channel, "1")
    updateDistance(message.channel, "10")
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send("OH NO! " + returnTeam.upper() + " FUMBLES THE BALL ON THE 20 AND " + kickingTeam.upper() + "HAS IT!\n"
                               + "**Result:** Fumble\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + kickingTeam + "\n"
                               + "The clock is stopped\n\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + returnUser.mention + " for a number.\n\n")
    await messageUser(client, returnUser, gameInfo, time)
    updatePlayType(message.channel, "NORMAL")
                
"""
Handle a kickoff that's a standard return by the return team

"""               
async def normalKickoff(client, message, gameInfo, result, playType, difference, time, returnTeam, kickingUser):
    updatePossession(message.channel, returnTeam)
    if(playType == "normal"): 
        updateNormalKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
    elif(playType == "squib"): 
        updateSquibKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
    elif(playType == "onside"): 
        updateOnsideKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
    
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
        
    if str(result[0]) != "Returned TD":
        await message.channel.send("It's a kickoff taken by " + returnTeam + " to the " + gameInfo["yard line"] + "\n"
                                   + "**Result:** Return to the " + gameInfo["yard line"] + "\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + returnTeam + "\n"
                                   + "The clock is stopped\n\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + kickingUser.mention + " for a number.\n\n")
        updatePlayType(message.channel, "NORMAL")
    else: 
        await message.channel.send("It's a kickoff taken by " + returnTeam + " to the 20.... NO WAIT HE BREAKS FREE. HE MAKES THE KICKER MISS. HE WILL GO ALL THE WAY! TOUCHDOWN!!!\n"
                                   + "**Result:** Return Touchdown\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + returnTeam + "\n"
                                   + "The clock is stopped\n\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + kickingUser.mention + " for a number.\n\n")
        updatePlayType(message.channel, "TOUCHDOWN")
        if returnTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)
        elif returnTeam == gameInfo["away name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
    await messageUser(client, kickingUser, gameInfo, time)  
    updateDown(message.channel, "1")
    updateDistance(message.channel, "10")     
                

   
async def coinTossDecision(client, homeDiscordUser, awayDiscordUser, message, gameInfo):
    # Message is not valid
    if (message.content.lower() != "receive" and message.content.lower() != "defer"):
        await message.channel.send("I did not understand your decision, please try again")
    # Handle receiving
    elif "receive" in message.content.lower().strip():
        await message.channel.send(message.author.mention + " chooses to receive. Waiting on a kickoff number from them")
        updateCoinTossDecision(message.channel, "receive")
        if (str(message.author) == str(gameInfo["home user"])):
            updatePossession(message.channel, str(gameInfo["away name"]))
            await messageUser(client, homeDiscordUser, gameInfo, "7:00")
        else: 
            updatePossession(message.channel, str(gameInfo["home name"]))
            await messageUser(client, awayDiscordUser, gameInfo, "7:00")
    # Handle a defer
    elif "defer" in message.content.lower().strip():
        await message.channel.send(message.author.mention + " chooses to defer to the second half. Waiting on a kickoff number from their opponent")
        updateCoinTossDecision(message.channel, "defer")  
        if (str(message.author) == str(gameInfo["home user"])):
            updatePossession(message.channel, str(gameInfo["home name"]))
            await messageUser(client, awayDiscordUser, gameInfo, "7:00")
        else:
            updatePossession(message.channel, str(gameInfo["away name"]))
            await messageUser(client, homeDiscordUser, gameInfo, "7:00")
        
"""
Handle the coin toss

"""
async def coinToss(homeDiscordUser, awayDiscordUser, message, gameInfo):
    result = random.randint(1, 2)
    if("head" in message.content):
        # Heads, away wins
        if result == 1:
            await message.channel.send("It is heads, " + awayDiscordUser.mention  + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
            updateCoinTossWinner(message.channel, gameInfo["away user"])
        else:
            await message.channel.send("It is tails, " + homeDiscordUser.mention  + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
            updateCoinTossWinner(message.channel, gameInfo["home user"])
    else:
        # Heads, home wins
        if result == 1:
            await message.channel.send("It is heads, " + homeDiscordUser.mention + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
            updateCoinTossWinner(message.channel, gameInfo["home user"])
        # Tails, aways wins
        else:
            await message.channel.send("It is tails, " + awayDiscordUser.mention  + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
            updateCoinTossWinner(message.channel, gameInfo["away user"])
    return "Invalid"