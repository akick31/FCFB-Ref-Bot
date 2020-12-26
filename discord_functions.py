import discord
from ranges_functions import getFinalResult
from util import calculateDifference
from util import representsInt
from user_database_functions import getUser
from user_database_functions import getTeam


"""
Handle the Discord side of the bot. Look for messages and post responses

@author: apkick
"""

helpMessage = "There was an issue with your command, please type '$help' and double check you entered the command correctly"

async def createGame(message):
    if(message.content.startswith('$createGame') and message.author == ("pm_me_cute_sloths#5223")):
        command = message.content.split("$createGame")[1].strip()
    try:
        homeTeam = command.split("vs")[0].strip()
        awayTeam = command.split("vs")[0].strip()
        homeUser = getUser(homeTeam)
        awayUser = getUser(awayTeam)
        await message.guild.create_text_channel(homeTeam + " vs " + awayTeam, category = "Games")
    except:
        await message.channel.send(helpMessage)
        return
    
    
    
 
async def handleResultCommand(message):
    if(message.content.startswith('$result')):
        command = message.content.split("$result")[1].strip()
    try:
        offensivePlaybook = command.split(",")[0].strip()
        defensivePlaybook = command.split(",")[1].strip()
        playType = command.split(",")[2].strip()
        offensiveNumber = command.split(",")[3].strip()
        defensiveNumber = command.split(",")[4].strip()
        difference = calculateDifference(offensiveNumber, defensiveNumber)
        
        # Invalid difference
        if difference == -1:
            await message.channel.send(helpMessage)
            return
    except:
        await message.channel.send(helpMessage)
        return
    result = getFinalResult(offensivePlaybook, defensivePlaybook, playType, difference)
    if(str(result[0]) == "DID NOT FIND PLAY"):
        await message.channel.send(helpMessage)
    else:
        post = ("-------------------------------------------------------------------------\n" 
        + "Result for a " + playType + " with " + offensivePlaybook + " vs " + defensivePlaybook + " with a " + str(difference) + " difference\n"
        + "-------------------------------------------------------------------------\n\n")
        if(representsInt(result[0]) == True):
            post = post + str(int(result[0])) + " yard gain\n" + str(int(result[1])) + " seconds off the clock"
        else:
            post = post + result[0] + "\n" + str(int(result[1])) + " seconds off the clock"
        await message.channel.send(post)

"""
Login to Discord and run the bot

"""
def loginDiscord():
    token = 'NzIzMzkwOTgxMTg5MjcxNjUz.Xuw85A.qVz7a8UlRDBxU5eb4oXFUb1ofr8'

    client = discord.Client()

    @client.event
    async def on_message(message):
        
        if(message.content == '$help'):
           await message.channel.send("===================\nCOMMANDS\n===================\n" 
                                      + "$result\n"
                                      + "$createGame (only an admin may use this)\n"
                                      + "$createTeam (only an admin may use this)\n\n"
                                      + "===================\nPLAYBOOK FORMATTING\n===================\n"
                                      + "Offensive Playbook: Flexbone, West Coast, Pro, Spread, Air Raid\n" 
                                      + "Defensive Playbook: 3-4, 4-3, 4-4, 3-3-5, 5-2\n\n"
                                      + "===================\nCOMMAND FORMATTING\n===================\n"
                                      + "$result [OFFENSIVE PLAYBOOK], [DEFENSIVE PLAYBOOK], [PLAY TYPE], [OFFENSIVE NUMBER], [DEFENSIVE NUMBER]\n" 
                                      + "$createGame [HOME TEAM] vs [AWAY TEAM]\n" 
                                      + "$createTeam [TEAM NAME], [TEAM NICKNAME], [CONFERENCE], [DISCORD NAME], [COACH NAME], [OFFENSIVE PLAYBOOK], [DEFENSIVE PLAYBOOK]\n")
                                      
        if(message.content.startswith('$result')):
           await handleResultCommand(message)
                
    @client.event
    async def on_ready():
        print('------')
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    client.run(token) 