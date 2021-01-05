## **FakeCFB RefBot for Discord**

### **What is RefBot?**

This code is for the Discord version of the RefBot that
/r/FakeCollegeFootball uses. The purpose of the bot is 
to mediate a game between two individuals where they guess
their opponents number and the difference determines the result
of the play as if it were a college football game.

The discord channel for this bot is: https://discord.gg/8arTq8F

### **How do I use RefBot in my server?**

1. Fork this code and clear out all of the data in the Excel
   spreadsheets except for the ranges.xlsx spreadsheet. The
   code currently uses these to store data
    
2. Configure a config.json file, it should be in the following style:

`{"discordToken": "[INSERT TOKEN]",
 "githubToken": "[INSERT TOKEN]",
"guildID": [INSERT ID],
"logRepository": "[INSERT PATH]"}`

3. To get the Discord Token, go to https://discord.com/developers/applications
and create a bot. Name it and choose whatever name you desire. Under bot, generate
   a token and copy it into the quotations WITHOUT the brackets. 
   
4. Scroll down and give the bot admin permissions

5. Navigate to the oath2 tab and select the bot box in Scopes and copy and paste the 
URL it generates into a new window. Add the bot to your sever
   
6. In your server, create a category named "Scrimmages" and in that category a channel
named "game-logs"
   
7. Go into your profile settings on Discord and go to appearance
and at the bottom select "Developer Mode" and turn it on
   
8. Right click on your server icon and select "Copy ID", paste this
into the guildID bracket in the config file. There should be no quotations or brackets
   
9. Navigate to github.com and create a Github account and then create a repository. 
   named mine FCFB-Score-Logs. Whatever you name it, take your GitHub Username
   + your repository name and copy and paste that into the logRepository section
    of the config file. For example, for me it was "akick31/FCFB-Score-Logs"

10. In Github, go to your profile settings->Developer settings->OAuth Apps->
    Generate your token
    
11. Once everything is all set up, run "python3 FCFBRefBot.py". Do not post your config
file anywhere otherwise Github and Discord will reset your token. 
    
### **Final Notes**
- Please submit an issue if you run into one. 
- This bot and the subreddit and Discord associated with it are not
associated with the real college football sport in any way
- Please visit the Discord link and ask for help if you need help with the bot
- You do need some sort of server to run the code 24/7

This bot was written by and is maintained by Andrew Kicklighter