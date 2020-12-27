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
from game_database_functions import updatePlayType
from game_database_functions import updateWaitingOn
from game_database_functions import updateClockStopped
from game_database_functions import getGameInfo
from game_database_functions import getGameInfoDM
from util import messageUser
from util import messageConfirmationUser
from util import getDiscordUser
from util import hasNumbers
from util import calculateDifference
from util import convertTime
from util import convertDown

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
                time = convertTime(message.channel, gameInfo, result[1])
            
            
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
    
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send("OH NO! " + returnTeam.upper() + " FUMBLES THE BALL ON THE 20 AND " + kickingTeam.upper() + "TAKES IT TO THE HOUSE!\n\n"
                               + "**Result:** Fumble Touchdown by the Kicking Team\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n\n" 
                               + "**" + str(gameInfo["home name"]) + ":** " + str(gameInfo["home score"]) + " | Timeouts: " + str(gameInfo["home timeouts"]) + "\n"
                               + "**" + str(gameInfo["away name"]) + ":** " + str(gameInfo["away score"]) + " | Timeouts: " + str(gameInfo["away timeouts"]) + "\n"  
                               + "Q" + str(gameInfo["quarter"])  + " | " + str(time) + " | " + down + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | " + kickingTeam + " :football:\n"
                               + "Waiting on " + returnUser.mention + " for a number.")
    await messageUser(client, returnUser, gameInfo, time) 
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
    down = convertDown(str(gameInfo["down"]))
    
    await message.channel.send("OH NO! " + returnTeam.upper() + " FUMBLES THE BALL ON THE 20 AND " + kickingTeam.upper() + "HAS IT!\n\n"
                               + "**Result:** Fumble\n"
                               + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                               + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                               + "**Difference:** " + str(difference) + "\n\n\n" 
                               + "**" + str(gameInfo["home name"]) + ":** " + str(gameInfo["home score"]) + " | Timeouts: " + str(gameInfo["home timeouts"]) + "\n"
                               + "**" + str(gameInfo["away name"]) + ":** " + str(gameInfo["away score"]) + " | Timeouts: " + str(gameInfo["away timeouts"]) + "\n"  
                               + "Q" + str(gameInfo["quarter"])  + " | " + str(time) + " | " + down + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | " + kickingTeam + " :football:\n"
                               + "Waiting on " + returnUser.mention + " for a number.")
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
        await message.channel.send("It's a kickoff taken by " + returnTeam + " to the " + gameInfo["yard line"] + "\n\n"
                                   + "**Result:** Return to the " + gameInfo["yard line"] + "\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n\n" 
                                   + "**" + str(gameInfo["home name"]) + ":** " + str(gameInfo["home score"]) + " | Timeouts: " + str(gameInfo["home timeouts"]) + "\n"
                                   + "**" + str(gameInfo["away name"]) + ":** " + str(gameInfo["away score"]) + " | Timeouts: " + str(gameInfo["away timeouts"]) + "\n"  
                                   + "Q" + str(gameInfo["quarter"])  + " | " + str(time) + " | " + down + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | " + returnTeam + " :football:\n"
                                   + "Waiting on " + kickingUser.mention + " for a number.")
        updatePlayType(message.channel, "NORMAL")
    else: 
        await message.channel.send("It's a kickoff taken by " + returnTeam + " to the 20.... NO WAIT HE BREAKS FREE. HE MAKES THE KICKER MISS. HE WILL GO ALL THE WAY! TOUCHDOWN!!!\n\n"
                                   + "**Result:** Return Touchdown\n"
                                   + "**Offensive Number: **" + str(gameInfo["offensive number"]) + "\n" 
                                   + "**Defensive Number:** " + str(gameInfo["defensive number"]) + "\n" 
                                   + "**Difference:** " + str(difference) + "\n\n\n" 
                                   + "**" + str(gameInfo["home name"]) + ":** " + str(gameInfo["home score"]) + " | Timeouts: " + str(gameInfo["home timeouts"]) + "\n"
                                   + "**" + str(gameInfo["away name"]) + ":** " + str(gameInfo["away score"]) + " | Timeouts: " + str(gameInfo["away timeouts"]) + "\n"  
                                   + "Q" + str(gameInfo["quarter"])  + " | " + str(time) + " | " + down + " & " + str(gameInfo["distance"]) + " | " + str(gameInfo["yard line"]) + " | " + returnTeam + " :football:\n"
                                   + "Waiting on " + kickingUser.mention + " for a number.")
        updatePlayType(message.channel, "TOUCHDOWN")
    await messageUser(client, kickingUser, gameInfo, time)       
                

   
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
