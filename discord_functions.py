import discord
from ranges_functions import getFinalResult
from util import *

"""
Handle the Discord side of the bot. Look for messages and post responses

@author: apkick
"""
 
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
            await message.channel.send("There was an issue with your command, please type '$result' and double check you entered the command correctly")
            return
    except:
        await message.channel.send("There was an issue with your command, please type '$result' and double check you entered the command correctly")
        return
    result = getFinalResult(offensivePlaybook, defensivePlaybook, playType, difference)
    if(str(result[0]) == "DID NOT FIND PLAY"):
        await message.channel.send("Could not find result, please type '$result' and double check you entered the command correctly")
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
        
        if(message.content == '$result'):
           await message.channel.send("The command format is: $result [OFFENSIVE PLAYBOOK], [DEFENSIVE PLAYBOOK], [PLAY TYPE], [OFFENSIVE NUMBER], [DEFENSIVE NUMBER]\n" 
                                      + "Offensive Playbook commands are: Flexbone, West Coast, Pro, Spread, Air Raid\n" 
                                      + "Defensive Playbook commands are: 3-4, 4-3, 4-4, 3-3-5, 5-2")
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