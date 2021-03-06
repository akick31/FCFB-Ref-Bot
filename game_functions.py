import random
import re
import json
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
from game_database_functions import updateWaitingOnUser
from game_database_functions import updateWaitingOnKickoffDM
from game_database_functions import updateClockStopped
from game_database_functions import updateDown
from game_database_functions import updateDistance
from game_database_functions import updateHomeScore
from game_database_functions import updateAwayScore
from game_database_functions import updateQuarter
from game_database_functions import updateTime
from game_database_functions import getGameInfo
from game_database_functions import getGameInfoDM
from game_database_functions import updateNumberSubmitted
from game_database_functions import updateHalftime
from user_database_functions import updateRecord
from github_functions import getLogFile
from github_functions import updateLogFile
from stats_database_functions import updatePuntResult
from stats_database_functions import updateSquibKickoffResult
from stats_database_functions import updateOnsideKickoffResult
from stats_database_functions import updateNormalKickoffResult
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
from util import getScoreboardString
from util import handleHalftime

with open('config.json') as f:
    data = json.load(f)
jsonData = json.dumps(data)
guildID = json.loads(jsonData)["guildID"]

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
    if str(message.author) == str(gameInfo["away user"]) and ('head' in message.content.lower().strip() or 'tail' in message.content.lower().strip()) and gameInfo["coin toss winner"] == "NONE":
        await coinToss(homeDiscordUser, awayDiscordUser, message, gameInfo)

    # Handle coin toss decision
    elif str(message.author) == str(gameInfo["coin toss winner"]) and ('receive' in message.content.lower().strip() or 'defer' in message.content.lower().strip()) and gameInfo["coin toss decision"] == "NONE":
        await coinTossDecision(homeDiscordUser, awayDiscordUser, message, gameInfo)
        updateNumberSubmitted(message.channel, "NO")

    # Handle kickoff return response
    elif (gameInfo["play type"] == "KICKOFF" and ((str(message.author) == str(gameInfo["home user"]) and gameInfo["possession"] == gameInfo["home name"] and gameInfo["waiting on"] == gameInfo["home user"])
                    or (str(message.author) == str(gameInfo["away user"]) and gameInfo["possession"] == gameInfo["away name"] and gameInfo["waiting on"] == gameInfo["away user"]))
                    and ("normal" in message.content.lower() or "squib" in message.content.lower() or "onside" in message.content.lower())):
        gameInfo = getGameInfo(message.channel)
        result = await kickoffReturn(message, homeDiscordUser, awayDiscordUser, gameInfo)
        if result != "INVALID":
            updateNumberSubmitted(message.channel, "NO")
        else:
            await message.channel.send("There was an issue with determining the kickoff result")

    # Handle a normal play type
    elif (gameInfo["play type"] == "NORMAL" and ((str(message.author) == str(gameInfo["home user"]) and gameInfo["possession"] == gameInfo["home name"] and gameInfo["waiting on"] == gameInfo["home user"])
                    or (str(message.author) == str(gameInfo["away user"]) and gameInfo["possession"] == gameInfo["away name"] and gameInfo["waiting on"] == gameInfo["away user"]))
                    and ("pass" in message.content.lower() or "run" in message.content.lower() or "punt" in message.content.lower() or "field goal" in message.content.lower()
                         or "spike" in message.content.lower() or "kneel" in message.content.lower())):

        gameInfo = getGameInfo(message.channel)
        result = await normalPlay(client, message, gameInfo)
        if result != "INVALID":
            updateNumberSubmitted(message.channel, "NO")
        else:
            await message.channel.send("There was an issue with determining the play result")

        # Handle a touchdown play type
    elif (gameInfo["play type"] == "TOUCHDOWN" and ((str(message.author) == str(gameInfo["home user"]) and gameInfo["possession"] == gameInfo["home name"] and gameInfo["waiting on"] == gameInfo["home user"])
                    or (str(message.author) == str(gameInfo["away user"]) and gameInfo["possession"] == gameInfo["away name"] and gameInfo["waiting on"] == gameInfo["away user"]))
                    and ("pat" in message.content.lower() or "two point" in message.content.lower())):
        gameInfo = getGameInfo(message.channel)
        result = await pointAfterPlay(client, message, gameInfo)
        if result != "INVALID":
            updateNumberSubmitted(message.channel, "NO")
        else:
            await message.channel.send("There was an issue with determining the PAT result")


    elif (gameInfo["play type"] == "SAFETY KICKOFF" and ((str(message.author) == str(gameInfo["home user"]) and gameInfo["possession"] == gameInfo["home name"] and gameInfo["waiting on"] == gameInfo["home user"])
                    or (str(message.author) == str(gameInfo["away user"]) and gameInfo["possession"] == gameInfo["away name"] and gameInfo["waiting on"] == gameInfo["away user"]))
                    and "punt" in message.content.lower()):
        gameInfo = getGameInfo(message.channel)
        result = await safetyKickoff(client, message, gameInfo)
        if result != "INVALID":
            updateNumberSubmitted(message.channel, "NO")
        else:
            await message.channel.send("There was an issue with determining the safety kickoff result")

    elif gameInfo["play type"] == "OVERTIME":
        updatePlayType(message.channel, "GAME DONE")

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

        elif gameInfo["home score"] == gameInfo["away score"]:
            updateRecord(gameInfo["home name"], "T")
            updateRecord(gameInfo["away name"], "T")
            winner = "TIE"

        if winner != "TIE":
            await message.channel.send(winner + " wins the game " + gameInfo["home score"] + "-" + gameInfo["away score"] + "!\n\n"
                                   + "Please use &end whenever you're ready to clear the channel. You must delete this game before you play another.")
        else:
            await message.channel.send("The game finishes tied at " + gameInfo["home score"] + "-" + gameInfo["away score"] + ". Overtime is not currently implemented.\n\n"
                                   + "Please use &end whenever you're ready to clear the channel. You must delete this game before you play another.")

async def gameDM(client, message):
    """
    Handle DMs to the bot. Gets the defensive team's number
    
    """

    gameInfo = getGameInfoDM(message.author)
    homeDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
    awayDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))

    if message.author.name == "FCFB Ref Bot":
        return
    elif gameInfo["waiting on"] is None:
        await message.author.send("There doesn't seem to be anyone I am waiting on in your game. Contact Dick")
        return
    elif gameInfo["waiting on"].split("#")[0] == str(message.author.name) and gameInfo["number submitted"] == "YES":
        await message.author.send("I am not waiting on a message from you")
        return
    elif gameInfo["waiting on"].split("#")[0] != str(message.author.name):
        await message.author.send("I am not waiting on a message from you")
        return
    else:
        # Get the guild so you update the correct channel
        guild = client.get_guild(guildID)
        gameChannel = None
        homeTeam = str(gameInfo["home name"])
        awayTeam = str(gameInfo["away name"])
        name = homeTeam.lower() + " vs " + awayTeam.lower()
        channelName = name.replace(" ", "-")
        if "&" in channelName:
            channelName = channelName.replace("&", "")
        for channel in guild.channels:
            if channel.name == channelName:
                gameChannel = channel
                break

        gameInfo = getGameInfoDM(message.author)

        if homeDiscordUser != "COULD NOT FIND" and awayDiscordUser != "COULD NOT FIND":
            # Check if numbers are in the message
            if not hasNumbers(message.content):
                if gameInfo["possession"] == gameInfo["home name"]:
                    await awayDiscordUser.send("I could not find a number in your message, please try again and submit a number between 1-1500")
                if gameInfo["possession"] == gameInfo["away name"]:
                    await homeDiscordUser.send("I could not find a number in your message, please try again and submit a number between 1-1500")
            elif len(list(map(int, re.findall(r'\d+', message.content)))) > 1:
                if gameInfo["possession"] == gameInfo["home name"]:
                    await awayDiscordUser.send("I found multiple numbers in your message, please try again and submit a number between 1-1500")
                if gameInfo["possession"] == gameInfo["away name"]:
                    await homeDiscordUser.send("I found multiple numbers in your message, please try again and submit a number between 1-1500")
            elif gameChannel is None:
                if gameInfo["possession"] == gameInfo["home name"]:
                    await awayDiscordUser.send("I could not find the game channel, please contact Dick")
                if gameInfo["possession"] == gameInfo["away name"]:
                    await homeDiscordUser.send("I could not find the game channel, please contact Dick")
            else:
                numList = list(map(int, re.findall(r'\d+', message.content)))
                number = numList[0]
                if number < 1 or number > 1500:
                    await message.author.send("Your number is not valid, please try again and submit a number between 1-1500")
                else:
                    # If valid numbers, update the information in the DB
                    updateDefensiveNumber(gameChannel.id, number)
                    gameInfo = getGameInfo(gameChannel)

                    if "timeout" in message.content.lower():
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
                    if gameInfo["possession"] == gameInfo["home name"] and gameInfo["play type"] == "KICKOFF":
                        await gameChannel.send("The opposing team has submitted their number, " + homeDiscordUser.mention + " you're up!\n\n"
                                                + "Please submit either **normal**, **onside**, or **squib** and "
                                                + "your number")
                        updatePossession(gameChannel, gameInfo["home name"])
                        await messageConfirmationUser(awayDiscordUser, number)
                    elif gameInfo["possession"] == gameInfo["away name"] and gameInfo["play type"] == "KICKOFF":
                        await gameChannel.send("The opposing team has submitted their number, " + awayDiscordUser.mention + " you're up!\n\n"
                                                    + "Please submit either **normal**, **onside**, or **squib** and your number")
                        updatePossession(gameChannel, gameInfo["away name"])
                        await messageConfirmationUser(homeDiscordUser, number)
                    elif gameInfo["possession"] == gameInfo["home name"] and gameInfo["play type"] == "NORMAL":
                        await gameChannel.send("The opposing team has submitted their number, " + homeDiscordUser.mention + " you're up!\n\n"
                                                    + "Please submit either **run**, **pass**, **punt**, **field goal**, **kneel**, or **spike** and your number")
                        await messageConfirmationUser(awayDiscordUser, number)
                    elif gameInfo["possession"] == gameInfo["away name"] and gameInfo["play type"] == "NORMAL":
                        await gameChannel.send("The opposing team has submitted their number, " + awayDiscordUser.mention + " you're up!\n\n"
                                                    + "Please submit either **run**, **pass**, **punt**, **field goal**, **kneel**, or **spike** and your number")
                        await messageConfirmationUser(homeDiscordUser, number)
                    elif gameInfo["possession"] == gameInfo["home name"] and gameInfo["play type"] == "TOUCHDOWN":
                        await gameChannel.send("The opposing team has submitted their number, " + homeDiscordUser.mention + " you're up!\n\n"
                                                    + "Please submit either **PAT** or **Two Point** and your number")
                        await messageConfirmationUser(awayDiscordUser, number)
                    elif gameInfo["possession"] == gameInfo["away name"] and gameInfo["play type"] == "TOUCHDOWN":
                        await gameChannel.send("The opposing team has submitted their number, " + awayDiscordUser.mention + " you're up!\n\n"
                                                    + "Please submit either **PAT** or **Two Point** and your number")
                        await messageConfirmationUser(homeDiscordUser, number)
                    elif gameInfo["possession"] == gameInfo["home name"] and gameInfo["play type"] == "SAFETY KICKOFF":
                        await gameChannel.send("The opposing team has submitted their number, " + homeDiscordUser.mention + " you're up!\n\n"
                                                    + "Please submit **punt** and your number")
                        await messageConfirmationUser(awayDiscordUser, number)
                    elif gameInfo["possession"] == gameInfo["away name"] and gameInfo["play type"] == "SAFETY KICKOFF":
                        await gameChannel.send("The opposing team has submitted their number, " + awayDiscordUser.mention + " you're up!\n\n"
                                                    + "Please submit **punt** and your number")
                        await messageConfirmationUser(homeDiscordUser, number)
                    elif gameInfo["possession"] == gameInfo["home name"] and gameInfo["play type"] == "CHANGE OF POSSESSION":
                        await gameChannel.send("The opposing team has submitted their number, " + homeDiscordUser.mention + " you're up!\n\n"
                                                    + "Please submit either **run**, **pass**, **punt**, **field goal**, **kneel**, or **spike** and your number")
                        await messageConfirmationUser(awayDiscordUser, number)
                        updatePlayType(gameChannel, "NORMAL")
                    elif gameInfo["possession"] == gameInfo["away name"] and gameInfo["play type"] == "CHANGE OF POSSESSION":
                        await gameChannel.send("The opposing team has submitted their number, " + awayDiscordUser.mention + " you're up!\n\n"
                                                    + "Please submit either **run**, **pass**, **punt**, **field goal**, **kneel**, or **spike** and your number")
                        await messageConfirmationUser(homeDiscordUser, number)
                        updatePlayType(gameChannel, "NORMAL")


                    if gameInfo["play type"] == "KICKOFF":
                        updateWaitingOnKickoffDM(gameChannel)
                    else:
                        updateWaitingOn(gameChannel)

                    updateNumberSubmitted(gameChannel, "YES")
        else:
            await message.author.send("I could not find one of the Discord users in the game database. Did a user change their username?")


#########################
#     TYPE OF PLAYS     #
#########################
async def safetyKickoff(client, message, gameInfo):
    """
    Handle how the bot deals with kickoff returns
    
    """

    # Handle invalid messages
    if "punt" not in message.content.lower():
        await message.channel.send("I could not find a play in your message, please try again and submit **punt**")
        return "INVALID"
    elif not hasNumbers(message.content):
        await message.channel.send("I could not find a number in your message, please try again and submit a number between 1-1500")
        return "INVALID"
    elif len(list(map(int, re.findall(r'\d+', message.content)))) > 1:
        await message.channel.send("I found multiple numbers in your message, please try again and submit a number between 1-1500")
        return "INVALID"
    # Valid message, get the play and number
    else:
        numList = list(map(int, re.findall(r'\d+', message.content)))
        number = numList[0]
        # Ensure number is valid
        if number < 1 or number > 1500:
            await message.channel.send("Your number is not valid, please try again and submit a number between 1-1500")
            return "INVALID"
        else:
            offensiveNumber = number
            updateOffensiveNumber(message.channel, offensiveNumber)
            defensiveNumber = gameInfo["defensive number"]
            difference = calculateDifference(offensiveNumber, defensiveNumber)

            if gameInfo["possession"] == gameInfo["home name"]:
                offenseTeam = gameInfo["home name"]
                defenseTeam = gameInfo["away name"]
            else:
                offenseTeam = gameInfo["away name"]
                defenseTeam = gameInfo["home name"]

            # Invalid difference
            if difference == -1:
                await message.channel.send("There was an issue calculating the difference, please contact Dick")
                return "INVALID"
            else:
                if gameInfo["possession"] == gameInfo["home name"]:
                    offensivePlaybook = gameInfo["home offensive playbook"]
                    defensivePlaybook = gameInfo["away defensive playbook"]
                else:
                    offensivePlaybook = gameInfo["away offensive playbook"]
                    defensivePlaybook = gameInfo["home defensive playbook"]

                # Get the result from the play
                result = getFinalPlayResult(message, offensivePlaybook, defensivePlaybook, "punt", difference, "none", "YES")
                # Update the time and game information
                convertTime(message.channel, gameInfo, result[1])
                gameInfo = getGameInfo(message.channel)
                if str(result[0]) != "punt":
                    await puntResult(client, message, gameInfo, result, offenseTeam, defenseTeam, difference)
                return "VALID"


async def normalPlay(client, message, gameInfo):
    """
    Handle normal plays in a college football game and determine the outcome (not PATs or kickoffs)
    
    """
    try:
        # Handle invalid messages
        if ("pass" not in message.content.lower() and "run" not in message.content.lower() and "punt" not in message.content.lower() and "field goal" not in message.content.lower()
        and "spike" not in message.content.lower() and "kneel" not in message.content.lower()):
            await message.channel.send("I could not find a play in your message, please try again and submit **run**, **pass**, **punt**, **field goal**, **kneel**, or **spike**")
            return "INVALID"
        elif not hasNumbers(message.content):
            await message.channel.send("I could not find a number in your message, please try again and submit a number between 1-1500")
            return "INVALID"
        elif len(list(map(int, re.findall(r'\d+', message.content)))) > 1:
            await message.channel.send("I found multiple numbers in your message, please try again and submit a number between 1-1500")
            return "INVALID"
        # Valid message, get the play and number
        else:
            numList = list(map(int, re.findall(r'\d+', message.content)))
            number = numList[0]
            # Ensure number is valid
            if number < 1 or number > 1500:
                await message.channel.send("Your number is not valid, please try again and submit a number between 1-1500")
                return "INVALID"
            else:
                offensiveNumber = number
                updateOffensiveNumber(message.channel, offensiveNumber)
                defensiveNumber = gameInfo["defensive number"]
                difference = calculateDifference(offensiveNumber, defensiveNumber)
                playType = ""
                timeout = 0

                # Get the play type
                if "run" in message.content.lower():
                    playType = "run"
                elif "pass" in message.content.lower():
                    playType = "pass"
                elif "punt" in message.content.lower():
                    playType = "punt"
                elif "field goal" in message.content.lower():
                    playType = "field goal"
                elif "kneel" in message.content.lower():
                    playType = "kneel"
                elif "spike" in message.content.lower():
                    playType = "spike"

                # Get the clock runoff
                if "chew" in message.content.lower():
                    clockRunoffType = "chew"
                elif "hurry" in message.content.lower():
                    clockRunoffType = "hurry"
                elif "final play" in message.content.lower():
                    clockRunoffType = "final play"
                else:
                    clockRunoffType = "normal"

                # See if there's a timeout
                if "timeout" in message.content.lower():
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
                        updateHalftime(message.channel, "YES")

                        # End of half
                        if int(gameInfo["quarter"]) + 1 == 3 or int(gameInfo["quarter"]) + 1 == 5:
                            endOfHalf = True
                            await message.channel.send("The half has ended. Did not get the play off in time\n")

                    if not endOfHalf:
                        result = getFinalPlayResult(message, offensivePlaybook, defensivePlaybook, playType, difference, clockRunoffType, clockStopped)

                        if gameInfo["possession"] == gameInfo["home name"]:
                            offenseTeam = gameInfo["home name"]
                            defenseTeam = gameInfo["away name"]
                        else:
                            offenseTeam = gameInfo["away name"]
                            defenseTeam = gameInfo["home name"]

                        if playType == "run":
                            await playResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference)
                        elif playType == "pass":
                            await playResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference)
                        elif playType == "punt":
                            await puntResult(client, message, gameInfo, result, offenseTeam, defenseTeam, difference)
                            updatePuntResult(result)
                        elif playType == "field goal":
                            await fieldGoalResult(client, message, gameInfo, result, offenseTeam, defenseTeam, difference)
                        elif playType == "kneel":
                            await kneelResult(client, message, gameInfo, result, offenseTeam, defenseTeam, difference)
                        elif playType == "spike":
                            await spikeResult(client, message, gameInfo, result, offenseTeam, defenseTeam, difference)

                    # Check if half or game is over
                    gameInfo = getGameInfo(message.channel)
                    if gameInfo["play type"] != "TOUCHDOWN" and endOfHalf is True or (int(gameInfo["quarter"]) == 3 and str(gameInfo["time"]) == "7:00") or (int(gameInfo["quarter"]) == 5 and str(gameInfo["time"]) == "7:00"):
                        updateHalftime(message.channel, "YES")
                        if gameInfo["play type"] == "TOUCHDOWN":
                            updateHalftime(message.channel, "YES")

                        elif int(gameInfo["quarter"]) == 5 and int(gameInfo["home score"]) != int(gameInfo["away score"]):
                            updatePlayType(message.channel, "GAME DONE")
                            updateHalftime(message.channel, "NO")

                        elif int(gameInfo["quarter"]) == 5 and int(gameInfo["home score"]) == int(gameInfo["away score"]):
                            updatePlayType(message.channel, "OVERTIME")
                            updateHalftime(message.channel, "NO")

                        # Handle halftime
                        elif int(gameInfo["quarter"]) == 3 and gameInfo["time"] == "7:00":
                            await handleHalftime(client, message, gameInfo)

                    return "VALID"
    except Exception:
        print("Invalid play due to " + str(Exception))
        raise Exception


async def kickoffReturn(message, homeDiscordUser, awayDiscordUser, gameInfo):
    """
    Handle how the bot deals with kickoff returns
    
    """
    try:
        # Handle invalid messages
        if "normal" not in message.content.lower() and "squib" not in message.content.lower() and "onside" not in message.content.lower():
            await message.channel.send("I could not find a play in your message, please try again and submit **normal**, **squib**, or **onside**")
            return "INVALID"
        elif not hasNumbers(message.content):
            await message.channel.send("I could not find a number in your message, please try again and submit a number between 1-1500")
            return "INVALID"
        elif len(list(map(int, re.findall(r'\d+', message.content)))) > 1:
            await message.channel.send("I found multiple numbers in your message, please try again and submit a number between 1-1500")
            return "INVALID"
        # Valid message, get the play and number
        else:
            numList = list(map(int, re.findall(r'\d+', message.content)))
            number = numList[0]
            # Ensure number is valid
            if number < 1 or number > 1500:
                await message.channel.send("Your number is not valid, please try again and submit a number between 1-1500")
                return "INVALID"
            else:
                offensiveNumber = number
                updateOffensiveNumber(message.channel, offensiveNumber)
                defensiveNumber = gameInfo["defensive number"]
                difference = calculateDifference(offensiveNumber, defensiveNumber)
                playType = ""
                if "normal" in message.content.lower():
                    playType = "normal"
                elif "onside" in message.content.lower():
                    playType = "onside"
                elif "squib" in message.content.lower():
                    playType = "squib"

                # Invalid difference
                if difference == -1:
                    await message.channel.send("There was an issue calculating the difference, please contact Dick")
                else:
                    # Get the result from the play
                    result = getFinalKickoffResult(playType, difference)
                    # Update the time and game information
                    convertTime(message.channel, gameInfo, result[1])
                    gameInfo = getGameInfo(message.channel)
                    if str(result[0]) != "Fumble" and str(result[0]) != "Touchdown":
                        if gameInfo["possession"] == gameInfo["home name"]:
                            await normalKickoff(message, gameInfo, result, playType, difference,
                                                str(gameInfo["home name"]), str(gameInfo["away name"]), homeDiscordUser)
                        if gameInfo["possession"] == gameInfo["away name"]:
                            await normalKickoff(message, gameInfo, result, playType, difference,
                                                str(gameInfo["away name"]), str(gameInfo["home name"]), awayDiscordUser)
                    if str(result[0]) == "Fumble":
                        if gameInfo["possession"] == gameInfo["home name"]:
                            await fumbleKickoff(message, gameInfo, result, playType, difference,
                                                str(gameInfo["home name"]), str(gameInfo["away name"]), awayDiscordUser)
                        if gameInfo["possession"] == gameInfo["away name"]:
                            await fumbleKickoff(message, gameInfo, result, playType, difference,
                                                str(gameInfo["away name"]), str(gameInfo["home name"]), homeDiscordUser)
                    if str(result[0]) == "Touchdown":
                        if gameInfo["possession"] == gameInfo["home name"]:
                            await fumbleReturnKickoff(message, gameInfo, result, playType, difference,
                                                      str(gameInfo["home name"]), str(gameInfo["away name"]), awayDiscordUser)
                        if gameInfo["possession"] == gameInfo["away name"]:
                            await fumbleReturnKickoff(message, gameInfo, result, playType, difference,
                                                      str(gameInfo["away name"]), str(gameInfo["home name"]), homeDiscordUser)
                    return "VALID"
    except Exception:
        print("Invalid kickoff due to " + str(Exception))
        raise Exception

async def pointAfterPlay(client, message, gameInfo):
    """
    Handle how the bot deals with PATs and two point conversions
    
    """
    try:
        # Handle invalid messages
        if "pat" not in message.content.lower() and "two point" not in message.content.lower():
            await message.channel.send("I could not find a play in your message, please try again and submit **two point** or **pat**")
            return "INVALID"
        elif not hasNumbers(message.content):
            await message.channel.send("I could not find a number in your message, please try again and submit a number between 1-1500")
            return "INVALID"
        elif len(list(map(int, re.findall(r'\d+', message.content)))) > 1:
            await message.channel.send("I found multiple numbers in your message, please try again and submit a number between 1-1500")
            return "INVALID"
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
                if "pat" in message.content.lower():
                    playType = "pat"
                elif "two point" in message.content.lower():
                    playType = "two point"

                # Invalid difference
                if difference == -1:
                    await message.channel.send("There was an issue calculating the difference, please contact Dick")
                else:
                    # Get the result from the play
                    result = getFinalPointAfterResult(playType, difference)

                    if gameInfo["possession"] == gameInfo["home name"]:
                        offenseTeam = gameInfo["home name"]
                        defenseTeam = gameInfo["away name"]
                    else:
                        offenseTeam = gameInfo["away name"]
                        defenseTeam = gameInfo["home name"]

                    if playType == "two point":
                        await twoPointResult(client, message, gameInfo, result, offenseTeam, defenseTeam, difference)
                    elif playType == "pat":
                        await patResult(client, message, gameInfo, result, offenseTeam, defenseTeam, difference)

                # If it is halftime or end of game, make sure you do the kickoff and adjust accordingly
                if gameInfo["halftime"] == "YES":
                    if int(gameInfo["quarter"]) == 5 and int(gameInfo["home score"]) != int(gameInfo["away score"]):
                        updatePlayType(message.channel, "GAME DONE")
                        updateHalftime(message.channel, "NO")

                    elif int(gameInfo["quarter"]) == 5 and int(gameInfo["home score"]) == int(gameInfo["away score"]):
                        updatePlayType(message.channel, "OVERTIME")
                        updateHalftime(message.channel, "NO")

                    # Handle halftime
                    elif int(gameInfo["quarter"]) == 3 and gameInfo["time"] == "7:00":
                        await handleHalftime(client, message, gameInfo)

                return "VALID"
    except Exception:
        print("Invalid PAT due to " + str(Exception))
        raise Exception

#########################
#      POINT AFTER      #
#########################  
async def twoPointResult(client, message, gameInfo, result, offenseTeam, defenseTeam, difference):
    """
    Update the database and post the message for a two point conversion
    
    """

    if str(gameInfo["possession"]) == str(gameInfo["home name"]):
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
        updateBallLocation(message.channel, str(gameInfo["home name"]) + " 35")
    else:
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        updateBallLocation(message.channel, str(gameInfo["away name"]) + " 35")

    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    updatePossession(message.channel, offenseTeam)
    updateClockStopped(message.channel, "YES")
    updatePlayType(message.channel, "KICKOFF")

    if str(result[0]) == "Good":
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        if offenseTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 2)
        elif offenseTeam == gameInfo["away name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 2)

        gameInfo = getGameInfo(message.channel)

        await message.channel.send(offenseTeam + " goes for two and....... THEY GET IT!!\n\n"
                                   + "**Result:** Two point conversion is successful\n"
                                   + getScoreboardString(message, difference, down, offenseTeam, defenseDiscordUser))
        await messageUser(defenseDiscordUser, gameInfo)
        updateWaitingOnUser(str(defenseDiscordUser.name) + "#" + str(defenseDiscordUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "TWO POINT", str(result[0]), "0", "0")

    elif str(result[0]) == "No Good":
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))

        await message.channel.send(offenseTeam + " goes for two and....... THEY DON'T GET IT!!\n\n"
                                   + "**Result:** Two point conversion is unsuccessful\n"
                                   + getScoreboardString(message, difference, down, offenseTeam, defenseDiscordUser))
        await messageUser(defenseDiscordUser, gameInfo)
        updateWaitingOnUser(str(defenseDiscordUser.name) + "#" + str(defenseDiscordUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "TWO POINT", str(result[0]), "0", "0")

    elif str(result[0]) == "Defense 2PT":
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        if offenseTeam == gameInfo["home name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 2)
        elif offenseTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 2)

        gameInfo = getGameInfo(message.channel)

        await message.channel.send(offenseTeam + " goes for two and....... IT IS INTERCEPTED AT THE GOAL LINE!! THE " + defenseTeam.upper() + " DEFENDER HAS AN OPEN FIELD AND WILL TAKE IT FOR TWO THE OTHER WAY!\n\n"
                                   + "**Result:** Two point conversion is unsuccessful and taken for a defensive two point conversion\n"
                                   + getScoreboardString(message, difference, down, offenseTeam, defenseDiscordUser))
        await messageUser(defenseDiscordUser, gameInfo)
        updateWaitingOnUser(str(defenseDiscordUser.name) + "#" + str(defenseDiscordUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "TWO POINT", str(result[0]), "0", "0")

    updatePossession(message.channel, offenseTeam)


async def patResult(client, message, gameInfo, result, offenseTeam, defenseTeam, difference):
    """
    Update the database and post the message for a PAT
    
    """

    if str(gameInfo["possession"]) == str(gameInfo["home name"]):
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
        updateBallLocation(message.channel, str(gameInfo["home name"]) + " 35")
    else:
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        updateBallLocation(message.channel, str(gameInfo["away name"]) + " 35")

    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    updatePossession(message.channel, offenseTeam)
    updateClockStopped(message.channel, "YES")
    updatePlayType(message.channel, "KICKOFF")

    if str(result[0]) == "Good":
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        if offenseTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 1)
        elif offenseTeam == gameInfo["away name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 1)

        gameInfo = getGameInfo(message.channel)
        await message.channel.send(offenseTeam + " attempts the PAT and it is right down the pipe.\n\n"
                                   + "**Result:** PAT is successful\n"
                                   + getScoreboardString(message, difference, down, offenseTeam, defenseDiscordUser))
        await messageUser(defenseDiscordUser, gameInfo)
        updateWaitingOnUser(str(defenseDiscordUser.name) + "#" + str(defenseDiscordUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PAT", str(result[0]), "0", "0")

    elif str(result[0]) == "No Good":
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))

        await message.channel.send(offenseTeam + " attempts the PAT and it goes wide!!\n\n"
                                   + "**Result:** PAT is unsuccessful\n"
                                   + getScoreboardString(message, difference, down, offenseTeam, defenseDiscordUser))
        await messageUser(defenseDiscordUser, gameInfo)
        updateWaitingOnUser(str(defenseDiscordUser.name) + "#" + str(defenseDiscordUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PAT", str(result[0]), "0", "0")

    elif str(result[0]) == "Defense 2PT":
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))
        if offenseTeam == gameInfo["home name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 2)
        elif offenseTeam == gameInfo["home name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 2)

        gameInfo = getGameInfo(message.channel)
        await message.channel.send(offenseTeam + " attempts the PAT AND IT IS BLOCKED!! IT IS SCOOPED UP BY A " + defenseTeam.upper() + " DEFENDER WHO HAS AN OPEN FIELD AND WILL TAKE IT FOR TWO THE OTHER WAY!\n\n"
                                   + "**Result:** Two point conversion is unsuccessful and taken for a defensive two point conversion\n"
                                   + getScoreboardString(message, difference, down, offenseTeam, defenseDiscordUser))
        await messageUser(defenseDiscordUser, gameInfo)
        updateWaitingOnUser(str(defenseDiscordUser.name) + "#" + str(defenseDiscordUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PAT", str(result[0]), "0", "0")

    updatePossession(message.channel, offenseTeam)



#########################
#         SPIKE         #
#########################     
async def spikeResult(client, message, gameInfo, result, offenseTeam, defenseTeam, difference):
    """
    Update the database and post the message for a spike
    
    """

    if str(gameInfo["possession"]) == str(gameInfo["home name"]):
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

    # Handle turnover on downs
    if down + 1 > 4:
        finalResult = "spikes it on 4th and turns it over!!! What a mistake!\n\n"
        updateDown(message.channel, 1)
        updateDistance(message.channel, 10)
        updatePossession(message.channel, defenseTeam)
        updateClockStopped(message.channel, "YES")
        updatePlayType(message.channel, "NORMAL")
        convertTime(message.channel, gameInfo, result[1])
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))

        await message.channel.send(offenseTeam + finalResult
                                   + "**Result:** spike on 4th down for a turnover\n"
                                   + getScoreboardString(message, difference, down, defenseTeam, offenseDiscordUser))
        await messageUser(offenseDiscordUser, gameInfo)
        updateWaitingOnUser(str(offenseDiscordUser.name) + "#" + str(offenseDiscordUser.discriminator))
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

        await message.channel.send(offenseTeam + finalResult
                                   + "**Result:** spike\n"
                                   + getScoreboardString(message, difference, down, offenseTeam, defenseDiscordUser))
        await messageUser(defenseDiscordUser, gameInfo)
        updateWaitingOnUser(str(defenseDiscordUser.name) + "#" + str(defenseDiscordUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "SPIKE", "INCOMPLETE", "0", result[1])


#########################
#         KNEEL         #
#########################          
async def kneelResult(client, message, gameInfo, result, offenseTeam, defenseTeam, difference):
    """
    Update the database and post the message for a kneel
    
    """
    if str(gameInfo["possession"]) == str(gameInfo["home name"]):
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

    # Handle safety
    if yardLine + 2 > 100:
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

        await message.channel.send(offenseTeam + finalResult
                                   + "**Result:** kneels in the end zone for a safety\n"
                                   + getScoreboardString(message, difference, down, offenseTeam, offenseDiscordUser))
        await messageUser(defenseDiscordUser, gameInfo)
        updateWaitingOnUser(str(defenseDiscordUser.name) + "#" + str(defenseDiscordUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "KNEEL", "SAFETY", "-2", result[1])

    # Handle turnover on downs
    elif down + 1 > 4:
        finalResult = "kneels it on 4th down and turns it over!!! What a mistake!\n\n"
        updateDown(message.channel, 1)
        updateDistance(message.channel, 10)
        updatePossession(message.channel, defenseTeam)
        updateClockStopped(message.channel, "YES")
        updatePlayType(message.channel, "NORMAL")
        convertTime(message.channel, gameInfo, result[1])
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))

        await message.channel.send(offenseTeam + finalResult
                                   + "**Result:** kneels on 4th down for a turnover\n"
                                   + getScoreboardString(message, difference, down, defenseTeam, offenseDiscordUser))
        await messageUser(offenseDiscordUser, gameInfo)
        updateWaitingOnUser(str(offenseDiscordUser.name) + "#" + str(offenseDiscordUser.discriminator))
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

        await message.channel.send(offenseTeam + finalResult
                                   + "**Result:** kneels\n"
                                   + getScoreboardString(message, difference, down, offenseTeam, defenseDiscordUser))
        await messageUser(defenseDiscordUser, gameInfo)
        updateWaitingOnUser(str(defenseDiscordUser.name) + "#" + str(defenseDiscordUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "KNEEL", "KNEEL", "-2", result[1])



#########################
#      FIELD GOAL       #
#########################
async def fieldGoalResult(client, message, gameInfo, result, kickingTeam, defenseTeam, difference):
    """
    Determine which field goal result updater to go to
    
    """
    if str(gameInfo["possession"]) == str(gameInfo["home name"]):
        kickingDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
    else:
        kickingDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))

    if str(result[0]) == "Made":
        await fieldGoalMade(message, gameInfo, result, defenseDiscordUser, kickingTeam, difference)
    elif str(result[0]) == "Miss":
        await fieldGoalMiss(message, gameInfo, result, kickingDiscordUser, kickingTeam, defenseTeam, difference)
        updatePlayType(message.channel, "CHANGE OF POSSESSION")
    elif str(result[0]) == "Blocked":
        await fieldGoalBlocked(message, gameInfo, result, kickingDiscordUser, defenseTeam, difference)
        updatePlayType(message.channel, "CHANGE OF POSSESSION")
    elif str(result[0]) == "Kick 6":
        await fieldGoalKickSix(message, gameInfo, result, kickingDiscordUser, kickingTeam, defenseTeam, difference)

async def fieldGoalMade(message, gameInfo, result, defenseUser, kickingTeam, difference):
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

    await message.channel.send(kickingTeam + " drills a " + str(fieldGoalDistance) + " yard field goal!\n\n"
                               + "**Result:** " + str(fieldGoalDistance) + " yard field goal is **good**\n"
                               + getScoreboardString(message, difference, down, kickingTeam, defenseUser))
    await messageUser(defenseUser, gameInfo)
    updateWaitingOnUser(str(defenseUser.name) + "#" + str(defenseUser.discriminator))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "FIELD GOAL", "GOOD", str(fieldGoalDistance) + " ATTEMPT", result[1])


async def fieldGoalMiss(message, gameInfo, result, kickingUser, kickingTeam, defenseTeam, difference):
    """
    Update the database and post the message for a missed field goal
    
    """

    yardLine = convertYardLine(gameInfo)
    fieldGoalDistance = yardLine + 17

    yardLine = convertYardLine(gameInfo)  # Line of scrimmage
    if yardLine >= 20:
        updatedYardLine = 100 - yardLine  # Flip the yard line to the opponent's side
        convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, convertedYardLine)
    else:
        updatedYardLine = 80  # Place the ball on the 20
        convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, convertedYardLine)

    updatePlayType(message.channel, "NORMAL")
    updateClockStopped(message.channel, "YES")
    updatePossession(message.channel, defenseTeam)

    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))

    await message.channel.send(kickingTeam + " misses the " + str(fieldGoalDistance) + " yard field goal.\n\n"
                               + "**Result:** " + str(fieldGoalDistance) + " yard field goal is **no good**\n"
                               + getScoreboardString(message, difference, down, defenseTeam, kickingUser))
    await messageUser(kickingUser, gameInfo)
    updateWaitingOnUser(str(kickingUser.name) + "#" + str(kickingUser.discriminator))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "FIELD GOAL", "MISS", str(fieldGoalDistance) + " ATTEMPT", result[1])


async def fieldGoalBlocked(message, gameInfo, result, kickingUser, defenseTeam, difference):
    """
    Update the database and post the message for a blocked field goal
    
    """

    yardLine = convertYardLine(gameInfo)
    fieldGoalDistance = yardLine + 17

    yardLine = convertYardLine(gameInfo)  # Line of scrimmage
    if yardLine >= 20:
        updatedYardLine = 100 - yardLine  # Flip the yard line to the opponent's side
        convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, convertedYardLine)
    else:
        updatedYardLine = 80  # Place the ball on the 20
        convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, convertedYardLine)

    updatePlayType(message.channel, "NORMAL")
    updateClockStopped(message.channel, "YES")
    updatePossession(message.channel, defenseTeam)

    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))

    await message.channel.send(defenseTeam + " blocks the " + str(fieldGoalDistance) + " yard field goal!!!!\n\n"
                               + "**Result:** " + str(fieldGoalDistance) + " yard field goal is **blocked**\n"
                               + getScoreboardString(message, difference, down, defenseTeam, kickingUser))
    await messageUser(kickingUser, gameInfo)
    updateWaitingOnUser(str(kickingUser.name) + "#" + str(kickingUser.discriminator))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "FIELD GOAL", "BLOCKED", str(fieldGoalDistance) + " ATTEMPT", result[1])


async def fieldGoalKickSix(message, gameInfo, result, kickingUser, kickingTeam, defenseTeam, difference):
    """
    Update the database and post the message for a blocked field goal
    
    """

    yardLine = convertYardLine(gameInfo)
    fieldGoalDistance = yardLine + 17
    updatePossession(message.channel, defenseTeam)

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


    await message.channel.send(defenseTeam + " blocks the " + str(fieldGoalDistance) + " yard field goal!!!! AND THEY HAVE THE BALL AND HAVE A BLOCKER! THEY'LL TAKE IT IN FOR SIX! TOUCHDOWN " + defenseTeam.upper() + "!!!\n\n"
                               + "**Result:** " + str(fieldGoalDistance) + " yard field goal is blocked and returned for a **kick six**\n"
                               + getScoreboardString(message, difference, down, defenseTeam, kickingUser))
    await messageUser(kickingUser, gameInfo)
    updateWaitingOnUser(str(kickingUser.name) + "#" + str(kickingUser.discriminator))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "FIELD GOAL", "KICK SIX", str(fieldGoalDistance) + " ATTEMPT", result[1])


#########################
#        PUNTS          #
#########################
async def puntResult(client, message, gameInfo, result, puntTeam, returnTeam, difference):
    """
    Determine which punt result updater to go to
    
    """
    if str(gameInfo["possession"]) == str(gameInfo["home name"]):
        puntDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        returnDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
    else:
        puntDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
        returnDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))

    # If it's not a standard return
    if not representsInt(result[0]):
        if str(result[0]) == "Punt Six":
            await puntReturnTouchdown(message, result, puntDiscordUser, puntTeam, returnTeam, difference)
            updatePlayType(message.channel, "TOUCHDOWN")
        elif str(result[0]) == "Blocked":
            await puntBlock(message, result, puntDiscordUser, returnTeam, difference)
            updatePlayType(message.channel, "CHANGE OF POSSESSION")
        elif str(result[0]) == "Touchback":
            await puntTouchback(message, result, puntDiscordUser, puntTeam, returnTeam, difference)
            updatePlayType(message.channel, "CHANGE OF POSSESSION")
        elif str(result[0]) == "Fumble":
            await puntFumble(message, result, returnDiscordUser, puntTeam, returnTeam, difference)
            updatePlayType(message.channel, "CHANGE OF POSSESSION")
        elif str(result[0]) == "Touchdown":
            await puntTeamTouchdown(message, result, returnDiscordUser, puntTeam, returnTeam, difference)
            updatePlayType(message.channel, "TOUCHDOWN")
    else:
        await punt(message, result, puntDiscordUser, returnTeam, difference)
        updatePlayType(message.channel, "CHANGE OF POSSESSION")

"""
Handle punt return specifics

"""
async def punt(message, result, puntUser, returnTeam, difference):
    """
    Update the database and post the message for a standard punt return
    
    """

    gameInfo = getGameInfo(message.channel)
    puntYardage = int(result[0])
    yardLine = convertYardLine(gameInfo)  # Line of scrimmage
    updatedYardLine = yardLine - puntYardage
    updatedYardLine = 100-updatedYardLine  # Flip the yard line to the opponent's side
    convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)

    updateBallLocation(message.channel, convertedYardLine)
    updatePlayType(message.channel, "NORMAL")
    updateClockStopped(message.channel, "YES")
    updatePossession(message.channel, returnTeam)

    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))

    if puntYardage > 35:
        await message.channel.send(returnTeam + " calls for a fair catch " + str(puntYardage) + " yards downfield\n\n"
                                   + "**Result:** " + str(puntYardage) + " net yard punt\n"
                                   + getScoreboardString(message, difference, down, returnTeam, puntUser))
    else:
        await message.channel.send(returnTeam + " attempts to return it and gets taken down for a net " + str(puntYardage) + " yard punt\n\n"
                                   + "**Result:** " + str(puntYardage) + " net yard punt\n"
                                   + getScoreboardString(message, difference, down, returnTeam, puntUser))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "PUNT", str(puntYardage) + " NET YARD PUNT", result[1])
    await messageUser(puntUser, gameInfo)
    updateWaitingOnUser(str(puntUser.name) + "#" + str(puntUser.discriminator))


async def puntReturnTouchdown(message, result, puntUser, puntTeam, returnTeam, difference):
    """
    Update the database and post the message for a punt return touchdown
    
    """
    updatePossession(message.channel, returnTeam)
    gameInfo = getGameInfo(message.channel)
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
                               + getScoreboardString(message, difference, down, returnTeam, puntUser))
    await messageUser(puntUser, gameInfo)
    updateWaitingOnUser(str(puntUser.name) + "#" + str(puntUser.discriminator))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "PUNT RETURN TD", "PUNT RETURN TD", result[1])


async def puntBlock(message, result, puntUser, returnTeam, difference):
    """
    Update the database and post the message for a blocked punt return
    
    """

    gameInfo = getGameInfo(message.channel)
    yardLine = convertYardLine(gameInfo)
    updatedYardLine = 100 - yardLine
    convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)

    updateBallLocation(message.channel, convertedYardLine)
    updatePlayType(message.channel, "NORMAL")
    updateClockStopped(message.channel, "YES")
    updatePossession(message.channel, returnTeam)

    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))

    await message.channel.send(returnTeam.upper() + " BLOCKS THE PUNT!\n\n"
                               + "**Result:** Blocked Punt\n"
                               + getScoreboardString(message, difference, down, returnTeam, puntUser))
    await messageUser(puntUser, gameInfo)
    updateWaitingOnUser(str(puntUser.name) + "#" + str(puntUser.discriminator))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "PUNT BLOCK", "PUNT BLOCK", result[1])


async def puntTouchback(message, result, puntUser, puntTeam, returnTeam, difference):
    """
    Update the database and post the message for a touchback punt
    
    """

    gameInfo = getGameInfo(message.channel)
    updatedYardLine = 80
    updatePossession(message.channel, returnTeam)
    convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)
    updatePossession(message.channel, returnTeam)

    updateBallLocation(message.channel, convertedYardLine)
    updatePlayType(message.channel, "NORMAL")
    updateClockStopped(message.channel, "YES")

    convertTime(message.channel, gameInfo, result[1])
    updateDown(message.channel, 1)
    updateDistance(message.channel, 10)
    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))

    await message.channel.send(puntTeam + " kicks it into the endzone for a touchback.\n\n"
                               + "**Result:** Touchback\n"
                               + getScoreboardString(message, difference, down, returnTeam, puntUser))
    await messageUser(puntUser, gameInfo)
    updateWaitingOnUser(str(puntUser.name) + "#" + str(puntUser.discriminator))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "PUNT", "TOUCHBACK", result[1])


async def puntFumble(message, result, returnUser, puntTeam, returnTeam, difference):
    """
    Update the database and post the message for a muffed punt
    
    """

    gameInfo = getGameInfo(message.channel)
    yardLine = convertYardLine(gameInfo)
    updatedYardLine = int(yardLine) - 40
    convertedYardLine = convertYardLineBack(updatedYardLine, gameInfo)

    # Handle touchdown
    if updatedYardLine <= 0:
        updateBallLocation(message.channel, returnTeam + " 3")
        updatePlayType(message.channel, "TOUCHDOWN")
        updatePossession(message.channel, puntTeam)
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
                                   + getScoreboardString(message, difference, down, puntTeam, returnUser))
        await messageUser(returnUser, gameInfo)
        updateWaitingOnUser(str(returnUser.name) + "#" + str(returnUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "MUFF PUNT TD", "MUFF PUNT TD", result[1])
    # Handle normal muff
    else:
        updateBallLocation(message.channel, convertedYardLine)
        updatePlayType(message.channel, "NORMAL")
        updateClockStopped(message.channel, "YES")
        updatePossession(message.channel, puntTeam)

        convertTime(message.channel, gameInfo, result[1])
        updateDown(message.channel, 1)
        updateDistance(message.channel, 10)
        gameInfo = getGameInfo(message.channel)
        down = convertDown(str(gameInfo["down"]))

        await message.channel.send(returnTeam + " muffs the punt 40 yards downfield!!! AND " + puntTeam.upper() + " RECOVERS!!!\n\n"
                                   + "**Result:** Muffed punt\n"
                                   + getScoreboardString(message, difference, down, puntTeam, returnUser))
        await messageUser(returnUser, gameInfo)
        updateWaitingOnUser(str(returnUser.name) + "#" + str(returnUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "MUFFED PUNT", "MUFFED PUNT", result[1])


async def puntTeamTouchdown(message, result, returnUser, puntTeam, returnTeam, difference):
    """
    Update the database and post the message for a muffed punt and touchdown
    
    """

    updatePossession(message.channel, puntTeam)
    gameInfo = getGameInfo(message.channel)
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
                               + getScoreboardString(message, difference, down, puntTeam, returnUser))
    await messageUser(returnUser, gameInfo)
    updateWaitingOnUser(str(returnUser.name) + "#" + str(returnUser.discriminator))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, "PUNT", "MUFF PUNT TD", "MUFF PUNT TD", result[1])




#########################
#      NORMAL PLAY      #
#########################              
async def playResult(client, message, gameInfo, result, playType, offenseTeam, defenseTeam, difference):
    """
    Determine which play result updater to go to
    
    """

    if str(gameInfo["possession"]) == str(gameInfo["home name"]):
        offenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
    else:
        offenseDiscordUser = getDiscordUser(client, str(gameInfo["away user"]))
        defenseDiscordUser = getDiscordUser(client, str(gameInfo["home user"]))

    # If it's not a standard gain
    if not representsInt(result[0]):
        if str(result[0]) == "Pick/Fumble 6":
            await defensiveTouchdown(message, gameInfo, result, playType, offenseDiscordUser, offenseTeam, defenseTeam, difference)
        elif "TO + " in str(result[0]) or "TO - " in str(result[0]) or "Turnover" in str(result[0]):
            await turnover(message, gameInfo, result, playType, offenseDiscordUser, offenseTeam, defenseTeam, difference)
        elif str(result[0]) == "No Gain" or str(result[0]) == "Incompletion" or str(result[0]) == "Touchdown":
            await play(message, gameInfo, result, playType, offenseDiscordUser, defenseDiscordUser, offenseTeam, defenseTeam, difference)
    else:
        await play(message, gameInfo, result, playType, offenseDiscordUser, defenseDiscordUser, offenseTeam, defenseTeam, difference)


async def play(message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference):
    """
    Sort through the different types of standard plays
    
    """
    if not representsInt(result[0]):
        if str(result[0]) == "No Gain":
            await normalPlayType(message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference, 0)
            updateClockStopped(message.channel, "NO")
        elif str(result[0]) == "Incompletion":
            await normalPlayType(message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference, 0)
            updateClockStopped(message.channel, "YES")
        elif str(result[0]) == "Touchdown":
            await normalPlayType(message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference, 110)
            updateClockStopped(message.channel, "YES")
    else:
        await normalPlayType(message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference, int(result[0]))


async def normalPlayType(message, gameInfo, result, playType, offenseUser, defenseUser, offenseTeam, defenseTeam, difference, yards):
    """
    Update the database and post the message for a normal play (run or pass)
    
    """

    finalResult = offenseTeam + " gains " + str(yards) + " yards."
    yardLine = convertYardLine(gameInfo)
    updatedYardLine = yardLine - yards

    # Handle touchdown
    if updatedYardLine <= 0:
        updateBallLocation(message.channel, defenseTeam + " 3")
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
                                   + getScoreboardString(message, difference, down, offenseTeam, defenseUser))
        await messageUser(defenseUser, gameInfo)
        updateWaitingOnUser(str(defenseUser.name) + "#" + str(defenseUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "TOUCHDOWN", str(yards), result[1])

    # Handle safety
    elif updatedYardLine > 100:
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
                                   + getScoreboardString(message, difference, down, offenseTeam, defenseUser))

        await messageUser(defenseUser, gameInfo)
        updateWaitingOnUser(str(defenseUser.name) + "#" + str(defenseUser.discriminator))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "SAFETY", str(yards), result[1])

    # Handle a standard play
    else:
        down = int(gameInfo["down"])
        distance = int(gameInfo["distance"])
        newYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, newYardLine)
        turnoverOnDownsFlag = False

        distanceToGo = distance - yards
        if distanceToGo <= 0:
            finalResult = finalResult + " It is good enough for a first down!\n"
            updateDown(message.channel, 1)
            updateDistance(message.channel, 10)
        else:
            # Handle turnover on downs
            if down + 1 > 4:
                finalResult = finalResult + " It won't be good enough for a first down! Turnover on downs\n"
                updateDown(message.channel, 1)
                updateDistance(message.channel, 10)
                updatePossession(message.channel, defenseTeam)
                newYardLine = convertYardLineBack(100-updatedYardLine, gameInfo)
                updateBallLocation(message.channel, newYardLine)
                updateClockStopped(message.channel, "YES")
                updatePlayType(message.channel, "CHANGE OF POSSESSION")
                turnoverOnDownsFlag = True
            # Update the distance and down
            else:
                finalResult = finalResult + " \n"
                updateDown(message.channel, down + 1)
                updateDistance(message.channel, distanceToGo)

        gameInfo = getGameInfo(message.channel)
        convertTime(message.channel, gameInfo, result[1])

        incompleteFlag = False
        if not representsInt(result[0]):
            if result[0] == "Incompletion":
                incompleteFlag = True

        down = convertDown(str(gameInfo["down"]))

        if incompleteFlag and turnoverOnDownsFlag is False:
            updateClockStopped(message.channel, "YES")
            await message.channel.send("The pass is incomplete\n\n"
                                       + "**Result:** Incomplete pass\n"
                                       + getScoreboardString(message, difference, down, offenseTeam, defenseUser))
            await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "INCOMPLETE", str(yards), result[1])
            await messageUser(defenseUser, gameInfo)
            updateWaitingOnUser(str(defenseUser.name) + "#" + str(defenseUser.discriminator))
        elif turnoverOnDownsFlag:
            updateClockStopped(message.channel, "YES")
            await message.channel.send(offenseTeam + " doesn't get enough on 4th down! Turnover on downs!\n\n"
                                       + "**Result:** Turnover on Downs\n"
                                       + getScoreboardString(message, difference, down, defenseTeam, offenseUser))
            await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "CHANGE OF POSSESSION", str(yards), result[1])
            await messageUser(offenseUser, gameInfo)
            updateWaitingOnUser(str(offenseUser.name) + "#" + str(offenseUser.discriminator))
        else:
            if yards >= 0:
                updateClockStopped(message.channel, "NO")
                await message.channel.send(offenseTeam + " gets a " + str(yards) + " yard gain.\n\n"
                                           + "**Result:** " + finalResult
                                           + getScoreboardString(message, difference, down, offenseTeam, defenseUser))
                await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "GAIN", str(yards), result[1])
                await messageUser(defenseUser, gameInfo)
                updateWaitingOnUser(str(defenseUser.name) + "#" + str(defenseUser.discriminator))
            else:
                updateClockStopped(message.channel, "NO")
                await message.channel.send(offenseTeam + " has a " + str(yards) + " yard loss!\n\n"
                                           + "**Result:** loss of " + str(yards) + "\n"
                                           + getScoreboardString(message, difference, down, offenseTeam, defenseUser))
                await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "LOSS", str(yards), result[1])
                await messageUser(defenseUser, gameInfo)
                updateWaitingOnUser(str(defenseUser.name) + "#" + str(defenseUser.discriminator))



async def turnover(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference):
    """
    Go through all the turnover scenarios
    
    """

    if str(result[0]) == "TO + 20 YDs":
        await turnoverType(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, 20)
    elif str(result[0]) == "TO + 15 YDs":
        await turnoverType(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, 15)
    elif str(result[0]) == "TO + 10 YDs":
        await turnoverType(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, 10)
    elif str(result[0]) == "TO + 5 YDs":
        await turnoverType(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, 5)
    elif str(result[0]) == "Turnover":
        await turnoverType(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, 0)
    elif str(result[0]) == "TO - 5 YDs":
        await turnoverType(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, -5)
    elif str(result[0]) == "TO - 10 YDs":
        await turnoverType(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, -10)
    elif str(result[0]) == "TO - 15 YDs":
        await turnoverType(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, -15)
    elif str(result[0]) == "TO - 20 YDs":
        await turnoverType(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, -20)
    updatePlayType(message.channel, "CHANGE OF POSSESSION")

async def turnoverType(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference, turnoverDistance):
    """
    Update the database and post the message for a turnover based on the turnover yardage given
    
    """

    finalResult = defenseTeam + " gets a turnover of " + str(turnoverDistance) + " yards\n"
    yardLine = convertYardLine(gameInfo)
    updatedYardLine = 100-yardLine
    updatedYardLine = updatedYardLine - turnoverDistance

    # Handle touchdown
    if updatedYardLine <= 0:
        updateBallLocation(message.channel, defenseTeam + " 3")
        updatePlayType(message.channel, "TOUCHDOWN")
        if offenseTeam == gameInfo["home name"]:
            updateAwayScore(message.channel, int(gameInfo["away score"]) + 6)
        elif offenseTeam == gameInfo["away name"]:
            updateHomeScore(message.channel, int(gameInfo["home score"]) + 6)

    # Handle touchback
    elif updatedYardLine > 100:
        updateBallLocation(message.channel, defenseTeam + " 20")
        updatePlayType(message.channel, "NORMAL")

    else:
        newYardLine = convertYardLineBack(updatedYardLine, gameInfo)
        updateBallLocation(message.channel, newYardLine)

    updatePossession(message.channel, defenseTeam)
    updateClockStopped(message.channel, "YES")
    updateDown(message.channel, "1")
    updateDistance(message.channel, "10")
    convertTime(message.channel, gameInfo, result[1])

    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))

    await message.channel.send("OH NO! " + offenseTeam.upper() + " GIVES UP THE BALL! " + defenseTeam.upper() + " HAS IT!!!\n\n"
                               + "**Result:** " + finalResult
                               + getScoreboardString(message, difference, down, defenseTeam, offenseUser))

    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "TURNOVER", "TURNOVER", result[1])
    await messageUser(offenseUser, gameInfo)
    updateWaitingOnUser(str(offenseUser.name) + "#" + str(offenseUser.discriminator))


async def defensiveTouchdown(message, gameInfo, result, playType, offenseUser, offenseTeam, defenseTeam, difference):
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

    await message.channel.send("OH NO! " + offenseTeam.upper() + " GIVES UP THE BALL! " + defenseTeam.upper() + " HAS IT AND THEY'RE WEAVING DOWNFIELD AND THEY TAKE IT TO THE HOUSE! TOUCHDOWN " + defenseTeam.upper() + "!!!\n\n"
                               + "**Result:** " + finalResult
                               + getScoreboardString(message, difference, down, defenseTeam, offenseUser))

    await messageUser(offenseUser, gameInfo)
    updateWaitingOnUser(str(offenseUser.name) + "#" + str(offenseUser.discriminator))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "TURNOVER TD", "TURNOVER TD", result[1])




#########################
#        KICKOFFS       #
#########################
async def fumbleReturnKickoff(message, gameInfo, result, playType, difference, kickingTeam, returnTeam, returnUser):
    """
    Update the database and post the message for a fumble on the kickoff returned for a touchdown
    
    """

    updatePossession(message.channel, kickingTeam)
    if playType == "normal":
        updateNormalKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
        updateNormalKickoffResult(result)
    elif playType == "squib":
        updateSquibKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
        updateSquibKickoffResult(result)
    elif playType == "onside":
        updateOnsideKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
        updateOnsideKickoffResult(result)

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
                               + getScoreboardString(message, difference, down, kickingTeam, returnUser))
    await messageUser(returnUser, gameInfo)
    updateWaitingOnUser(str(returnUser.name) + "#" + str(returnUser.discriminator))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "MUFFED KICKOFF TD", "MUFFED KICKOFF TD", result[1])
    updatePlayType(message.channel, "TOUCHDOWN")


async def fumbleKickoff(message, gameInfo, result, playType, difference, kickingTeam, returnTeam, returnUser):
    """
    Update the database and post the message for a fumble on the kickoff
    
    """

    updatePossession(message.channel, kickingTeam)
    if playType == "normal":
        updateNormalKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
        updateNormalKickoffResult(result)
    elif playType == "squib":
        updateSquibKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
        updateSquibKickoffResult(result)
    elif playType == "onside":
        updateOnsideKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
        updateOnsideKickoffResult(result)

    gameInfo = getGameInfo(message.channel)
    updateDown(message.channel, "1")
    updateDistance(message.channel, "10")
    down = convertDown(str(gameInfo["down"]))

    await message.channel.send("OH NO! " + returnTeam.upper() + " FUMBLES THE BALL ON THE 20 AND " + kickingTeam.upper() + " HAS IT!\n\n"
                               + "**Result:** Fumble\n"
                               + getScoreboardString(message, difference, down, kickingTeam, returnUser))
    await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "MUFFED KICKOFF", "MUFFED KICKOFF", result[1])
    await messageUser(returnUser, gameInfo)
    updateWaitingOnUser(str(returnUser.name) + "#" + str(returnUser.discriminator))
    updatePlayType(message.channel, "NORMAL")


async def normalKickoff(message, gameInfo, result, playType, difference, kickingTeam, returnTeam, kickingUser):
    """
    Update the database and post the message for a standard kickoff
    
    """

    updatePossession(message.channel, returnTeam)
    if playType == "normal":
        updateNormalKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
        updateNormalKickoffResult(result)
    elif playType == "squib":
        updateSquibKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
        updateSquibKickoffResult(result)
    elif playType == "onside":
        updateOnsideKickoffBallLocation(message.channel, str(gameInfo["home name"]), str(gameInfo["away name"]), str(result[0]), str(gameInfo["possession"]))
        updateOnsideKickoffResult(result)
    updateDown(message.channel, "1")
    updateDistance(message.channel, "10")

    gameInfo = getGameInfo(message.channel)
    down = convertDown(str(gameInfo["down"]))

    if str(result[0]) == "25":
        await message.channel.send("It's a touchback.\n\n"
                                   + "**Result:** Touchback\n"
                                   + getScoreboardString(message, difference, down, returnTeam, kickingUser))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "KICKOFF RETURN", "RETURN TO THE " + str(gameInfo["yard line"]).upper(), result[1])
        updatePlayType(message.channel, "NORMAL")
    elif str(result[0]) == "Recovered":
        await message.channel.send("It's an onside kick.... AND " + kickingTeam.upper() + " RECOVERS IT!!\n\n"
                                   + "**Result:** Successful onside kick\n"
                                   + getScoreboardString(message, difference, down, returnTeam, kickingUser))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "ONSIDE KICK",
                            "SUCCESS", result[1])
        updatePlayType(message.channel, "NORMAL")
    elif str(result[0]) == "No Good":
        await message.channel.send("It's an onside kick.... and " + returnTeam + " falls on it.\n\n"
                                   + "**Result:**Unsuccessful onside kick\n"
                                   + getScoreboardString(message, difference, down, returnTeam, kickingUser))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "ONSIDE KICK",
                            "UNSUCCESSFUL", result[1])
        updatePlayType(message.channel, "NORMAL")
    elif str(result[0]) != "Returned TD":
        await message.channel.send("It's a kickoff taken by " + returnTeam + " to the " + gameInfo["yard line"] + "\n\n"
                                   + "**Result:** Return to the " + gameInfo["yard line"] + "\n"
                                   + getScoreboardString(message, difference, down, returnTeam, kickingUser))
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
                                   + getScoreboardString(message, difference, down, returnTeam, kickingUser))
        await updateLogFile(message, getLogFile(gameInfo["gist link"]), gameInfo, playType.upper(), "KICKOFF RETURN TD", "KICKOFF RETURN TD", result[1])
        updatePlayType(message.channel, "TOUCHDOWN")
    await messageUser(kickingUser, gameInfo)
    updateWaitingOnUser(str(kickingUser.name) + "#" + str(kickingUser.discriminator))



#########################
#       COIN TOSS       #
#########################

async def coinTossDecision(homeDiscordUser, awayDiscordUser, message, gameInfo):
    """
    Update the database and post the message for the coin toss winner's decision
    
    """

    # Message is not valid
    if message.content.lower() != "receive" and message.content.lower() != "defer":
        await message.channel.send("I did not understand your decision, please try again")
    # Handle receiving
    elif "receive" in message.content.lower().strip():
        await message.channel.send(message.author.mention + " chooses to receive. Waiting on a kickoff number from them")
        updateCoinTossDecision(message.channel, "receive")
        if str(message.author) == str(gameInfo["home user"]):
            updatePossession(message.channel, str(gameInfo["away name"]))
            await messageUser(homeDiscordUser, gameInfo)
            updateWaitingOnUser(str(homeDiscordUser.name) + "#" + str(homeDiscordUser.discriminator))
        else:
            updatePossession(message.channel, str(gameInfo["home name"]))
            await messageUser(awayDiscordUser, gameInfo)
            updateWaitingOnUser(str(awayDiscordUser.name) + "#" + str(awayDiscordUser.discriminator))
    # Handle a defer
    elif "defer" in message.content.lower().strip():
        await message.channel.send(message.author.mention + " chooses to defer to the second half. Waiting on a kickoff number from their opponent")
        updateCoinTossDecision(message.channel, "defer")
        if str(message.author) == str(gameInfo["home user"]):
            updatePossession(message.channel, str(gameInfo["home name"]))
            await messageUser(awayDiscordUser, gameInfo)
            updateWaitingOnUser(str(awayDiscordUser.name) + "#" + str(awayDiscordUser.discriminator))
        else:
            updatePossession(message.channel, str(gameInfo["away name"]))
            await messageUser(homeDiscordUser, gameInfo)
            updateWaitingOnUser(str(homeDiscordUser.name) + "#" + str(homeDiscordUser.discriminator))


async def coinToss(homeDiscordUser, awayDiscordUser, message, gameInfo):
    """
    Update the database and post the message for the coin toss result
    
    """

    result = random.randint(1, 2)
    if "head" in message.content.lower().strip():
        # Heads, away wins
        if result == 1:
            await message.channel.send("It is heads, " + awayDiscordUser.mention + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
            updateCoinTossWinner(message.channel, gameInfo["away user"])
        else:
            await message.channel.send("It is tails, " + homeDiscordUser.mention + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
            updateCoinTossWinner(message.channel, gameInfo["home user"])
    else:
        # Heads, home wins
        if result == 1:
            await message.channel.send("It is heads, " + homeDiscordUser.mention + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
            updateCoinTossWinner(message.channel, gameInfo["home user"])
        # Tails, away wins
        else:
            await message.channel.send("It is tails, " + awayDiscordUser.mention + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
            updateCoinTossWinner(message.channel, gameInfo["away user"])
    return "Invalid"