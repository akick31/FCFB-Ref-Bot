import discord
import pandas as pd

ranges = pd.read_excel (r'C:\Users\Ron\Desktop\Product List.xlsx')

"""
Handle the Discord side of the bot. Look for messages and post responses

@author: apkick
"""
 

"""
Login to Discord and run the bot

"""
def loginDiscord(r):
    token = 'NzIzMzkwOTgxMTg5MjcxNjUz.Xuw85A.qVz7a8UlRDBxU5eb4oXFUb1ofr8'

    client = discord.Client()

    @client.event
    async def on_message(message):
        message.c
                
    @client.event
    async def on_ready():
        print('------')
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    client.run(token) 