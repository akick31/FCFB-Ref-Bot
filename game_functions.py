import random
import re
from ranges_functions import getFinalKickoffResult
from ranges_functions import getFinalPlayResult
from ranges_functions import getFinalPointAfterResult
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
from game_database_functions import updateQuarter
from game_database_functions import updateTime
from game_database_functions import getGameInfo
from game_database_functions import getGameInfoDM
from user_database_functions import updateRecord
from github_functions import getLogFile
from github_functions import getLogFileURL
from github_functions import updateLogFile
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
from util import getClockRunoff

guildID = 398332149335326720


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions that handle the game logic for a college football game

@author: apkick
"""

async def game(client, message):
    """
    Function that looks at the various play types and determines which play type to run based on the situation

    """
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
     
        # Handle a touchdown play type
    elif (gameInfo["play type"] == "TOUCHDOWN" and ((str(message.author) == str(gameInfo["home user"]) and gameInfo["possession"] == gameInfo["home name"] and gameInfo["waiting on"] == gameInfo["home user"]) 
                    or (str(message.author) == str(gameInfo["away user"]) and gameInfo["possession"] == gameInfo["away name"] and gameInfo["waiting on"] == gameInfo["away user"]))):
        gameInfo = getGameInfo(message.channel)
        await pointAfterPlay(client, message, homeDiscordUser, awayDiscordUser, gameInfo)
        updateWaitingOn(message.channel)
    
    #elif (gameInfo["play type"] == "SAFETY KICKOFF"):
    
    #elif (gameInfo["play type"] == "OVERTIME"):
        
    #elif (gameInfo["play type"] == "GAME DONE"):
       
    gameInfo = getGameInfo(message.channel)
    if gameInfo["play type"] == "GAME DONE":
        winner = ""
        if gameInfo["home score"] > gameInfo["away score"]:
            updateRecord(gameInfo["home name"], "W")
            updateRecord(gameInfo["away name"], "L")
            winner = gameInfo["home name"]
            
        elif gameInfo["home score"] < gameInfo["away score"]:
            updateRecord(gameInfo["home name"], "L")
            updateRecord(gameInfo["away name"], "W")
            winner = gameInfo["away name"]
            
        await message.channel.send(winner + " wins the game " + gameInfo["home score"] + "-" + gameInfo["away score"] + "!\n\n"
                                   + "Please use $end whenever you're ready to clear the channel. You must delete this game before you play another.")
            


async def gameDM(client, message):
    """
    Handle DMs to the bot. Gets the defensive team's number
    
    """
    
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
    

#########################
#     TYPE OF PLAYS     #
#########################
async def normalPlay(client, message, homeDiscordUser, awayDiscordUser, gameInfo):
    """
    Handle normal plays in a college football game and determine the outcome (not PATs or kickoffs)
    
    """

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
                    
                # Handle end of half
                minutes, seconds = gameInfo["time"].split(':')
                time = int(minutes) * 60 + int(seconds)
                clockRunoff = getClockRunoff(message, offensivePlaybook, clockRunoffType)
                endOfHalf = False
                if time < clockRunoff and timeout == 0 and (clockStopped == "NO" or gameInfo["clock stopped"] == "NO"):
                    int(gameInfo["quarter"]) + 1
                    updateQuarter(message.channel, int(gameInfo["quarter"]) + 1)
                    updateTime(message.channel, "7:00")
                    
                    # End of half
                    if int(gameInfo["quarter"]) + 1 == 3 or int(gameInfo["quarter"]) + 1 == 5:
                        endOfHalf = True
                        await message.channel.send("The half has ended. Did not get the play off in time\n")
                        
                if endOfHalf == False:  
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
                        await puntResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference)
                    elif(playType == "field goal"):
                        await fieldGoalResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference)
                    elif(playType == "kneel"):
                        await kneelResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference)
                    elif(playType == "spike"):
                        await spikeResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference)
                              
                # Check if half or game is over
                gameInfo = getGameInfo(message.channel)
                if endOfHalf == True or (int(gameInfo["quarter"]) == 3 and int(gameInfo["time"]) == "7:00") or (int(gameInfo["quarter"]) == 5 and int(gameInfo["time"]) == "7:00"):
                    if int(gameInfo["quarter"]) == 5 and int(gameInfo["home score"]) != int(gameInfo["away score"]):
                        updatePlayType(message.channel, "GAME DONE")
                        
                    elif int(gameInfo["quarter"]) == 5 and int(gameInfo["home score"]) == int(gameInfo["away score"]):
                        updatePlayType(message.channel, "OVERTIME")
                      
                    # Handle halftime
                    elif int(gameInfo["quarter"]) == 3:
                        updatePlayType(message.channel, "KICKOFF")
                        updateClockStopped(message.channel, "YES")
                        
                        if(gameInfo["coin toss winner"] == gameInfo["home user"] and gameInfo["coin toss decision"] == gameInfo["receive"]):
                            updatePossession(message.channel, gameInfo["home name"]) # home team is kicking off
                        elif(gameInfo["coin toss winner"] == gameInfo["home user"] and gameInfo["coin toss decision"] == gameInfo["defer"]):
                            updatePossession(message.channel, gameInfo["away name"]) # home team is receiving
                        elif(gameInfo["coin toss winner"] == gameInfo["away user"] and gameInfo["coin toss decision"] == gameInfo["receive"]):
                            updatePossession(message.channel, gameInfo["away name"]) # away team is kicking off
                        elif(gameInfo["coin toss winner"] == gameInfo["away user"] and gameInfo["coin toss decision"] == gameInfo["defer"]):
                            updatePossession(message.channel, gameInfo["home name"]) # away team is receiving 
                            
                        updateHomeTimeouts(message.channel, 3)
                        updateAwayTimeouts(message.channel, 3)
                        updateDown(message.channel, 1)
                        updateDistance(message.channel, 10)
                        

async def kickoffReturn(client, message, homeDiscordUser, awayDiscordUser, gameInfo):
    """
    Handle how the bot deals with kickoff returns
    
    """

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
                if gameInfo["possession"] == gameInfo["home name"]:
                    offensivePlaybook = gameInfo["home offensive playbook"]
                    defensivePlaybook = gameInfo["away defensive playbook"]
                else:
                    offensivePlaybook = gameInfo["away offensive playbook"]
                    defensivePlaybook = gameInfo["home defensive playbook"]
                                          
                # Get the result from the play
                result = getFinalKickoffResult(playType, difference)
                # Update the time and game information
                time = convertTime(message.channel, gameInfo, result[1])
                gameInfo = getGameInfo(message.channel)
                if str(result[0]) != "Fumble" and str(result[0]) != "Touchdown":
                    if gameInfo["possession"] == gameInfo["home name"]:
                        await normalKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["home name"]), awayDiscordUser)              
                    if gameInfo["possession"] == gameInfo["away name"]:
                        await normalKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["away name"]), homeDiscordUser)              
                if str(result[0]) == "Fumble":
                    if gameInfo["possession"] == gameInfo["home name"]:
                        await fumbleKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["away name"]), str(gameInfo["home name"]), awayDiscordUser)
                    if gameInfo["possession"] == gameInfo["away name"]:
                        await fumbleKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["home name"]), str(gameInfo["away name"]), homeDiscordUser)
                if str(result[0]) == "Touchdown":
                    if gameInfo["possession"] == gameInfo["home name"]:
                        await fumbleReturnKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["away name"]), str(gameInfo["home name"]), awayDiscordUser)
                    if gameInfo["possession"] == gameInfo["away name"]:
                        await fumbleReturnKickoff(client, message, gameInfo, result, playType, difference, time, str(gameInfo["home name"]), str(gameInfo["away name"]), homeDiscordUser)

                        
async def pointAfterPlay(client, message, homeDiscordUser, awayDiscordUser, gameInfo):
    """
    Handle how the bot deals with PATs and two point conversions
    
    """

    # Handle invalid messages
    if ("pat" not in message.content.lower() and "two point" not in message.content.lower()):
        await message.channel.send("I could not find a play in your message, please try again and submit **two point** or **pat**")
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
            
            # Get the play type
            if("pat" in message.content.lower()):
                playType = "pat"
            elif("two point" in message.content.lower()):
                playType = "two point"
             
            # Invalid difference
            if difference == -1:
                await message.channel.send("There was an issue calculating the difference, please contact Dick")
            else:
                # Get the result from the play
                result = getFinalPointAfterResult(playType, difference)
                
                offenseTeam = ""
                defenseTeam = ""
                
                if(gameInfo["possession"] == gameInfo["home name"]):
                    offenseTeam = gameInfo["home name"]
                    defenseTeam = gameInfo["away name"]
                else:
                    offenseTeam = gameInfo["away name"]
                    defenseTeam = gameInfo["home name"]
                
                if(playType == "two point"):
                    await twoPointResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference)
                elif(playType == "pat"):
                    await patResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference)
                
                              
#########################
#      POINT AFTER      #
#########################  
async def twoPointResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference): 
    """
    Update the database and post the message for a two point conversion
    
    """  

    if(str(gameInfo["possession"]) == str(gameInfo["home name"])):
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
    else:
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
      
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    updatePossession(message.channel, offenseTeam)
    updateClockStopped(message.channel, "YES")
    updatePlayType(message.channel, "KICKOFF")
    
    if(str(result[0]) == "Good"):
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        if offenseTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 1)
        elif offenseTeam == gameInfo["away name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 1)
            
        gameInfo = getGameInfo(message.channel)
        
        await message.channel.send(offenseTeam + " goes for two and....... THEY GET IT!!\n\n"
                                   + "**Result:** Two point conversion is successful\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseDiscordUser.mention + " for a number.\n\n")
        await messageUser(client, defenseDiscordUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "TWO POINT", str(result[0]), "0", "0")
                      
    elif(str(result[0]) == "No Good"):
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        
        await message.channel.send(offenseTeam + " goes for two and....... THEY DON'T GET IT!!\n\n"
                                   + "**Result:** Two point conversion is unsuccessful\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseDiscordUser.mention + " for a number.\n\n")
        await messageUser(client, defenseDiscordUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "TWO POINT", str(result[0]), "0", "0")
        
    elif(str(result[0]) == "Defense 2PT"):
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        if offenseTeam == gameInfo["home name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 2)
        elif offenseTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 2)
            
        gameInfo = getGameInfo(message.channel)
        
        await message.channel.send(offenseTeam + " goes for two and....... IT IS INTERCEPTED AT THE GOAL LINE!! THE " + defenseTeam.upper() + " DEFENDER HAS AN OPEN FIELD AND WILL TAKE IT FOR TWO THE OTHER WAY!\n\n"
                                   + "**Result:** Two point conversion is unsuccesful and taken for a defensive two point conversion\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseDiscordUser.mention + " for a number.\n\n")
        await messageUser(client, defenseDiscordUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "TWO POINT", str(result[0]), "0", "0")
        
    updatePossession(message.channel, defenseTeam)
        
       
async def patResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference):   
    """
    Update the database and post the message for a PAT
    
    """  
    
    if(str(gameInfo["possession"]) == str(gameInfo["home name"])):
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
    else:
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
       
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    updatePossession(message.channel, offenseTeam)
    updateClockStopped(message.channel, "YES")
    updatePlayType(message.channel, "KICKOFF")
    
    if(str(result[0]) == "Good"):
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        if offenseTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 2)
        elif offenseTeam == gameInfo["away name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 2)
            
        gameInfo = getGameInfo(message.channel)
        await message.channel.send(offenseTeam + " attempts the PAT and it is right down the pipe.\n\n"
                                   + "**Result:** PAT is successful\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseDiscordUser.mention + " for a number.\n\n")
        await messageUser(client, defenseDiscordUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PAT", str(result[0]), "0", "0")
        
    elif(str(result[0]) == "No Good"):
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        
        await message.channel.send(offenseTeam + " attempts the PAT and it goes wide!!\n\n"
                                   + "**Result:** PAT is unsuccessful\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseDiscordUser.mention + " for a number.\n\n")
        await messageUser(client, defenseDiscordUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PAT", str(result[0]), "0", "0")
        
    elif(str(result[0]) == "Defense 2PT"):
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        if offenseTeam == gameInfo["home name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 2)
        elif offenseTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 2)
        
        gameInfo = getGameInfo(message.channel)
        await message.channel.send(offenseTeam + " attempts the PAT AND IT IS BLOCKED!! IT IS SCOOPED UP BY A " + defenseTeam.upper() + " DEFENDER WHO HAS AN OPEN FIELD AND WILL TAKE IT FOR TWO THE OTHER WAY!\n\n"
                                   + "**Result:** Two point conversion is unsuccesful and taken for a defensive two point conversion\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseDiscordUser.mention + " for a number.\n\n")
        await messageUser(client, defenseDiscordUser, gameInfo, gameInfo["time"])  
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PAT", str(result[0]), "0", "0")

    updatePossession(message.channel, defenseTeam)           
                    
                    
                    
#########################
#         SPIKE         #
#########################     
async def spikeResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference): 
    """
    Update the database and post the message for a spike
    
    """  
    
    if(str(gameInfo["possession"]) == str(gameInfo["home name"])):
        offenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
    else:
        offenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        
    yardLine = convertYardLine(gameInfo)
    convertedYardLine = convertYardLineBack(yardLine, gameInfo)
    updateBallLocation(message.channel, convertedYardLine)
    down = int(gameInfo["down"])
    distance = int(gameInfo["distance"])
    finalResult = ""
        
    # Handle turnover on downs
    if(down + 1 > 4):
        finalResult = "spikes it on 4th and turns it over!!! What a mistake!\n\n"
        updateDown(message.channel, 1)
        updateDistance(message.channel, 10)
        updatePossession(message.channel, defenseTeam)
        updateClockStopped(message.channel, "YES")
        updatePlayType(message.channel, "NORMAL")
        convertTime(message.channel, gameInfo, result[1])
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        distance = int(gameInfo["distance"])
        
        await message.channel.send(offenseTeam + finalResult
                                   + "**Result:** spike on 4th down for a turnover\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + defenseTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + offenseDiscordUser.mention + " for a number.\n\n")
        await messageUser(client, offenseDiscordUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "SPIKE", "TURNOVER", "0", result[1])
        
    # Update the distance and down
    else:
        finalResult = "spikes the ball.\n\n"
        updateDown(message.channel, down + 1)
        updateDistance(message.channel, distance)
        updatePlayType(message.channel, "NORMAL")
        updateClockStopped(message.channel, "YES")
        convertTime(message.channel, gameInfo, result[1])
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        distance = int(gameInfo["distance"])
        
        await message.channel.send(offenseTeam + finalResult
                                   + "**Result:** kspike\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"   
                                   + "The clock is moving\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseDiscordUser.mention + " for a number.\n\n")
        await messageUser(client, defenseDiscordUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "SPIKE", "INCOMPLETE", "0", result[1])
        

#########################
#         KNEEL         #
#########################          
async def kneelResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference):
    """
    Update the database and post the message for a kneel
    
    """  
    if(str(gameInfo["possession"]) == str(gameInfo["home name"])):
        offenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
    else:
        offenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        
    yardLine = convertYardLine(gameInfo)
    convertedYardLine = convertYardLineBack(yardLine + 2, gameInfo)
    updateBallLocation(message.channel, convertedYardLine)
    down = int(gameInfo["down"])
    distance = int(gameInfo["distance"])
    finalResult = ""

     # Handle safety
    if(yardLine + 2 > 100):
        finalResult = " kneels it in the end zone for a safety!!! What a mistake!\n\n"
        updateBallLocation(message.channel, offenseTeam + " 20")
        updatePlayType(message.channel, "SAFETY KICKOFF")
        if offenseTeam == gameInfo["home name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 2)
        elif offenseTeam == gameInfo["away name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 2)
        updateClockStopped(message.channel, "YES")
        convertTime(message.channel, gameInfo, result[1])
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        distance = int(gameInfo["distance"])
        
        await message.channel.send(offenseTeam + finalResult
                                   + "**Result:** kneels in the end zone for a safety\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseDiscordUser.mention + " for a number.\n\n")
        await messageUser(client, defenseDiscordUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "KNEEL", "SAFETY", "-2", result[1])
        
    # Handle turnover on downs
    elif(down + 1 > 4):
        finalResult = "kneels it on 4th down and turns it over!!! What a mistake!\n\n"
        updateDown(message.channel, 1)
        updateDistance(message.channel, 10)
        updatePossession(message.channel, defenseTeam)
        updateClockStopped(message.channel, "YES")
        updatePlayType(message.channel, "NORMAL")
        convertTime(message.channel, gameInfo, result[1])
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        distance = int(gameInfo["distance"])
        
        await message.channel.send(offenseTeam + finalResult
                                   + "**Result:** kneels on 4th down for a turnover\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + defenseTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + offenseDiscordUser.mention + " for a number.\n\n")
        await messageUser(client, offenseDiscordUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "KNEEL", "TURNOVER", "-2", result[1])
        
    # Update the distance and down
    else:
        finalResult = "kneels the ball.\n\n"
        updateDown(message.channel, down + 1)
        updateDistance(message.channel, distance + 2)
        updatePlayType(message.channel, "NORMAL")
        updateClockStopped(message.channel, "NO")
        convertTime(message.channel, gameInfo, result[1])
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        distance = int(gameInfo["distance"])
        
        await message.channel.send(offenseTeam + finalResult
                                   + "**Result:** kneels\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"   
                                   + "The clock is moving\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseDiscordUser.mention + " for a number.\n\n")
        await messageUser(client, defenseDiscordUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "KNEEL", "KNEEL", "-2", result[1])
    

                    
#########################
#      FIELD GOAL       #
#########################
async def fieldGoalResult(client, message, gameInfo, result, playType, kickingTeam, defenseTeam, difference):
    """
    Determine which field goal result updater to go to
    
    """  
    if(str(gameInfo["possession"]) == str(gameInfo["home name"])):
        kickingDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
    else:
        kickingDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        
    if str(result[0]) == "Made":
        await fieldGoalMade(client, message, gameInfo, result, playType, kickingDiscordUser, defenseDiscordUser, kickingTeam, defenseTeam, difference)
    elif str(result[0]) == "Miss":
        await fieldGoalMiss(client, message, gameInfo, result, playType, kickingDiscordUser, defenseDiscordUser, kickingTeam, defenseTeam, difference)
    elif str(result[0]) == "Blocked":
        await fieldGoalBlocked(client, message, gameInfo, result, playType, kickingDiscordUser, defenseDiscordUser, kickingTeam, defenseTeam, difference)
    elif str(result[0]) == "Kick 6":
        await fieldGoalKickSix(client, message, gameInfo, result, playType, kickingDiscordUser, defenseDiscordUser, kickingTeam, defenseTeam, difference)
        
        
async def fieldGoalMade(client, message, gameInfo, result, playType, kickingUser, defenseUser, kickingTeam, defenseTeam, difference):
    """
    Update the database and post the message for a made field goal
    
    """  
    yardLine = convertYardLine(gameInfo)
    fieldGoalDistance = yardLine + 17
    updateBallLocation(message.channel, kickingTeam + " 35")
    updatePlayType(message.channel, "KICKOFF")
    
    if kickingTeam == gameInfo["home name"]:
        updateHomeScore(message.channel, int(gameInfo["home score"]) + 3)
    elif kickingTeam == gameInfo["away name"]:
        updateAwayScore(message.channel, int(gameInfo["away score"]) + 3)
    updateClockStopped(message.channel, "YES")
    
    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send(kickingTeam + " drills a " + fieldGoalDistance + " yard field goal!\n\n"
                               + "**Result:** " + fieldGoalDistance + " yard field goal is **good**\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + kickingTeam + "\n"   
                               + "The clock is stopped\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + defenseUser.mention + " for a number.\n\n")
    await messageUser(client, defenseUser, gameInfo, gameInfo["time"])
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "FIELD GOAL", "GOOD", str(fieldGoalDistance) + " ATTEMPT", result[1])
    
    
async def fieldGoalMiss(client, message, gameInfo, result, playType, kickingUser, defenseUser, kickingTeam, defenseTeam, difference):
    """
    Update the database and post the message for a missed field goal
    
    """  
    
    yardLine = convertYardLine(gameInfo)
    fieldGoalDistance = yardLine + 17
    
    yardLine = convertYardLine(gameInfo) # Line of scrimmage
    if yardLine >= 20:
        updatedYardLine = 100 - yardLine # Flip the yard line to the opponent's side
        convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, convertedYardLine)
    else:
        updatedYardLine = 80 # Place the ball on the 20
        convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, convertedYardLine)
        
    updatePlayType(message.channel, "NORMAL")
    updateClockStopped(message.channel, "YES")
    
    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send(kickingTeam + " misses the " + fieldGoalDistance + " yard field goal.\n\n"
                               + "**Result:** " + fieldGoalDistance + " yard field goal is **no good**\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + defenseTeam + "\n"   
                               + "The clock is stopped\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + kickingUser.mention + " for a number.\n\n")
    await messageUser(client, kickingUser, gameInfo, gameInfo["time"])
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "FIELD GOAL", "MISS", str(fieldGoalDistance) + " ATTEMPT", result[1])
    
    
async def fieldGoalBlocked(client, message, gameInfo, result, playType, kickingUser, defenseUser, kickingTeam, defenseTeam, difference):
    """
    Update the database and post the message for a blocked field goal
    
    """  
    
    yardLine = convertYardLine(gameInfo)
    fieldGoalDistance = yardLine + 17
    
    yardLine = convertYardLine(gameInfo) # Line of scrimmage
    if yardLine >= 20:
        updatedYardLine = 100 - yardLine # Flip the yard line to the opponent's side
        convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, convertedYardLine)
    else:
        updatedYardLine = 80 # Place the ball on the 20
        convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, convertedYardLine)
        
    updatePlayType(message.channel, "NORMAL")
    updateClockStopped(message.channel, "YES")
    
    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send(defenseTeam + " blocks the " + fieldGoalDistance + " yard field goal!!!!\n\n"
                               + "**Result:** " + fieldGoalDistance + " yard field goal is **blocked**\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + defenseTeam + "\n"   
                               + "The clock is stopped\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + kickingUser.mention + " for a number.\n\n")
    await messageUser(client, kickingUser, gameInfo, gameInfo["time"])
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "FIELD GOAL", "BLOCKED", str(fieldGoalDistance) + " ATTEMPT", result[1])
    

async def fieldGoalKickSix(client, message, gameInfo, result, playType, kickingUser, defenseUser, kickingTeam, defenseTeam, difference):
    """
    Update the database and post the message for a blocked field goal
    
    """  
    
    yardLine = convertYardLine(gameInfo)
    fieldGoalDistance = yardLine + 17
    
    updateBallLocation(message.channel, kickingTeam + " 3")
    updatePlayType(message.channel, "TOUCHDOWN")
    if defenseTeam == gameInfo["home name"]:
        updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)
    elif defenseTeam == gameInfo["away name"]:
        updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
        
    updatePlayType(message.channel, "TOUCHDOWN")
    updateClockStopped(message.channel, "YES")
    
    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    
    await message.channel.send(defenseTeam + " blocks the " + fieldGoalDistance + " yard field goal!!!! AND THEY HAVE THE BALL AND HAVE A BLOCKER! THEY'LL TAKE IT IN FOR SIX! TOUCHDOWN " + defenseTeam.upper() + "!!!\n\n"
                               + "**Result:** " + fieldGoalDistance + " yard field goal is blocked and returned for a **kick six**\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + defenseTeam + "\n"   
                               + "The clock is stopped\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + kickingUser.mention + " for a number.\n\n")
    await messageUser(client, kickingUser, gameInfo, gameInfo["time"])
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "FIELD GOAL", "KICK SIX", str(fieldGoalDistance) + " ATTEMPT", result[1])

                    
#########################
#        PUNTS          #
#########################
async def puntResult(client, message, gameInfo, result, playType, puntTeam, returnTeam, difference):
    """
    Determine which punt result updater to go to
    
    """  
    if(str(gameInfo["possession"]) == str(gameInfo["home name"])):
        puntDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        returnDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
    else:
        puntDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
        returnDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        
    # If it's not a standard return
    if(representsInt(result[0]) == False):
        if str(result[0]) == "Punt Six":
            await puntReturnTouchdown(client, message, gameInfo, result, playType, puntDiscordUser, returnDiscordUser, puntTeam, returnTeam, difference)
        elif str(result[0]) == "Blocked":
            await puntBlock(client, message, gameInfo, result, playType, puntDiscordUser, returnDiscordUser, puntTeam, returnTeam, difference)
        elif str(result[0]) == "Touchback":
            await puntTouchback(client, message, gameInfo, result, playType, puntDiscordUser, returnDiscordUser, puntTeam, returnTeam, difference)
        elif str(result[0]) == "Fumble":
            await puntFumble(client, message, gameInfo, result, playType, puntDiscordUser, returnDiscordUser, puntTeam, returnTeam, difference)
        elif str(result[0]) == "Touchdown":
            await puntTeamTouchdown(client, message, gameInfo, result, playType, puntDiscordUser, returnDiscordUser, puntTeam, returnTeam, difference)
    else:
        await punt(client, message, gameInfo, result, playType, puntDiscordUser, returnDiscordUser, puntTeam, returnTeam, difference)

"""
Handle punt return specifics

""" 
async def punt(client, message, gameInfo, result, playType, puntUser, returnUser, puntTeam, returnTeam, difference):
    """
    Update the database and post the message for a standard punt return
    
    """  
    
    puntYardage = int(result[0])
    yardLine = convertYardLine(gameInfo) # Line of scrimmage
    updatedYardLine = yardLine - puntYardage
    updatedYardLine = 100 - updatedYardLine # Flip the yard line to the opponent's side
    convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
    
    updateBallLocation(message.channel, convertedYardLine)
    updatePlayType(message.channel, "NORMAL")
    updateClockStopped(message.channel, "YES")
    
    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    if(puntYardage < 35): 
        await message.channel.send(returnTeam + " calls for a fair catch " + str(puntYardage) + " yards downfield\n\n"
                                   + "**Result:** " + str(puntYardage) + " net yard punt\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + returnTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + puntUser.mention + " for a number.\n\n")
    else:
        await message.channel.send(returnTeam + " attempts to return it and gets taken down for a net " + str(puntYardage) + " yard punt\n\n"
                                   + "**Result:** " + str(puntYardage) + " net yard punt\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + returnTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + puntUser.mention + " for a number.\n\n")
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "PUNT", str(puntYardage) + " NET YARD PUNT", result[1])
    await messageUser(client, puntUser, gameInfo, gameInfo["time"])   
    
    
async def puntReturnTouchdown(client, message, gameInfo, result, playType, puntUser, returnUser, puntTeam, returnTeam, difference):
    """
    Update the database and post the message for a punt return touchdown
    
    """  
    
    updateBallLocation(message.channel, puntTeam + " 3")
    updatePlayType(message.channel, "TOUCHDOWN")
    if returnTeam == gameInfo["home name"]:
        updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)
    elif returnTeam == gameInfo["away name"]:
        updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
    updateClockStopped(message.channel, "YES")
    
    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send(returnTeam + " takes the punt and tries to return it.... they break a tackle AND THEY HAVE ROOM! HE COULD. GO. ALL. THE. WAY!! TOUCHDOWN!!!!\n\n"
                               + "**Result:** Punt Return Touchdown\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + returnTeam + "\n"   
                               + "The clock is stopped\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + puntUser.mention + " for a number.\n\n")
    await messageUser(client, puntUser, gameInfo, gameInfo["time"])
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "PUNT RETURN TD", "PUNT RETURN TD", result[1])
    

async def puntBlock(client, message, gameInfo, result, playType, puntUser, returnUser, puntTeam, returnTeam, difference):
    """
    Update the database and post the message for a blocked punt return
    
    """  
    
    yardLine = convertYardLine(gameInfo)
    updatedYardLine = 100 - yardLine
    convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
    
    updateBallLocation(message.channel, convertedYardLine)
    updatePlayType(message.channel, "NORMAL")
    updateClockStopped(message.channel, "YES")
    
    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send(returnTeam + " BLOCKS THE PUNT!\n\n"
                               + "**Result:** Blocked Punt\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + returnTeam + "\n"   
                               + "The clock is stopped\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + puntUser.mention + " for a number.\n\n")
    await messageUser(client, puntUser, gameInfo, gameInfo["time"])
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "PUNT BLOCK", "PUNT BLOCK", result[1])
    
    
async def puntTouchback(client, message, gameInfo, result, playType, puntUser, returnUser, puntTeam, returnTeam, difference):
    """
    Update the database and post the message for a touchback punt
    
    """  
    
    updatedYardLine = 80
    convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
    
    updateBallLocation(message.channel, convertedYardLine)
    updatePlayType(message.channel, "NORMAL")
    updateClockStopped(message.channel, "YES")
    
    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send(puntTeam + "kicks it into the endzone for a touchback.\n\n"
                               + "**Result:** Touchback\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + returnTeam + "\n"   
                               + "The clock is stopped\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + puntUser.mention + " for a number.\n\n")
    await messageUser(client, puntUser, gameInfo, gameInfo["time"])
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "PUNT", "TOUCHBACK", result[1])
    
    
async def puntFumble(client, message, gameInfo, result, playType, puntUser, returnUser, puntTeam, returnTeam, difference):
    """
    Update the database and post the message for a muffed punt
    
    """  
    
    yardLine = convertYardLine(gameInfo)
    updatedYardLine = int(yardLine) - 40
    convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
    
    # Handle touchdown
    if(updatedYardLine <= 0):
        updateBallLocation(message.channel, returnTeam + " 3")
        updatePlayType(message.channel, "TOUCHDOWN")
        if puntTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)
        elif puntTeam == gameInfo["away name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
        updateClockStopped(message.channel, "YES")
        
        convertTime(message.channel, gameInfo, result[1])
        updateDown(message.channel, 1)
        updateDistance(message.channel, 10)
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        
        await message.channel.send(returnTeam + " muffs the punt in the end zone!!! AND " + puntTeam.upper() + " RECOVERS!!! TOUCHDOWN " + + puntTeam.upper() + "!!!!\n\n"
                                   + "**Result:** Muffed punt in the end zone for a touchdown\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + puntTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + returnUser.mention + " for a number.\n\n")
        await messageUser(client, returnUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "MUFF PUNT TD", "MUFF PUNT TD", result[1])
    # Handle normal muff
    else:
        updateBallLocation(message.channel, convertedYardLine)
        updatePlayType(message.channel, "NORMAL")
        updateClockStopped(message.channel, "YES")
        
        convertTime(message.channel, gameInfo, result[1])
        updateDown(message.channel, 1)
        updateDistance(message.channel, 10)
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        
        await message.channel.send(returnTeam + " muffs the punt 40 yards downfield!!! AND " + puntTeam.upper() + " RECOVERS!!!\n\n"
                                   + "**Result:** Muffed punt\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + puntTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + returnUser.mention + " for a number.\n\n")
        await messageUser(client, returnUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "MUFFED PUNT", "MUFFED PUNT", result[1])
        

async def puntTeamTouchdown(client, message, gameInfo, result, playType, puntUser, returnUser, puntTeam, returnTeam, difference):
    """
    Update the database and post the message for a muffed punt and touchdown
    
    """  
    
    updateBallLocation(message.channel, returnTeam + " 3")
    updatePlayType(message.channel, "TOUCHDOWN")
    if puntTeam == gameInfo["home name"]:
        updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)
    elif puntTeam == gameInfo["away name"]:
        updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
    updateClockStopped(message.channel, "YES")
    
    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send(returnTeam + " muffs the punt!!! AND " + puntTeam.upper() + " RECOVERS WITH AN OPEN FIELD AHEAD OF THEM. HE WILL GO ALL THE WAY!!! TOUCHDOWN " + + puntTeam.upper() + "!!!!\n\n"
                               + "**Result:** Muffed Punt Touchdown\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + puntTeam + "\n"   
                               + "The clock is stopped\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + returnUser.mention + " for a number.\n\n")
    await messageUser(client, returnUser, gameInfo, gameInfo["time"])
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "MUFF PUNT TD", "MUFF PUNT TD", result[1])




#########################
#      NORMAL PLAY      #
#########################              
async def playResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference):
    """
    Determine which play result updater to go to
    
    """  
    
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


async def play(client, message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference):
    """
    Sort through the different types of standard plays
    
    """  
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
        
        
async def normalPlayType(client, message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference, yards):
    """
    Update the database and post the message for a normal play (run or pass)
    
    """  
    
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
        
        await message.channel.send(offenseTeam + " breaks free for a touchdown!\n\n"
                                   + "**Result:** Touchdown\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"   
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseUser.mention + " for a number.\n\n")
        await messageUser(client, defenseUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "TOUCHDOWN", str(yards), result[1])
        
    # Handle safety
    elif(updatedYardLine > 100):
        updateBallLocation(message.channel, offenseTeam + " 20")
        updatePlayType(message.channel, "SAFETY KICKOFF")
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
        
        await message.channel.send(offenseTeam + " gets tackled in their endzone for a safety!\n\n"
                                   + "**Result:** Safety\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"
                                   + "The clock is stopped\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + defenseUser.mention + " for a number.\n\n")
        
        await messageUser(client, defenseUser, gameInfo, gameInfo["time"])
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "SAFETY", str(yards), result[1])
    
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
            await message.channel.send("The pass is incomplete\n\n"
                                       + "**Result:** Incomplete pass"
                                       + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                       + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                       + "**Difference:** " + str(difference) + "\n\n" 
                                       + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                       + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"
                                       + "The clock is stopped\n\n"
                                       + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                       + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                       + "\n\nWaiting on " + defenseUser.mention + " for a number.\n\n") 
            await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "INCOMPLETE", str(yards), result[1])
        else:
            if(yards >= 0): 
                updateClockStopped(message.channel, "NO")
                await message.channel.send(offenseTeam + " gets a " + str(yards) + " yard gain.\n\n"
                                           + "**Result:** " + finalResult
                                           + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                           + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                           + "**Difference:** " + str(difference) + "\n\n" 
                                           + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                           + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"
                                           + "The clock is moving\n\n"
                                           + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                           + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                           + "\n\nWaiting on " + defenseUser.mention + " for a number.\n\n")
                await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "GAIN", str(yards), result[1])
            else:
                updateClockStopped(message.channel, "NO")
                await message.channel.send(offenseTeam + " has a " + str(yards) + " yard loss!\n\n"
                                           + "**Result:** " + finalResult
                                           + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                           + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                           + "**Difference:** " + str(difference) + "\n\n" 
                                           + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                           + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + offenseTeam + "\n"
                                           + "The clock is moving\n\n"
                                           + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                           + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                           + "\n\nWaiting on " + defenseUser.mention + " for a number.\n\n")
                await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "LOSS", str(yards), result[1])
            
        await messageUser(client, defenseUser, gameInfo, gameInfo["time"])


async def turnover(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference):
    """
    Go through all the turnover scenarios
    
    """

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
       
        
async def turnoverType(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, turnoverDistance):
    """
    Update the database and post the message for a turnover based on the turnover yardage given
    
    """ 
    
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
    
    await message.channel.send("OH NO! " + offenseTeam.upper() + " GIVES UP THE BALL! " + defenseTeam.upper() + " HAS IT!!!\n\n"
                               + "**Result:** " + finalResult
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + defenseTeam + "\n"
                               + "The clock is stopped\n\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + offenseUser.mention + " for a number.\n\n")
    
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "TURNOVER", "TURNOVER", result[1])
    await messageUser(client, offenseUser, gameInfo, gameInfo["time"])


async def defensiveTouchdown(client, message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference):
    """
    Update the database and post the message for a defensive touchdown
    
    """ 
    
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
    
    await message.channel.send("OH NO! " + offenseTeam.upper() + " GIVES UP THE BALL! " + defenseTeam.upper() + "HAS IT AND THEY'RE WEAVING DOWNFIELD AND THEY TAKE IT TO THE HOUSE! TOUCHDOWN " + defenseTeam.upper() + "!!!\n\n"
                               + "**Result:** " + finalResult
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + defenseTeam + "\n"
                               + "The clock is stopped\n\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + offenseUser.mention + " for a number.\n\n")
    
    await messageUser(client, offenseUser, gameInfo, gameInfo["time"]) 
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "TURNOVER TD", "TURNOVER TD", result[1])
    
    
    

#########################
#        KICKOFFS       #
#########################
async def fumbleReturnKickoff(client, message, gameInfo, result, playType, difference, time, kickingTeam, returnTeam, returnUser):
    """
    Update the database and post the message for a fumble on the kickoff returned for a touchdown
    
    """ 
    
    updatePossession(message.channel, kickingTeam)
    if(playType == "normal"): 
        updateNormalKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
    elif(playType == "squib"): 
        updateSquibKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
    elif(playType == "onside"): 
        updateOnsideKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
    
    if kickingTeam == gameInfo["home name"]:
        updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)
    elif kickingTeam == gameInfo["away name"]:
        updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
        
    updateDown(message.channel, "1")
    updateDistance(message.channel, "10")
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send("OH NO! " + returnTeam.upper() + " FUMBLES THE BALL ON THE 20 AND " + kickingTeam.upper() + " TAKES IT TO THE HOUSE!\n\n"
                               + "**Result:** Fumble Touchdown by the Kicking Team\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + kickingTeam + "\n"
                               + "The clock is stopped\n\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + returnUser.mention + " for a number.\n\n")
    await messageUser(client, returnUser, gameInfo, time) 
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "MUFFED KICKOFF TD", "MUFFED KICKOFF TD", result[1])
    updatePlayType(message.channel, "TOUCHDOWN")


async def fumbleKickoff(client, message, gameInfo, result, playType, difference, time, kickingTeam, returnTeam, returnUser):
    """
    Update the database and post the message for a fumble on the kickoff
    
    """ 
    
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
    
    await message.channel.send("OH NO! " + returnTeam.upper() + " FUMBLES THE BALL ON THE 20 AND " + kickingTeam.upper() + " HAS IT!\n\n"
                               + "**Result:** Fumble\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n" 
                               + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                               + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + kickingTeam + "\n"
                               + "The clock is stopped\n\n"
                               + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                               + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                               + "\n\nWaiting on " + returnUser.mention + " for a number.\n\n")
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "MUFFED KICKOFF", "MUFFED KICKOFF", result[1])
    await messageUser(client, returnUser, gameInfo, time)
    updatePlayType(message.channel, "NORMAL")
                
              
async def normalKickoff(client, message, gameInfo, result, playType, difference, time, returnTeam, kickingUser):
    """
    Update the database and post the message for a standard kickoff
    
    """ 
    
    updatePossession(message.channel, returnTeam)
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
        
    if str(result[0]) != "Returned TD":
        await message.channel.send("It's a kickoff taken by " + returnTeam + " to the " + gameInfo["yard line"] + "\n\n"
                                   + "**Result:** Return to the " + gameInfo["yard line"] + "\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + returnTeam + "\n"
                                   + "The clock is stopped\n\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + kickingUser.mention + " for a number.\n\n")
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "KICKOFF RETURN", "RETURN TO THE " + str(gameInfo["yard line"]).upper(), result[1])
        updatePlayType(message.channel, "NORMAL")
    else: 
        if returnTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)
        elif returnTeam == gameInfo["away name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
        gameInfo = getGameInfo(message.channel)
        await message.channel.send("It's a kickoff taken by " + returnTeam + " to the 20.... NO WAIT HE BREAKS FREE. HE MAKES THE KICKER MISS. HE WILL GO ALL THE WAY! TOUCHDOWN!!!\n\n"
                                   + "**Result:** Return Touchdown\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n" 
                                   + "**Q" + str(gameInfo["quarter"])  + " | " + str(gameInfo["time"]) + " | " + str(gameInfo["home name"]) + " " + str(gameInfo["home score"]) + " " + str(gameInfo["away name"]) + " " + str(gameInfo["away score"]) + "**\n"
                                   + str(down) + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | :football: " + returnTeam + "\n"
                                   + "The clock is stopped\n\n"
                                   + str(gameInfo["home name"]) + " has " + str(gameInfo["home timeouts"]) + " timeouts\n"
                                   + str(gameInfo["away name"]) + " has " + str(gameInfo["away timeouts"]) + " timeouts\n"
                                   + "\n\nWaiting on " + kickingUser.mention + " for a number.\n\n")
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "KICKOFF RETURN TD", "KICKOFF RETURN TD", result[1])
        updatePlayType(message.channel, "TOUCHDOWN")
    await messageUser(client, kickingUser, gameInfo, time)      
                


#########################
#       COIN TOSS       #
#########################
   
async def coinTossDecision(client, homeDiscordUser, awayDiscordUser, message, gameInfo):
    """
    Update the database and post the message for the coin toss winner's decision
    
    """ 
    
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
        

async def coinToss(homeDiscordUser, awayDiscordUser, message, gameInfo):
    """
    Update the database and post the message for the coin toss result
    
    """ 
    
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