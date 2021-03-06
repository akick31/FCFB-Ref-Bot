import discord
import json
from user_database_functions import getUser
from user_database_functions import getNickname
from user_database_functions import getOffensivePlaybook
from user_database_functions import getDefensivePlaybook
from game_database_functions import addGameToDatabase
from game_database_functions import copyGameData
from game_database_functions import pasteGameData
from game_database_functions import deleteGameData
from game_database_functions import getGameInfo
from game_database_functions import checkUserFree
from game_database_functions import updateEmbeddedMessage
from game_database_functions import getGameInfoTeam
from github_functions import getLogFileURL
from github_functions import getLogFile
from github_functions import createLogFile
from github_functions import deleteLogFile
from user_database_functions import checkName
from user_database_functions import checkUser
from user_database_functions import addUser
from user_database_functions import deleteTeam
from user_database_functions import getTeamInformation
from game_functions import game
from game_functions import gameDM
from util import getDiscordUser
from util import convertDown


"""
Handle the Discord side of the bot. Look for messages and post responses

@author: apkick
"""

helpMessage = "There was an issue with your command, please type '&help' and double check you entered the command correctly"
with open('config.json') as f:
    data = json.load(f)
jsonData = json.dumps(data)
token = json.loads(jsonData)["discordToken"]
guildID = json.loads(jsonData)["guildID"]
commandMessage = ("===================\nCOMMANDS\n===================\n" 
                + "&start - starts games\n"
                + "&end - ends games and saves them\n" 
                + "&delete - deletes games and does not save them\n" 
                + "&create - creates teams\n" 
                + "&remove - removes teams\n"
                + "&view - view user information\n"
                + "&database - view the game database information\n"
                + "===================\nPLAYBOOK FORMATTING\n===================\n"
                + "Offensive Playbook: Flexbone, West Coast, Pro, Spread, Air Raid\n" 
                + "Defensive Playbook: 3-4, 4-3, 4-4, 3-3-5, 5-2\n\n"
                + "===================\nCOMMAND FORMATTING\n===================\n"
                + "&start [HOME TEAM] vs [AWAY TEAM]\n" 
                + "&end [HOME TEAM] vs [AWAY TEAM]\n" 
                + "&delete [HOME TEAM] vs [AWAY TEAM]\n" 
                + "&create [TEAM NAME], [TEAM NICKNAME], [CONFERENCE], [DISCORD NAME (WITH THE # TAG AS WELL)], [COACH NAME], [OFFENSIVE PLAYBOOK], [DEFENSIVE PLAYBOOK]\n"
                + "&remove [TEAM NAME]\n"
                + "&view [TEAM NAME]\n"
                + "&database (In the game channel) OR &database [HOME TEAM] vs [AWAY TEAM]")


async def createEmbed(client, gameChannel, homeTeam, awayTeam, url):
    """
    Create a Discord embed

    """
    embed = discord.Embed(title=homeTeam + " vs " + awayTeam, description="FCFB Game", url=url, color=0x28db18)
    embed.add_field(name="Home Team", value=homeTeam, inline=True)
    embed.add_field(name="Away Team", value=awayTeam, inline=True)
    embed.add_field(name="Score", value="0-0 Tied", inline=False)
    embed.add_field(name="Clock", value="7:00 left in Q1", inline=False)
    embed.add_field(name="Possession", value=":football: N/A", inline=True)
    embed.add_field(name="Yard Line", value=homeTeam + " 35", inline=True)
    embed.add_field(name="Down", value="1st and 10", inline=True)
    
    guild = client.get_guild(guildID)
    gameLogChannel = None
    for channel in guild.channels:
        if channel.name == "game-logs":
            gameLogChannel = channel
            break
    
    messagePosted = await gameLogChannel.send(embed=embed)
    updateEmbeddedMessage(gameChannel, messagePosted.id)
    
async def editEmbed(client, gameInfo, url):
    embed = discord.Embed(title=gameInfo["home name"] + " vs " + gameInfo["away name"], description="FCFB Game", url=url, color=0x28db18)
    embed.add_field(name="Home Team", value=gameInfo["home name"] + " " + gameInfo["home nickname"], inline=True)
    embed.add_field(name="Away Team", value=gameInfo["away name"] + " " + gameInfo["away nickname"], inline=True)
    homeScore = gameInfo["home score"]
    awayScore = gameInfo["away score"]
    if int(homeScore) > int(awayScore):
        score = str(homeScore) + "-" + str(awayScore) + " " + gameInfo["home name"] + " leads"
    elif int(homeScore) < int(awayScore):
        score = str(homeScore) + "-" + str(awayScore) + " " + gameInfo["away name"] + " leads"
    else:
        score = str(homeScore) + "-" + str(awayScore) + " Tied"
    embed.add_field(name="Score", value=score, inline=False)
    embed.add_field(name="Clock", value=str(gameInfo["time"]) + " left in Q" + str(gameInfo["quarter"]), inline=False)
    embed.add_field(name="Possession", value=":football: " + gameInfo["possession"], inline=True)
    embed.add_field(name="Yard Line", value=gameInfo["yard line"], inline=True)
    down = convertDown(str(gameInfo["down"]))
    embed.add_field(name="Down", value=down + " and " + str(gameInfo["distance"]), inline=True)
    
    guild = client.get_guild(guildID)
    gameLogChannel = None
    for channel in guild.channels:
        if channel.name == "game-logs":
            gameLogChannel = channel
            break
        
    try:
        oldEmbed = await gameLogChannel.fetch_message(gameInfo["embedded message"])
        await oldEmbed.edit(embed=embed)
    except:
        print("Could not edit game log, likely because the game log for this game doesn't exist anymore. Error due to " + str(Exception))
        raise Exception
    
    

def checkRole(user, roleName):
    """
    Check if user is a specific role
    
    """

    for role in user.roles:
        if role.name == roleName:
            return True
    return False
    

async def checkValidInfo(homeTeamInfo, awayTeamInfo, message):
    """
    Make sure the team info in the database is valid
    
    """

    if homeTeamInfo["user"] == "COULD NOT FIND":
        await message.channel.send("There was an issue with your database, I could not find the home user")
        return False
    if awayTeamInfo["user"] == "COULD NOT FIND":
        await message.channel.send("There was an issue with your database, I could not find the away user")
        return False
    if homeTeamInfo["nickname"] == "COULD NOT FIND":
        await message.channel.send("There was an issue with your database, I could not find the home team")
        return False
    if awayTeamInfo["nickname"] == "COULD NOT FIND":
        await message.channel.send("There was an issue with your database, I could not find the away team")
        return False
    if homeTeamInfo["offensive playbook"] == "COULD NOT FIND":
        await message.channel.send("There was an issue with your database, I could not find the home offensive playbook")
        return False
    if awayTeamInfo["offensive playbook"] == "COULD NOT FIND":
        await message.channel.send("There was an issue with your database, I could not find the away offensive playbook")
        return False
    if homeTeamInfo["defensive playbook"] == "COULD NOT FIND":
        await message.channel.send("There was an issue with your database, I could not find the home defensive playbook")
        return False
    if awayTeamInfo["defensive playbook"] == "COULD NOT FIND":
        await message.channel.send("There was an issue with your database, I could not find the away defensive playbook")
        return False

    # Check playbook validity
    if (homeTeamInfo["offensive playbook"].strip().lower() != "flexbone" and
    homeTeamInfo["offensive playbook"].strip().lower() != "west coast" and
    homeTeamInfo["offensive playbook"].strip().lower() != "pro" and
    homeTeamInfo["offensive playbook"].strip().lower() != "spread" and
    homeTeamInfo["offensive playbook"].strip().lower() != "air raid"):
        await message.channel.send("There was an issue with your database, the home offensive playbook is invalid")
        return False
    if (awayTeamInfo["offensive playbook"].strip().lower() != "flexbone" and
    awayTeamInfo["offensive playbook"].strip().lower() != "west coast" and
    awayTeamInfo["offensive playbook"].strip().lower() != "pro" and
    awayTeamInfo["offensive playbook"].strip().lower() != "spread" and
    awayTeamInfo["offensive playbook"].strip().lower() != "air raid"):
        await message.channel.send("There was an issue with your database, the away offensive playbook is invalid")
        return False

    if (homeTeamInfo["defensive playbook"].strip() != "3-4" and
    homeTeamInfo["defensive playbook"].strip() != "4-3" and
    homeTeamInfo["defensive playbook"].strip() != "4-4" and
    homeTeamInfo["defensive playbook"].strip() != "3-3-5" and
    homeTeamInfo["defensive playbook"].strip() != "5-2"):
        await message.channel.send("There was an issue with your database, the home defensive playbook is invalid")
        return False

    if (awayTeamInfo["defensive playbook"] != "3-4" and
    awayTeamInfo["defensive playbook"] != "4-3" and
    awayTeamInfo["defensive playbook"] != "4-4" and
    awayTeamInfo["defensive playbook"] != "3-3-5" and
    awayTeamInfo["defensive playbook"] != "5-2"):
        await message.channel.send("There was an issue with your database, the away defensive playbook is invalid")
        return False

    return True


async def handleStartCommand(client, message, category):
    """
    Handle starting the games
    
    """

    if message.content.startswith('&start'):
        command = message.content.split('&start')[1].strip()
        try:
            # Get all the information necessary to start a game
            homeTeam = command.split("vs")[0].strip()
            awayTeam = command.split("vs")[1].strip()

            homeUser = getUser(homeTeam)
            awayUser = getUser(awayTeam)

            homeDiscordUser = getDiscordUser(client, homeUser)
            awayDiscordUser = getDiscordUser(client, awayUser)


            # Verify the users aren't already in a game
            homeUserFree = checkUserFree(homeUser)
            awayUserFree = checkUserFree(awayUser)


            # Home user is already playing
            if not homeUserFree:
                await message.channel.send(homeDiscordUser.mention + " is already playing in a game! I cannot schedule them for a second game at this time")
                return
            elif not awayUserFree:
                await message.channel.send(awayDiscordUser.mention + " is already playing in a game! I cannot schedule them for a second game at this time")
                return

            homeNickname = getNickname(homeTeam)
            awayNickname = getNickname(awayTeam)

            homeOffensivePlaybook = getOffensivePlaybook(homeTeam)
            homeDefensivePlaybook = getDefensivePlaybook(homeTeam)

            awayOffensivePlaybook = getOffensivePlaybook(awayTeam)
            awayDefensivePlaybook = getDefensivePlaybook(awayTeam)

            homeTeamInfo = {"name": homeTeam, "nickname": homeNickname, "user": homeUser, "offensive playbook": homeOffensivePlaybook, "defensive playbook": homeDefensivePlaybook}
            awayTeamInfo = {"name": awayTeam, "nickname": awayNickname, "user": awayUser, "offensive playbook": awayOffensivePlaybook, "defensive playbook": awayDefensivePlaybook}

            valid = await checkValidInfo(homeTeamInfo, awayTeamInfo, message)
            if valid is False:
                await message.channel.send("There was an issue starting your game due to invalid team info")
                return

            # Create the game channel
            channel = await message.guild.create_text_channel(homeTeam + " vs " + awayTeam, category=category)

            # Add game to the database
            addGameToDatabase(channel, homeTeamInfo, awayTeamInfo)

            homeDiscordUser = getDiscordUser(client, homeUser)
            awayDiscordUser = getDiscordUser(client, awayUser)

            if homeDiscordUser == "COULD NOT FIND":
                await message.channel.send("Could not find the discord user " + homeUser + ". Please verify it is correct.")
            elif awayDiscordUser == "COULD NOT FIND":
                await message.channel.send("Could not find the discord user " + awayUser + ". Please verify it is correct.")

            await createLogFile(channel, homeTeam, awayTeam)

            gameInfo = getGameInfo(channel)
            gistLink = getLogFileURL(gameInfo["gist link"])

            await createEmbed(client, channel, homeTeam, awayTeam, gistLink)

            await channel.send("Welcome to this week's FCFB matchup between " + homeTeam + " and " + awayTeam + "! If you ever see any typos or errors with the bot, please ping Dick\n\n"
                               + homeDiscordUser.mention + ", you're home, " + awayDiscordUser.mention + ", you're away. " + awayDiscordUser.mention + " please call **heads** or **tails** in the air")
            await message.channel.send(homeTeam + " vs " + awayTeam + " was successfully started")
            print(channel.name + " was successfully started")
        except:
            await message.channel.send("There was an issue starting the game, please ensure you used the right command by using '&help' and then contact Dick")
            print("There was an issue starting " + message.content.split('&start')[1].strip() + " due to " + str(Exception))
            raise Exception
    else:
        return
    

async def handleEndCommand(message):
    """
    Handle ending the games
    
    """    

    if message.content.startswith('&end'):
        command = message.content.split('&end')[1].strip()
        try:
            # Get all the information necessary to end a game
            homeTeam = command.split("vs")[0].strip()
            awayTeam = command.split("vs")[1].strip()

            gameChannel = None
            name = homeTeam.lower() + " vs " + awayTeam.lower()
            channelName = name.replace(" ", "-")
            if "&" in channelName:
                channelName = channelName.replace("&", "")
            for channel in message.guild.channels:
                if channel.name == channelName:
                    gameChannel = channel
                    break

            # Ensure you can only delete in the game channel
            if gameChannel == message.channel:
                data = copyGameData(message.channel)
                if data == "NO GAME FOUND":
                    await message.channel.send("No game data was found and thus I cannot save this game. Deleting the channel.")
                    await gameChannel.delete()
                    print(gameChannel.name + " could not find game data and could not save, but was successfully deleted")
                    return
                else:
                    pasteGameData(data)
                    deleteGameData(message.channel)
                    await gameChannel.delete()
                    print(gameChannel.name + " was successfully saved and ended")
                    return
            else:
                await message.channel.send("You cannot delete a game here, you must be in the specific game channel")
                return
        except:
            await message.channel.send("There was an issue ending the game, please ensure you used the right command by using '&help' and then contact Dick")
            print("There was an issue ending " + message.channel.name + " due to " + str(Exception))
            raise Exception
    else:
        return
    
async def handleDeleteCommand(client, message):
    """
    Handle deleting the games
    
    """

    if message.content.startswith('&delete'):
        command = message.content.split('&delete')[1].strip()
        try:
            # Get all the information necessary to delete a game
            homeTeam = command.split("vs")[0].strip()
            awayTeam = command.split("vs")[1].strip()

            gameChannel = None
            name = homeTeam.lower() + " vs " + awayTeam.lower()
            channelName = name.replace(" ", "-")
            if "&" in channelName:
                channelName = channelName.replace("&", "")
            for channel in message.guild.channels:
                if channel.name == channelName:
                    gameChannel = channel
                    break

            # Ensure you can only delete in the game channel
            if gameChannel.name == message.channel.name:
                gameInfo = getGameInfo(message.channel)

                guild = client.get_guild(guildID)
                gameLogChannel = None
                for channel in guild.channels:
                    if channel.name == "game-logs":
                        gameLogChannel = channel
                        break
                if gameInfo["embedded message"] is not None and gameInfo["embedded message"] != "":
                    embedMessage = await gameLogChannel.fetch_message(gameInfo["embedded message"])
                    await embedMessage.delete()

                deleteGameData(message.channel)
                deleteLogFile(gameInfo["gist link"])
                await gameChannel.delete()
                print(gameChannel.name + " was successfully deleted")
                return
            else:
                await message.channel.send("You cannot delete a game here, you must be in the specific game channel")
                return
        except:
            await message.channel.send("There was an issue deleting the game, please ensure you used the right command by using '&help' and then contact Dick")
            print("There was an issue deleting " + message.channel.name + "due to " + str(Exception))
            raise Exception
    else:
        return
    
    
async def handleCreateCommand(message):
    """
    Handle creating teams
    
    """

    if message.content.startswith('&create'):
        command = message.content.split('&create')[1].strip()
        teamInformation = command.split(',')
        try:
            teamInfo = []
            if len(teamInformation) != 7:
                await message.channel.send("You do not have all of the correct information, please use '&help' to check what is needed")
                return

            # Handle the team name
            teamName = teamInformation[0].strip()
            # Verify the team name isn't already in a game
            teamUsed = checkName(teamName)
            if teamUsed:
                await message.channel.send("The team name, " + teamName + ", is already used. Please try another name")
                return
            teamInfo.append(teamName)

            # Handle the team nickname
            teamNickname = teamInformation[1].strip()
            teamInfo.append(teamNickname)

            # Handle the team conference
            teamConference = teamInformation[2].strip()
            teamInfo.append(teamConference)

            # Handle the team coach's discord
            teamUser = teamInformation[3].strip()
            # Verify the users aren't already in a game
            userUsed = checkUser(teamUser)
            if userUsed:
                await message.channel.send("The user, " + teamUser + ", already has a team, if you want to make changes please contact Dick")
                return
            if "#" not in teamUser:
                await message.channel.send("The user must include the tag. If you click on your profile, you'll see your discord name "
                                           + " and '#' and a number, please include the '#' and number. For example, #5233")
                return
            if "@" in teamUser:
                await message.channel.send("The user cannot include your '@', it should be something like myname#6969, not @myname")
                return
            teamInfo.append(teamUser)

            # Handle the team coach's name
            teamCoach = teamInformation[4].strip()
            teamInfo.append(teamCoach)

            # Handle the offensive playbook
            teamOffensivePlaybook = teamInformation[5].strip().lower()
            if (teamOffensivePlaybook != "flexbone" and teamOffensivePlaybook != "west coast"
            and teamOffensivePlaybook != "pro" and teamOffensivePlaybook != "spread"
            and teamOffensivePlaybook != "air raid"):
                await message.channel.send("The offensive playbook is not valid, please check what was entered and verify it matches one of the following:\n "
                                           + "Flexbone, West Coast, Pro, Spread, Air Raid\n")
                return
            teamInfo.append(teamOffensivePlaybook)

            # Handle the defensive playbook
            teamDefensivePlaybook = teamInformation[6].strip().lower()
            if (teamDefensivePlaybook != "5-2" and teamDefensivePlaybook != "4-4"
            and teamDefensivePlaybook != "4-3" and teamDefensivePlaybook != "3-4"
            and teamDefensivePlaybook != "3-3-5"):
                await message.channel.send("The defensive playbook is not valid, please check what was entered and verify it matches one of the following:\n "
                                           + "3-4, 4-3, 4-4, 3-3-5, 5-2\n")
                return
            teamInfo.append(teamDefensivePlaybook)

            addUser(teamInfo)

            await message.channel.send(str(teamName) + " was successfully created")
            print(teamName + " was successfully created")

        except:
            await message.channel.send("There was an issue creating the team, please ensure you used the right command by using '&help' and then contact Dick")
            print("There was an issue creating the team made by " + message.author.name + " due to " + str(Exception))
            raise Exception
    else:
        return
    
    
async def handleRemoveCommand(message):
    """
    Handle deleting a team
    
    """

    if message.content.startswith('&remove'):
        command = message.content.split('&remove')[1].strip()
        try:
            teamName = command
            # Verify the team actually exists
            teamExists = checkName(teamName)

            if teamExists:
                deleteTeam(teamName)
                await message.channel.send(teamName + " was deleted successfully")
                print(teamName + " was successfully deleted")
                return
            else:
                await message.channel.send("There was an issue deleting " + teamName + ", verify the team name is correct")
                print("There was an issue deleting " + teamName)
                return
        except Exception:
            await message.channel.send("There was an issue deleting the team, please ensure you used the right command by using '&help' and then contact Dick")
            print("There was an issue deleting " + message.content.split('&remove')[1].strip() + "due to " + str(Exception))
            raise Exception
    else:
        return
    

async def handleViewCommand(message):
    """
    Handle deleting a team
    
    """

    if message.content.startswith('&view'):
        command = message.content.split('&view')[1].strip()
        try:
            teamName = command
            # Verify the team actually exists
            teamExists = checkName(teamName)

            if teamExists:
                teamInfo = getTeamInformation(teamName)
                await message.channel.send("**" + teamName + " Information:** " + str(teamInfo))
                print(teamName + " information was successfully gathered")
                return
            else:
                await message.channel.send("There was an issue getting " + teamName + " information, verify the team name is correct")
                print("There was an issue getting information for " + teamName)
                return
        except:
            await message.channel.send("There was an issue getting the team information, please ensure you used the right command by using '&help' and then contact Dick")
            print("There was an issue getting information for " + message.content.split('&view')[1].strip() + " due to " + str(Exception))
            raise Exception
    else:
        return


async def handleDatabaseCommand(client, message):
    """
    Handle the database command, which displays the information for the game

    """

    if message.content.startswith('&database'):
        try:
            post = ''
            if "vs" in message.content:
                command = message.content.split('&database')[1].strip()
                # Get all the information necessary to start a game
                homeTeam = command.split("vs")[0].strip()
                awayTeam = command.split("vs")[1].strip()
                gameInfo = getGameInfoTeam(homeTeam)
            else:
                gameInfo = getGameInfo(message.channel)
                if gameInfo is None:
                    await message.channel.send("There was an issue getting game information. " +
                                               "Are you in the game channel? If you are not in a " +
                                               "game channel you must use [HOME TEAM] vs [AWAY TEAM] in your command")
                    return

            post = ("**" + gameInfo["home name"] + " vs " + gameInfo["away name"] + "**\n\n"
                    + "Home User: " + gameInfo["home user"] + "\n"
                    + "Away User: " + gameInfo["away user"] + "\n"
                    + "Home Offensive Playbook: " + gameInfo["home offensive playbook"] + "\n"
                    + "Away Offensive Playbook: " + gameInfo["away offensive playbook"] + "\n"
                    + "Home Defensive Playbook: " + gameInfo["home defensive playbook"] + "\n"
                    + "Away Offensive Playbook: " + gameInfo["away defensive playbook"] + "\n"
                    + "Home Offensive Playbook: " + gameInfo["home offensive playbook"] + "\n"
                    + "Coin Toss Winner: " + gameInfo["coin toss winner"] + "\n"
                    + "Coin Toss Decision: " + gameInfo["coin toss decision"] + "\n"
                    + "Quarter: " + str(gameInfo["quarter"]) + "\n"
                    + "Time: " + gameInfo["time"] + "\n"
                    + "Yard Line: " + gameInfo["yard line"] + "\n"
                    + "Possession: " + gameInfo["possession"] + "\n"
                    + "Waiting On: " + gameInfo["waiting on"] + "\n"
                    + "Next Play Type: " + gameInfo["play type"] + "\n"
                    + "Game Status: " + gameInfo["game status"] + "\n"
                    + "Clock Stopped: " + gameInfo["clock stopped"] + "\n"
                    + "Coin Toss Decision: " + gameInfo["coin toss decision"] + "\n"
                    + "Number Submitted: " + gameInfo["number submitted"] + "\n"
                    + "Halftime: " + gameInfo["halftime"] + "\n")
            await message.channel.send(post)
        except:
            await message.channel.send("There was an issue getting the game information, please ensure you used the right command by using '&help' and then contact Dick")
            print("There was an issue getting information for " + message.content.split('&database')[1].strip() + " due to " + str(Exception))
            raise Exception




def getCategory(client, categoryName):
    """
    Get the category Discord object and return it based on the name you're looking for
    
    """

    guild = client.get_guild(guildID)
    for serverCategory in guild.categories:
        if serverCategory.name == categoryName:
            category = serverCategory
            return category
    return "COULD NOT FIND"


def loginDiscord():
    """
    Login to Discord and run the bot
    
    """

    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message):
        
        # Message is from the server
        if message.guild is not None:
            if message.channel.category.name != "Scrimmages" or message.channel.name == "bot-game-chat":
                if message.content == '&help':
                    await message.channel.send(commandMessage)
                   
                elif message.content.startswith('&start'):
                    category = getCategory(client, "Scrimmages")
                    if category == "COULD NOT FIND":
                        await message.channel.send(helpMessage)
                    else:
                        await handleStartCommand(client, message, category)
                        
                elif message.content.startswith('&end'):
                    await message.channel.send("You cannot end a game here, you must be in the specific game channel")
                
                elif message.content.startswith('&delete'):
                    await message.channel.send("You cannot delete a game here, you must be in the specific game channel")
                    
                elif message.content.startswith('&create'):
                    await handleCreateCommand(message)
                
                elif message.content.startswith('&remove'):
                    await handleRemoveCommand(message)
                
                elif message.content.startswith('&view'):
                    await handleViewCommand(message)

                elif message.content.startswith('&database'):
                    await handleDatabaseCommand(client, message)
                   
                elif message.content.startswith('&'):
                    await message.channel.send(helpMessage)
                
            else:
                gameInfo = getGameInfo(message.channel)
                
                if message.content == '&help':
                    await message.channel.send(commandMessage)
                    
                elif message.content.startswith('&end'):
                    category = getCategory(client, "Scrimmages")
                    if category == "COULD NOT FIND":
                        await message.channel.send(helpMessage)
                    else:
                        await handleEndCommand(message)

                elif message.content.startswith('&database'):
                    await handleDatabaseCommand(client, message)
                        
                elif message.content.startswith('&delete'):
                    category = getCategory(client, "Scrimmages")
                    if category == "COULD NOT FIND":
                        await message.channel.send(helpMessage)
                    else:
                        await handleDeleteCommand(client, message)
    
                # Game is invalid
                elif gameInfo["home user"] is None or gameInfo["away user"] is None or gameInfo["home user"] == "" or gameInfo["away user"] == "":
                    if str(message.author) != "FCFB Ref Bot#3976" and message.channel.name != "bot-game-chat":
                        await message.channel.send("No game appears to be found, but a channel for the game exists, please contact Dick.")
                elif gameInfo["number submitted"] == "YES":
                    await game(client, message)
                    gameInfo = getGameInfo(message.channel)
                    if gameInfo["gist link"] is not None and gameInfo["gist link"] != "":
                        gistLink = getLogFileURL(gameInfo["gist link"])
                        await editEmbed(client, gameInfo, gistLink)
                            
                    
                
                
                                                   
        # Message is from the DM for a game
        else:
            await gameDM(client, message)
            
    @client.event
    async def on_ready():
        print('------')
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print("v1.1.0")
        print('------')

    client.run(token)