import discord
from ranges_functions import *
from util import *
from game_database_functions import *
from user_database_functions import *
from game_functions import *

"""
Handle the Discord side of the bot. Look for messages and post responses

@author: apkick
"""

helpMessage = "There was an issue with your command, please type '$help' and double check you entered the command correctly"
guildID = 723390838167699508
token = 'NzIzMzkwOTgxMTg5MjcxNjUz.Xuw8WQ.FUKbyJx2B5ylPBm2zpF0fBjPhlw'


"""
Check if user is a specific role

"""
def checkRole(user, roleName):
    for role in user.roles:
        if role.name == roleName:
            return True
    return False
    
"""
Make sure the team info is valid

"""
async def checkValidInfo(homeTeamInfo, awayTeamInfo, message):
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
    if (homeTeamInfo["offensive playbook"].strip() != "Flexbone" and 
    homeTeamInfo["offensive playbook"].strip()  != "West Coast" and 
    homeTeamInfo["offensive playbook"].strip()  != "Pro" and
    homeTeamInfo["offensive playbook"].strip()  != "Spread" and
    homeTeamInfo["offensive playbook"].strip()  != "Air Raid"):
        await message.channel.send("There was an issue with your database, the home offensive playbook is invalid")
        return False
    if (awayTeamInfo["offensive playbook"].strip()  != "Flexbone" and
    awayTeamInfo["offensive playbook"].strip()  != "West Coast" and 
    awayTeamInfo["offensive playbook"].strip()  != "Pro" and
    awayTeamInfo["offensive playbook"].strip()  != "Spread" and
    awayTeamInfo["offensive playbook"].strip()  != "Air Raid"):
        await message.channel.send("There was an issue with your database, the away offensive playbook is invalid")
        return False
    
    if (homeTeamInfo["defensive playbook"].strip()  != "3-4" and 
    homeTeamInfo["defensive playbook"].strip()  != "4-3" and 
    homeTeamInfo["defensive playbook"].strip()  != "4-4" and 
    homeTeamInfo["defensive playbook"].strip()  != "3-3-5" and
    homeTeamInfo["defensive playbook"].strip()  != "5-2"):
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
    
    
"""
Handle starting the games

"""
async def handleStartCommand(client, message, category):
    if(message.content.startswith('$start')):
        command = message.content.split('$start')[1].strip()
    try:
        # Get all the information necessary to start a game
        homeTeam = command.split("vs")[0].strip()
        awayTeam = command.split("vs")[1].strip()
        
        homeUser = getUser(homeTeam)
        awayUser = getUser(awayTeam)
        
        homeNickname = getNickname(homeTeam)
        awayNickname = getNickname(awayTeam)
       
        homeOffensivePlaybook = getOffensivePlaybook(homeTeam)
        homeDefensivePlaybook = getDefensivePlaybook(homeTeam)
        
        awayOffensivePlaybook = getOffensivePlaybook(awayTeam)
        awayDefensivePlaybook = getDefensivePlaybook(awayTeam)
        
        homeTeamInfo = {"name": homeTeam, "nickname": homeNickname, "user": homeUser, "offensive playbook": homeOffensivePlaybook, "defensive playbook": homeDefensivePlaybook}
        awayTeamInfo = {"name": awayTeam, "nickname": awayNickname, "user": awayUser, "offensive playbook": awayOffensivePlaybook, "defensive playbook": awayDefensivePlaybook}
        
        valid = await checkValidInfo(homeTeamInfo, awayTeamInfo, message)
        if valid == False:
            return
        
        # Create the game channel
        channel = await message.guild.create_text_channel(homeTeam + " vs " + awayTeam, category=category)
        
        # Add game to the databae
        addGameToDatabase(channel, homeTeamInfo, awayTeamInfo)
        
        homeDiscordUser = getDiscordUser(client, homeUser)
        awayDiscordUser = getDiscordUser(client, awayUser)
        
        await channel.send("Welcome to this week's FCFB matchup between " + homeTeam + " and " + awayTeam + "! If you ever see any typos or errors with the bot, please ping Dick\n\n"
                           + homeDiscordUser.mention + ", you're home, " + awayDiscordUser.mention + ", you're away. Call **heads** or **tails** in the air")
    except:
        await message.channel.send(helpMessage)
        return
 
"""
Handle the result command

"""
async def handleResultCommand(message):
    if(message.content.startswith('$result')):
        command = message.content.split("$result")[1].strip()
    try:
        playType = command.split(",")[0].strip()
        offensiveNumber = command.split(",")[1].strip()
        defensiveNumber = command.split(",")[2].strip()
        difference = calculateDifference(offensiveNumber, defensiveNumber)
        
        # Invalid difference
        if difference == -1:
            await message.channel.send("There was an issue calculating the difference, please contact Dick")
            return
    except:
        await message.channel.send(helpMessage)
        return
    result = getFinalKickoffResult(playType, difference)
    if(str(result[0]) == "DID NOT FIND PLAY"):
        await message.channel.send(helpMessage)
    else:
        post = ("-------------------------------------------------------------------------\n" 
        + "Result for a " + str(playType) + " with a " + str(difference) + " difference\n"
        + "-------------------------------------------------------------------------\n\n")
        if(representsInt(result[0]) == True):
            post = post + str(int(result[0]))
        else:
            post = post + str(result[0]) + "\n" + str(int(result[1])) + " seconds off the clock"
        await message.channel.send(post)

"""
Get the category

"""
def getCategory(client, categoryName):
    guild = client.get_guild(guildID)
    for serverCategory in guild.categories:
        if serverCategory.name == categoryName:
            category = serverCategory
            return category
    return "COULD NOT FIND"

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
Check if a string has a number, useful for determining if play call is valid

"""
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)
    

"""
Login to Discord and run the bot

"""
def loginDiscord():
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message):
        
        if(message.channel.category.name != "Games"):
            if(message.content == '$help'):
                await message.channel.send("===================\nCOMMANDS\n===================\n" 
                                          + "$result\n"
                                          + "$start (only an admin may use this)\n"
                                          + "$createTeam (only an admin may use this)\n\n"
                                          + "===================\nPLAYBOOK FORMATTING\n===================\n"
                                          + "Offensive Playbook: Flexbone, West Coast, Pro, Spread, Air Raid\n" 
                                          + "Defensive Playbook: 3-4, 4-3, 4-4, 3-3-5, 5-2\n\n"
                                          + "===================\nCOMMAND FORMATTING\n===================\n"
                                          + "$result [PLAY TYPE], [OFFENSIVE NUMBER], [DEFENSIVE NUMBER]\n" 
                                          + "$start [HOME TEAM] vs [AWAY TEAM]\n" 
                                          + "$createTeam [TEAM NAME], [TEAM NICKNAME], [CONFERENCE], [DISCORD NAME], [COACH NAME], [OFFENSIVE PLAYBOOK], [DEFENSIVE PLAYBOOK]\n")
                                          
            elif(message.content.startswith('$result')):
                await handleResultCommand(message)
               
            elif(message.content.startswith('$start')):
                if checkRole(message.author, "FCFB Test Admin") == False:
                    await message.channel.send("You do not have permission to use this command")
                    
                category = getCategory(client, "Games")
                if category == "COULD NOT FIND":
                    await message.channel.send(helpMessage)
                else:
                    await handleStartCommand(client, message, category)
               
            elif(message.content.startswith('$')):
                await message.channel.send(helpMessage)
            
        else:
            # Get the game info for the channel
            gameInfo = getGameInfo(message.channel)
            homeDiscordUser = getDiscordUser(client, gameInfo["home user"])
            awayDiscordUser = getDiscordUser(client, gameInfo["away user"])
            
            
            # Handle coin toss winner
            if (str(message.author) == str(gameInfo["away user"]) and ('head' in message.content or 'tail' in message.content) and gameInfo["coin toss winner"] == "NONE"):
                result = coinToss(gameInfo["home user"], gameInfo["away user"], message)
                if result == "heads, home wins":
                    await message.channel.send("It is heads, " + homeDiscordUser.mention + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
                    updateCoinTossWinner(message.channel, gameInfo["home user"])
                if result == "tails, home wins":
                    await message.channel.send("It is tails, " + homeDiscordUser.mention  + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
                    updateCoinTossWinner(message.channel, gameInfo["home user"])
                if result == "heads, away wins":
                    await message.channel.send("It is heads, " + awayDiscordUser.mention  + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
                    updateCoinTossWinner(message.channel, gameInfo["away user"])
                if result == "tails, away wins":
                    await message.channel.send("It is tails, " + awayDiscordUser.mention  + " you have won the toss. Do you wish to **receive** or **defer** to the second half?")
                    updateCoinTossWinner(message.channel, gameInfo["away user"])
            
            # Handle coin toss decision
            if (str(message.author) == str(gameInfo["coin toss winner"]) and ('receive' in message.content or 'defer' in message.content) and gameInfo["coin toss decision"] == "NONE"):
                if (message.content.lower() != "receive" and message.content.lower() != "defer"):
                    await message.channel.send("I did not understand your decision, please try again")
                elif "receive" in message.content.lower().strip():
                    await message.channel.send(message.author.mention + " chooses to receive. Waiting on a kickoff number from them")
                    updateCoinTossDecision(message.channel, "receive")
                    if (str(message.author) == str(gameInfo["home user"])):
                        updatePossession(message.channel, str(gameInfo["away team"]))
                    else: 
                        updatePossession(message.channel, str(gameInfo["home team"]))
                elif "defer" in message.content.lower().strip():
                    await message.channel.send(message.author.mention + " chooses to defer to the second half. Waiting on a kickoff number from their opponent")
                    updateCoinTossDecision(message.channel, "defer")  
                    if (str(message.author) == str(gameInfo["home user"])):
                        updatePossession(message.channel, str(gameInfo["home team"]))
                    else:
                        updatePossession(message.channel, str(gameInfo["away team"]))
            
            # Handle kickoffs after player has been DMed
            if (gameInfo["play type"] == "KICKOFF" and ((str(message.author) == str(gameInfo["home user"]) and gameInfo["possession"] == gameInfo["home team"] and gameInfo["waiting on"] == gameInfo["home team"]) 
                or (str(message.author) == str(gameInfo["away user"]) and gameInfo["possession"] == gameInfo["away team"] and gameInfo["waiting on"] == gameInfo["away team"]))):
                if "normal" not in message.content.lower() or "squib" not in message.content.lower() or "onside" not in message.content.lower():
                    await message.channel.send("I could not find a play in your message, please try again and submit **normal**, **squib**, or **onside**")
                elif hasNumbers(message.content) == False:
                    await message.channel.send("I could not find a number in your message, please try again and submit a number between 1-1500")
                elif len(list(map(int, re.findall(r'\d+', message.content)))) > 1:
                    await message.channel.send("I found multiple numbers in your message, please try again and submit a number between 1-1500")
                else:
                    numList = list(map(int, re.findall(r'\d+', message.content)))
                    number = numList[0]
                    if number < 1 or number > 1500:
                         await message.channel.send("Your number is not valid, please try again and submit a number between 1-1500")
                    else:
                        offensiveNumber = number
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
                            result = getKickoffResult(playType, difference)
            
            
                
    @client.event
    async def on_ready():
        print('------')
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    client.run(token) 