# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import json

# Retrieves bot token
with open('files/config/token.txt','r') as file:
    token = file.read()

with open('files/config/config.json', 'r') as fh:
    config = json.load(fh)

# Global Variables
token = token.strip()
prefix = config['prefix']
version = config['version']
debug = False

activeRoleIDs = [715319929942966312, 715319903376113745, 715319861684994069, 715319829611151440, 715319782198739016, 715319761927405668, 715319686710952018, 715319529550381056, 715319404803653632, 715319360884834376, 715319264805912580, 715319193188171846]
activeRoleDict = [[715319929942966312, "Veteran"], [715319903376113745, "Warrior"], [715319861684994069, "Trainee Warrior"], [715319829611151440, "Party Leader"], [715319782198739016, "Ikran Rider"], [715319761927405668, "Hunter"], [715319686710952018, "Trainee Hunter"], [715319529550381056, "Member"], [715319404803653632, "Trainee Member"], [715319360884834376, "Newcomer"], [715319264805912580, "Alien"]]
activeRoleThresholds = [16384, 8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16,8]

lepArchive = [["Placeholder","Tuple"]]

send_time = config['send_time']
sequelDate = config['sequel_date']

# Channels
general = 715296162394931340
modLog = 715052686487191583
lepChannel = 715988382706303038
regChannel = 768599416114118656
newRegChannel = 768627265037664257

# Embed Colors
botColor = 0x113f78
reportColor = 0x5Da9E9
QOTDColor = 0x8f6593
quizColor = 0x113f78
rankColor = 0x1e3626
welcomeColor = 0x6D326D
successColor = 0x00c600
failColor = 0xff0000

# IDs
frapoID = 715319193188171846
botRoleID = 715094486992027699
guildID = 715043968886505484
makoID = 81105065955303424
botID = 715296437335752714
reykID = 716618822744014848
adminID = 715044138864607334
modID = 715048580334878732
teacherID = 715044889049563147

tnpID = 768595645736288306
tnpKaryuID = 768627316958953532

modRoles = [adminID,modID]
allowedRoles = [adminID,modID,teacherID]

# Error Embeds
denied=discord.Embed(description="**Error: Denied** \n You do not have permission to run this command!", colour=failColor)
success=discord.Embed(description="**Success**", color=successColor)
syntax=discord.Embed(description="**Error: Invalid Syntax** \n If you need help with a command, type `!help <command name>`.", color=failColor)
arguments=discord.Embed(description="**Error: Too Many Arguments** \n If you need help with a command, type `!help <command name>`.", color=failColor)
dm_only=discord.Embed(description="**Error: Denied** \n This command is not permitted here. Use this command in DMs only.", color=failColor)
help_error=discord.Embed(description="**Error: Unknown Command** \n Unknown command specified. Please check your spelling and try again, or use `!help` to see a list of all commands.", color=failColor)

# File Paths
qotdFile = 'files/qotd/{}.tsk'
calendarFile = 'files/qotd/calendar.tsk'

botFile = 'cogs/utility/files/users/bot.tsk'
directoryFile = 'cogs/utility/files/users/new-directory.json'

dictionaryFile = 'cogs/utility/files/dictionary.json'
horenFile = 'cogs/utility/files/horen.json'
horenLicense = 'cogs/utility/files/license.txt'
horenChangelog = 'cogs/utility/files/changelog.txt'

## -- Clean output function for Quiz Command
def clean(var):
    var = var.replace("<u>","")
    var = var.replace("</u>","")
    var = var.replace("\"","")
    var = var.replace("([","")
    var = var.replace("])","")
    var = var.replace(" | ",", ")

    return var

# Reloads the directory when it is edited
def reloadDir():
    with open(directoryFile, 'r', encoding='utf-8') as fh:
        directory = json.load(fh)
    return directory

# Help command file
with open('files/config/help.json', 'r', encoding='utf-8') as fh:
    helpFile = json.load(fh)

# English / Na'vi output master file
with open('files/config/text_file.json', 'r', encoding='utf-8') as fh:
    text_file = json.load(fh)

# FAQ
with open('files/config/faq.json', 'r', encoding='utf-8') as fh:
    faq = json.load(fh)

# Initializes the directory at launch
directory = reloadDir()