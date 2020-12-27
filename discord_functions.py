import discord
from user_database_functions import getUser
from user_database_functions import getNickname
from user_database_functions import getOffensivePlaybook
from user_database_functions import getDefensivePlaybook
from game_database_functions import addGameToDatabase
from ranges_functions import getFinalKickoffResult
from game_functions import game
from game_functions import gameDM
from util import calculateDifference
from util import representsInt
from util import getDiscordUser

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
Login to Discord and run the bot

"""
def loginDiscord():
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message):
        
        # Message is from the server
        if message.guild is not None:
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
                # The message is for a game, handle game logic
                await game(client, message)
                
                                                   
        # Message is from the DM for a game
        else:
            await gameDM(client, message)
            
    @client.event
    async def on_ready():
        print('------')
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    client.run(token)