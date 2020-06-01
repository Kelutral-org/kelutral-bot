# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import os
import glob
import datetime

## -- Variables

kelutralBot = commands.Bot(command_prefix="!")

## -- Functions

def getStats(date):
    joins1 = 0
    leaves1 = 0
    rds1 = 0
    
    fileList = []
    for file in glob.glob('join_data/'+ date + '*.tsk'):
        fileList.append(file)
    for file in fileList:
        if os.path.exists(file):
            fh = open(file, 'r')
            joins = fh.read()
            joins1 = joins1 + int(joins)
            fh.close()
        else:
            joins = joins + 0
    fileList = []
    for file in glob.glob('leave_data/'+ date + '*.tsk'):
        fileList.append(file)
    for file in fileList:
        if os.path.exists(file):
            fh = open(file, 'r')
            leaves = fh.read()
            leaves1 = int(leaves) + leaves1
            fh.close()
        else:
            leaves = leaves + 0
    fileList = []
    for file in glob.glob('rds/'+ date + '*.tsk'):
        fileList.append(file)
    for file in fileList:
        if os.path.exists(file):
            fh = open(file, 'r')
            rds = fh.read()
            rds1 = int(rds) + rds1
            fh.close()
        else:
            rds = rds + 0
            
    return joins1, leaves1, rds1

def outputCheck(user):
    fileName = 'users/' + str(user.id) + '.tsk'

    if not os.path.exists(fileName):
        return "English"
    else:
        # Determines Language Output
        fh = open(fileName, 'r')
        content = fh.readlines()
        fh.close()
        lang = content[2].strip()
        return lang

def checkProfile(user, *args):
    fileName = 'users/' + str(user.id) + '.tsk'
    lines = ['Messages', 'User Name', 'Language Preference']
    indexList = []
    output = []
    i = 0
    line = 0
    
    if os.path.exists(fileName):
        fh = open(fileName, 'r')
        content = fh.readlines()
        fh.close()

        args = list(args)

        while i < len(args):
            indexList.append(lines.index(args[i]))
            i += 1

        indexList.sort()

        while line < len(indexList):
            output.insert(int(indexList[line]),content[int(indexList[line])].strip())
            line += 1
            
        return output
    else:
        return output

def checkPronouns(ctx, user):
    pronounsRole = ['He/Him', 'She/Her', 'They/Them']
    n = 0
    while n < len(pronounsRole):
        role = discord.utils.find(lambda r: r.name == pronounsRole[n], ctx.message.guild.roles)
        if role in user.roles:
            pronouns = pronounsRole[n]
            break
        else:
            pronouns = "Unspecified"
            n += 1
    return pronouns
            
async def adminMsgs(ctx, bot):
    user = ctx.message.author
    rulesChannel = 715727832063410207
    infoChannel = 715049168984473671
    resourcesChannel = 715050231967776778
    if user.top_role.name == "Olo'eyktan (Admin)":
        # path1 = 'files/rules1.txt'
        # path2 = 'files/rules2.txt'
        # path3 = 'files/rules3.txt'

        # fh = open(path1, 'r')
        # file1 = fh.read()
        # fh.close()

        # fh = open(path2, 'r')
        # file2 = fh.read()
        # fh.close()

        # fh = open(path3, 'r')
        # file3 = fh.read()
        # fh.close()

        # channel = bot.get_channel(rulesChannel)

        # await channel.send(file1)
        # await channel.send(file2)
        # await channel.send(file3)

        # oloEyktan = 715044138864607334
        # Eyktan = 715048580334878732
        # Karyu = 715044889049563147
        # Numeyu = 715044972436389890
        # Eylan = 715048542468833321

        # pre1 = "**Role Descriptions:**"
        # pre2 = "{} : Administrators, responsible for upkeep of the Kelutral network of resources.".format(ctx.guild.get_role(oloEyktan).mention)
        # pre3 = "{} : Moderators, responsible for monitoring content in the Kelutral Discord.".format(ctx.guild.get_role(Eyktan).mention)
        # pre4 = "---"
        # pre5 = "{} : Teacher, a capable, volunteer teacher who has shown knowledge and skill in the Na'vi Language".format(ctx.guild.get_role(Karyu).mention)
        # pre6 = "---"
        # pre7 = "{} : Someone who is learning the Na'vi language.".format(ctx.guild.get_role(Numeyu).mention)
        # pre8 = "{} : Inactive or non-language-learning Avatar enthusiasts".format(ctx.guild.get_role(Eylan).mention)
        # pre9 = "---"

        # path4 = 'files/info.txt'

        # fh = open(path4, 'r')
        # file4 = fh.read()
        # fh.close()

        # channel = kelutralBot.get_channel(infoChannel)

        # await channel.send(pre1)
        # await channel.send(pre2)
        # await channel.send(pre3)
        # await channel.send(pre4)
        # await channel.send(pre5)
        # await channel.send(pre6)
        # await channel.send(pre7)
        # await channel.send(pre8)
        # await channel.send(pre9)
        # await channel.send(file4)
        
        path1 = 'files/resources1.txt'
        path2 = 'files/resources2.txt'
        path3 = 'files/resources3.txt'
        path4 = 'files/resources4.txt'

        fh = open(path1, 'r', encoding="utf-8")
        file1 = fh.read()
        fh.close()

        fh = open(path2, 'r', encoding="utf-8")
        file2 = fh.read()
        fh.close()

        channel = bot.get_channel(resourcesChannel)

        await channel.send(file1)
        await channel.send(file2)
        
        fh = open(path3, 'r', encoding="utf-8")
        file1 = fh.read()
        fh.close()
        
        fh = open(path4, 'r', encoding="utf-8")
        file2 = fh.read()
        fh.close()
        
        await channel.send(file1)
        await channel.send(file2)
