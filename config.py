# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import json
import random
import asyncio
import os

from datetime import datetime
from datetime import timedelta
from os import listdir
from os.path import isfile, join

import kt_config
import pr_config

## File Paths
botFile = 'kelutral-bot/cogs/shared/files/users/bot.json'
directoryFile = 'kelutral-bot/cogs/shared/files/users/new-directory.json'
configFile = 'kelutral-bot/files/config/config.json'
tokenFile = 'kelutral-bot/files/config/token.txt'

# Reloads the directory when it is edited
def reloadDir():
    with open(directoryFile, 'r', encoding='utf-8') as fh:
        directory = json.load(fh)
    return directory
    
def log(to_log):
    today = datetime.strftime(datetime.now(), '%m-%d-%Y')
    now = datetime.now().strftime('%H:%M')
    try:
        with open(f'kelutral-bot/files/logs/{today}.log', 'r') as fh:
            content = fh.read()
        with open(f'kelutral-bot/files/logs/{today}.log', 'w') as fh:
            fh.write(f"{content}\n{now} -- {to_log}")
        print(f"{now} -- {to_log}")
    except FileNotFoundError:
        with open(f'kelutral-bot/files/logs/{today}.log', 'w+') as fh:
            fh.write(f"{now} -- {to_log}")
        print(f"{now} -- {to_log}")

## File Initialization
# Retrieves bot token
with open(tokenFile,'r') as fh:
    token = fh.read()

# Retrieves config file
with open(configFile, 'r') as fh:
    config = json.load(fh)

# Retrieves help command file
with open('kelutral-bot/files/config/help.json', 'r', encoding='utf-8') as fh:
    helpFile = json.load(fh)

# Retrieves English / Na'vi output master file
with open('kelutral-bot/files/config/text_file.json', 'r', encoding='utf-8') as fh:
    text_file = json.load(fh)

# Retrieves FAQ
with open('kelutral-bot/files/config/faq.json', 'r', encoding='utf-8') as fh:
    faq = json.load(fh)
    
with open(kt_config.dictionaryFile, 'r', encoding='utf-8') as fh:
    dictionary = json.load(fh)
    
# Global Config Variables
token = token.strip()
prefix = config['prefix']
version = config['version']
send_time = config['send_time']
sequelDate = config['sequel_date']
watched_phrases = config['keywords']
blacklist = config['blacklist']
debug = False
watch_keywords = False

## Shared Roles
modRoles = [kt_config.adminID,kt_config.modID,pr_config.adminID,pr_config.modID]
allowedRoles = [kt_config.adminID,kt_config.modID,kt_config.teacherID,pr_config.adminID,pr_config.modID]

## Shared Users
makoID = 81105065955303424
botID = 715296437335752714

## Embed Config
# Colors
botColor = 0x113f78 # Black
reportColor = 0x5Da9E9 # Kelutral Blue
QOTDColor = 0x8f6593 # Kelutral Purple
quizColor = 0x113f78 # Deep Blue
rankColor = 0x1e3626 #
welcomeColor = 0x6D326D # 
successColor = 0x00c600 # Green
failColor = 0xff0000 # Red

# Errors
database=discord.Embed(description="**Error:**\nNo entries found.", color=failColor)
denied=discord.Embed(description="**Error: Denied** \n You do not have permission to run this command!", colour=failColor)
success=discord.Embed(description="**Success**", color=successColor)
syntax=discord.Embed(description="**Error: Invalid Syntax** \n If you need help with a command, type `!help <command name>`.", color=failColor)
arguments=discord.Embed(description="**Error: Too Many Arguments** \n If you need help with a command, type `!help <command name>`.", color=failColor)
dm_only=discord.Embed(description="**Error: Denied** \n This command is not permitted here. Use this command in DMs only.", color=failColor)
help_error=discord.Embed(description="**Error: Unknown Command** \n Unknown command specified. Please check your spelling and try again, or use `!help` to see a list of all commands.", color=failColor)
horen_error=discord.Embed(description="**Error: End of File** \n End of Horen reached.", color=failColor)
    
# Initializes the directory at launch
directory = reloadDir()

## -- Initialize Twitter API
import tweepy

# Authenticate to Twitter
auth = tweepy.OAuthHandler("YktlMB8CpIBGwwJbzEl4IPdnW", "mebKR1pwRwU2038sJTcJeXKEXfZ7t6khVmFoa5MGgYHY2SfHBc")
auth.set_access_token("72386464-5V8OQIeM3bAX5BHTxQfrRpIPfl28bLJSf6evDhNVg","IDIjzUCoJvuI42s1aCpqgF7TnaSElkaGfYBPDpsIIWj2w")

# Create API object
api = tweepy.API(auth)

## -- System time check for QOTD and RSS Update.
async def time_check(kelutralBot):
    await kelutralBot.wait_until_ready()
    
    message_channel = kelutralBot.get_channel(kt_config.general)
    bot_ready = kelutralBot.is_closed()

    while not bot_ready:
        now = datetime.strftime(datetime.now(),'%H:%M')
        if send_time == now:
            print(now + " -- Starting daily task check.")
            
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%d-%m-%Y")
            dateCheck = dateTimeObj.strftime("%m-%d-%Y")
            fileName = kt_config.qotdFile.format(timestampStr)
            
            onlyfiles = [f for f in listdir('kelutral-bot/files/config/splashes') if isfile(join('kelutral-bot/files/config/splashes', f))]
            randomSplash = 'kelutral-bot/files/config/splashes/' + onlyfiles[random.randint(0,len(onlyfiles)-1)]
            
            with open(randomSplash, "rb") as image:
                f = image.read()
            
            guild = await kelutralBot.fetch_guild(715043968886505484)
            await guild.edit(banner=f)
            
            if os.path.exists(fileName):
                print(now + " -- Found a QOTD to send")
                with open(fileName, 'r') as fh:
                    fileContents = fh.readlines(1)
                    
                strippedContents = fileContents[0].strip("['")
                strippedContents = fileContents[0].strip("']")

                os.remove(fileName)
                
                await message_channel.send(strippedContents)
                await message_channel.edit(topic=strippedContents,reason="Mipa tìpawm fìtrrä.")

                with open(kt_config.calendarFile,'r') as fh:
                    fileContents = fh.read()

                removeDate = fileContents.replace("\n" + timestampStr,'')
                with open(kt_config.calendarFile,'w') as fh:
                    fh.write(removeDate)
                
                time = 120
                now = datetime.strftime(datetime.now(),'%H:%M')
                print(now + " -- Sending QOTD")
            else:
                time = 120
            
            if dateCheck == sequelDate:
                api.update_status("Yes (finally)")
                print(now + " -- Sending Tweet to @avatarsequels")
                time = 120
            else:
                responses = ["No.",
                             "Still no.",
                             "Stop asking, it's still no.",
                             "Kehe (part., KE-he) \"No\"",
                             "Nope.","Business as usual... No.",
                             "What do you think? No.",
                             "No. Go learn Na'vi at http://kelutral.org/",
                             "One moment please\n*checks the report*\n*turns a few pages*\nOK, so the answer is no.",
                             "BREAKING NEWS: We would like to announce that the first sequel of James Cameron's AVATAR has NOT been released yet."]
                index = random.randint(0,len(responses)-1)
                print(now + " -- Sending Tweet to @avatarsequels")
                api.update_status(responses[index])
                time = 120
            
            randomWord = random.choice(list(dictionary.keys()))
            sivaKoChannel = kelutralBot.get_channel(kt_config.sivaKo)
            
            await sivaKoChannel.send(f"**Daily Challenge**:\n\nCreate a sentence using __{randomWord}__!")
            
        else:
            time = 60
            
        await asyncio.sleep(time)