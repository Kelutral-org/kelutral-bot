# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import asyncio

import random

from datetime import datetime
from datetime import timedelta

import time
import os
import re
import sys
import json
from importlib import reload

import git

import config
import admin
import namegen # namegen.py update courtesy of Yayayr
import watcher

## -- Initialize Client
kelutral = discord.Client()

## -- Initialize Bot
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
kelutralBot = commands.Bot(command_prefix=config.prefix, help_command=None, intents=intents)

## -- Initialize Twitter API
import tweepy

# Authenticate to Twitter
auth = tweepy.OAuthHandler("YktlMB8CpIBGwwJbzEl4IPdnW", "mebKR1pwRwU2038sJTcJeXKEXfZ7t6khVmFoa5MGgYHY2SfHBc")
auth.set_access_token("72386464-5V8OQIeM3bAX5BHTxQfrRpIPfl28bLJSf6evDhNVg","IDIjzUCoJvuI42s1aCpqgF7TnaSElkaGfYBPDpsIIWj2w")

# Create API object
api = tweepy.API(auth)

##--------------------Global Variables--------------------##
## -- -- For Q/MOTD

            #Ja, Fe, Ma, Ap, Ma, Ju, Jl, Au, Se, Oc, No, De
monthDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

naviVocab = [
    # 0 1 2 3 4 5 6 7 actual
    ["", "'aw", "mune", "pxey", "tsìng", "mrr", "pukap", "kinä"],
    # 0 1 2 3 4 5 6 7 last digit
    ["", "aw", "mun", "pey", "sìng", "mrr", "fu", "hin"],
    # 0 1 2 3 4 5 6 7 first or middle digit
    ["", "", "me", "pxe", "tsì", "mrr", "pu", "ki"],
    # 0 1 2 3 4 powers of 8
    ["", "vo", "zam", "vozam", "zazam"],
    # 0 1 2 3 4 powers of 8 last digit
    ["", "l", "", "", ""],
]

##--------------------Global Functions--------------------##
## -- Updates the Visible Stat for 'names generated'

def update(newNameCount):
    fileName = 'files/users/bot.tsk'
    if os.path.exists(fileName): # If bot file exists
        with open(fileName, 'r') as fh:
            nameCount = json.load(fh)
        
        nameCount[0] = nameCount[0] + newNameCount
        
        with open(fileName, 'w') as fh:
            json.dump(nameCount, fh)
        
    return nameCount[0]

## -- System time check for QOTD and RSS Update.
async def time_check():
    await kelutralBot.wait_until_ready()
    
    message_channel = kelutralBot.get_channel(config.general)
    bot_ready = kelutralBot.is_closed()

    while not bot_ready:
        now = datetime.strftime(datetime.now(),'%H:%M')
        if config.send_time == now:
            print(now + " -- Starting daily task check.")
            
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%d-%m-%Y")
            dateCheck = dateTimeObj.strftime("%m-%d-%Y")
            fileName = 'files/qotd/' + timestampStr + '.tsk'
            
            if os.path.exists(fileName):
                print(now + " -- Found a QOTD to send")
                with open(fileName, 'r') as fh:
                    fileContents = fh.readlines(1)
                    
                strippedContents = fileContents[0].strip("['")
                strippedContents = fileContents[0].strip("']")

                os.remove(fileName)
                
                await message_channel.send(strippedContents)
                await message_channel.edit(topic=strippedContents,reason="Mipa tìpawm fìtrrä.")

                with open('files/qotd/calendar.tsk','r') as fh:
                    fileContents = fh.read()

                removeDate = fileContents.replace("\n" + timestampStr,'')
                with open('files/qotd/calendar.tsk','w') as fh:
                    fh.write(removeDate)
                
                time = 120
                now = datetime.strftime(datetime.now(),'%H:%M')
                print(now + " -- Sending QOTD")
            else:
                time = 120
            
            if dateCheck == config.sequelDate:
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
        else:
            time = 60
            
        await asyncio.sleep(time)

## -- English to Na'vi numberical conversion courtesy of Tirea Aean.
def reverse(s): 
    if len(s) == 0: 
        return s 
    else: 
        return reverse(s[1:]) + s[0] 

def wordify(input):
    rev = reverse(input)
    output = ""
    if len(input) == 1:
        if input == "0":
            return "kewa"
        if input == "1":
            return "'awa"
    for i, d in enumerate(rev):
        if i == 0:  # 7777[7]
            output = naviVocab[1][int(d)] + output
            if int(d) == 1 and rev[1] != '0':
                output = naviVocab[4][1] + output
        elif i == 1:  # 777[7]7
            if int((d)) > 0:
                output = naviVocab[2][int(d)] + naviVocab[3][1] + output
        elif i == 2:  # 77[7]77
            if int(d) > 0:
                output = naviVocab[2][int(d)] + naviVocab[3][2] + output
        elif i == 3:  # 7[7]777
            if int(d) > 0:
                output = naviVocab[2][int(d)] + naviVocab[3][3] + output
        elif i == 4:  # [7]7777
            if int(d) > 0:
                output = naviVocab[2][int(d)] + naviVocab[3][4] + output
    for d in ["01", "02", "03", "04", "05", "06", "07"]:
        if rev[0:2] == d:
            output = output + naviVocab[4][1]
        output = output.replace("mm", "m")
        output += "a"
        return output

## -- Function for finding the next available date relative to the current date.
def nextAvailableDate():
    tomorrow = datetime.today() + timedelta(days=1)
    nextDay = tomorrow.strftime("%d-%m-%Y")
    fileName = 'files/qotd/' + str(nextDay) + '.tsk'
    
    while os.path.exists(fileName): # Iterates through the directory to find the first file that doesn't exist. That file is the next available date.
        tomorrow = tomorrow + timedelta(days=1)
        nextDay = tomorrow.strftime("%d-%m-%Y")
        fileName = 'files/qotd/' + str(nextDay) + '.tsk'
    return nextDay

## -- Reads the necessary files and builds the output for the Leaderboard command.
async def buildLeaderboard(ctx, user_id, variant, requested_info):
    messageCounts = []
    userNames = []
    search_user = ctx.message.guild.get_member(user_id)
    t1 = time.time()
    
    ## -- Builds the Current Leaderboard
    async for member in ctx.guild.fetch_members(limit=None):
        profile = admin.readDirectory(member)
        
        if profile != None:
            if member.nick == None:
                userNames.append(str(member.name))
                user = ""
            else:
                userNames.append(str(member.nick))
                user = ""
            
            ## -- Checks the variant of leaderboard to build.
            if variant.lower() == "messages":
                messageCounts.append(admin.readDirectory(member, "message count"))
            elif variant.lower() == "thanks":
                try:
                    messageCounts.append(admin.readDirectory(member, "thanks"))
                except:
                    messageCounts.append(0)
        
    sortedUserNames = [x for _,x in sorted(zip(messageCounts, userNames))]
    sortedMessageCounts = sorted(messageCounts)
    sortedUserNames.reverse()
    sortedMessageCounts.reverse()

    ## -- Indexes by the user who is being searched to find their position on the leaderboard
    if search_user.nick == None:
        pos = sortedUserNames.index(search_user.name) + 1
    else:
        pos = sortedUserNames.index(search_user.nick) + 1
        
    t2 = time.time()
    tDelta = round(t2 - t1, 3)

    return {
        "full"    : [sortedUserNames, sortedMessageCounts, pos, tDelta], # Conditional return for !leaderboard
        "position": pos                                                  # Conditional return for !profile
        }.get(requested_info)
    
## -- Clear screen function
def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')
    
##                                                                                          Bot Events
##-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@kelutralBot.event
async def on_ready():
    nameCount = update(0)
    game = discord.Game("generated " + "{:,}".format(nameCount) + " names!")
    
    await kelutralBot.change_presence(status=discord.Status.online, activity=game)
    
    fileName = 'files/config/startup.txt'
    
    with open(fileName, 'r') as fh:
        lines = fh.readlines()
    
    ## -- Prints the Kelutral OS logo to the command line
    for line in lines:
        print(line.strip('\n').format(config.version))
        time.sleep(.025)
    
    time.sleep(3)
    clear()
    
    now = datetime.strftime(datetime.now(),'%H:%M')
    print(now + " - Watching activity on the server...")
    
    kelutralBot.loop.create_task(time_check())

@kelutralBot.event
async def on_member_join(member):
    await watcher.onJoin(member, kelutralBot)
     
@kelutralBot.event
async def on_member_remove(member):
    await watcher.onLeave(member, kelutralBot)

@kelutralBot.event
async def on_message_delete(message):
    await watcher.onDelete(message, kelutralBot)
    
@kelutralBot.event
async def on_member_update(before, after):
    await watcher.onUpdate(before, after, kelutralBot)
    
@kelutralBot.event
async def on_member_ban(guild, user):
    await watcher.onBan(guild, user, kelutralBot)
    
@kelutralBot.event
async def on_member_unban(guild, user):
    await watcher.onUnban(guild, user, kelutralBot)
    
@kelutralBot.event
async def on_message(message): 
    await watcher.onMessage(message, kelutralBot)
    
    await kelutralBot.process_commands(message)

@kelutralBot.event
async def on_voice_state_update(member, before, after):
    await watcher.onVCUpdate(member, before, after, kelutralBot)
    
@kelutralBot.event
async def on_raw_reaction_add(payload):
    await watcher.onReaction(payload, kelutralBot)
    
@kelutralBot.event
async def on_command(ctx):
    now = datetime.now().strftime('%H:%M')
    command = ctx.message.content.split(" ")[0]
    arguments = ctx.message.content.replace(command, "")
    print(now + " -- {}: {} executed the {} command with arguments:{}".format(ctx.message.author.name, ctx.message.author.id, command, arguments))

##                                                                                          Debug Commands
##------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Utility Command
@kelutralBot.command(name='test')
async def test(ctx, *date):
    with open('files/config/server_info.json', 'r', encoding='utf-8') as fh:
        server_info = json.load(fh)

    joins = 0
    leaves = 0
    rds = 0
       
    if date:
        date = ''.join(date)
        date = date.replace("*", ".")
        for entry in server_info:
            x = re.search(date, entry)
            if x:
                joins += server_info[entry]['joins']
                leaves += server_info[entry]['leaves']
                rds += server_info[entry]['rds']
    else:
        date = datetime.now().strftime("%m-%d-%Y")
        joins = server_info[date]['joins']
        leaves = server_info[date]['leaves']
        rds = server_info[date]['rds']
    
    with open('files/config/server_info.json', 'w', encoding='utf-8') as fh:
        json.dump(server_info, fh)
    await ctx.send("Found {} joins, {} leaves, and {} rds for that date range.".format(joins, leaves, rds))

## Update Rules
@kelutralBot.command(name='donotuse')
async def updateRules(ctx):
    user = ctx.message.author
    if user.top_role.id == config.adminID:
        await admin.adminMsgs(ctx, kelutralBot)

## Debug toggle
@kelutralBot.command(name='debug')
async def debugToggle(ctx):
    user = ctx.message.author
    
    if user.id == config.makoID:
        if config.debug == False:
            config.debug = True
            await ctx.send(embed=config.success)
        else:
            config.debug = False
            await ctx.send(embed=config.success)
    else:
        await ctx.send(embed=config.denied)

## Fixes a directory entry
@kelutralBot.command(name='fix')
async def fixDirectory(ctx, user: discord.Member, attribute, newVal):
    if ctx.message.author.top_role.id in modRoles:
        admin.writeDirectory(user, attribute, newVal)
        await ctx.send("Updated!")

## Kill Command
@kelutralBot.command(name='quit', aliases=['ftang'])
async def botquit(ctx):
    user = ctx.message.author

    if user.top_role.id == config.adminID:
        embed=discord.Embed(description="Shutting down...", colour=config.failColor)
        await ctx.send(embed=embed)
        await kelutralBot.close()
        quit()
    else:
        await ctx.send(embed=config.denied)

## Reload command
@kelutralBot.command(name='reload')
async def reloadBot(ctx):
    if ctx.message.author.top_role.id == config.adminID:
        await ctx.send("Reloading the bot...")
        reload(config)
        await ctx.send("Launching KelutralBot version {}".format(config.version))
        await kelutralBot.close()
        os.execv(sys.executable, ['python3'] + sys.argv)

## Member Join Stats   
@kelutralBot.command(name='showdata', aliases=['sd'])
async def showData(ctx, *date):
    user = ctx.message.author
    t1 = time.time()
    if user.top_role.id == config.adminID:
        if date:
            date = ''.join(date)
            joins1, leaves1, rds1 = admin.getStats(date)
        else:
            date = datetime.now().strftime('%m-%d-%Y')
            joins1, leaves1, rds1 = admin.getStats(date)
        
        embed=discord.Embed(title="Requested report for " + date, color=config.reportColor)
        embed.add_field(name="Joins", value=joins1, inline=True)
        embed.add_field(name="Leaves", value=leaves1, inline=True)
        embed.add_field(name="Revolving Doors", value=rds1, inline=True)
        if joins1 > 0:
            turnover = round(((leaves1 - rds1) / joins1) * 100, 2)
        else:
            turnover = 0
        embed.add_field(name="Turnover Rate", value=str(turnover) + "%", inline=True)
        if leaves1 > 0:
            retention = round((rds1 / leaves1) * 100, 2)
        else:
            retention = 0
        embed.add_field(name="RD %", value=str(retention) + "%", inline=True)
        
        t2 = time.time()
        tDelta = round(t2 - t1, 3)
        
        if config.debug == True:
            embed.set_footer(text="Use !find mm-dd-yyyy to query specific dates, or replace \nletters with ** to search all dates in that category.  |  Executed in " + str(tDelta) + " seconds.")
        else:
            embed.set_footer(text="Use !find mm-dd-yyyy to query specific dates, or replace \nletters with ** to search all dates in that category.")
        embed.set_footer(text="Use !find mm-dd-yyyy to query specific dates, or replace \nletters with ** to search all dates in that category.")
        
        await ctx.send(embed=embed)
        
    else:
        await ctx.send(embed=config.denied)

## Updates the bot and relaunches
@kelutralBot.   command(name='update')
async def updateBot(ctx, version, commit):
    if ctx.message.author.top_role.id == config.adminID:
        config.version = version
        
        REPO = r'C:\Users\Seth\kelutral-bot\.git'
        g = git.cmd.Git(r'C:\Users\Seth\kelutral-bot')
        COMMIT_MESSAGE = commit
        
        repo = git.Repo(REPO)
        repo.git.add(update=True)
        repo.index.commit(COMMIT_MESSAGE)
        
        origin = repo.remote(name='kelutral-bot')
        msg = origin.push()
        await ctx.send("Updating the bot...")
        
        msg = g.pull()
        await ctx.send("Pulling from the repo...")
        
        reload(config)
        await ctx.send("Launching KelutralBot version {}".format(config.version))
        
        await kelutralBot.close()
        
        os.execv(sys.executable, ['python3'] + sys.argv)

##                                                                                          Bot Commands
##------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##                                                                               Condensed Question of the Day Command
##------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@kelutralBot.command(name='qotd', aliases=['tìpawm'])
async def qotd(ctx, function, question, *date):
    user = ctx.message.author
    profile = admin.readDirectory(user)
    now = datetime.strftime(datetime.now(), '%H:%M')
    t1 = time.time()
    
    if user.top_role.id in config.allowedRoles:
        if date:
            date = str(date).strip("(),' ")
            fileName = config.qotdFile.format(str(date))
            if os.path.exists(fileName): ## Add specific error checking and output here
                modDate = nextAvailableDate()
                file_exists = True
                embed=discord.Embed(description=config.text_file[profile['language']]['errors']['qotd'] + config.text_file[profile['language']]['errors']['qotd_errors']['date_taken'].format(modDate), colour=config.failColor)
        else:
            date = nextAvailableDate()
            fileName = config.qotdFile.format(str(date))
            file_exists = False
            
    if function.lower() == 'add' and not file_exists:
        with open(fileName, 'w') as fh:
            fh.write(question)
            
        with open(config.calendarFile, 'w') as fh:
            fh.write("\n" + str(date))
            
        print(now + " -- Created a question of the day for {}.".format(str(date)))
        embed=discord.Embed(description=config.text_file[profile['language']]['qotd']['created'], color=config.successColor)
    elif function.lower() == 'edit' and file_exists:
        with open(fileName, 'w') as fh:
            fh.write(question)
            
        print(now + " -- Edited the question of the day on {}.".format(str(date)))
        embed=discord.Embed(description=config.text_file[profile['language']]['qotd']['edited'], color=config.successColor)
    elif function.lower() == 'delete' and file_exists:
        os.remove(fileName)
        
        with open(config.calendarFile, 'r') as fh:
            fileContents = fh.read()
        
        with open(config.calendarFile, 'w') as fh:
            removeDate = fileContents.replace("\n" + str(date),'')
            fh.write(removeDate)
            
        print(now + " -- Removed the question of the day on {}.".format(str(date)))
        embed=discord.Embed(description=config.text_file[profile['language']]['qotd']['deleted'], color=config.successColor)
    elif function.lower() == 'view' and file_exists:
        with open(fileName, 'r') as fh:
            contents = fh.read()
        
        print(now + " -- Retrieved the question of the day on {}.".format(str(date)))
        embed=discord.Embed(description=config.text_file[profile['language']]['qotd']['read'].format(contents), color=config.QOTDColor)
    elif function.lower() == 'schedule':
        dates = []
        questions = []
        if not os.path.getsize(config.calendarFile) == 10:
            with open(config.calendarFile, 'r') as fh:
                for line in fh:
                    filePath = config.qotdFile.format(line.strip())
                    if os.path.exists(filePath):
                        dates.append(line.strip())
                        with open(filePath, 'r') as fp:
                            questions.append(fp.read())
                            
            print(now + " -- Building a list of scheduled questions of the day.")
            embed=discord.Embed(description=config.text_file[profile['language']]['qotd']['schedule'], color=config.QOTDColor)
            for i, (question, date) in enumerate(zip(questions, dates)):
                embed.add_field(name=date, value="'{}'.".format(question), inline=True)
    elif not file_exists:
        embed=discord.Embed(description=config.text_file[profile['language']]['errors']['qotd'] + config.text_file[profile['language']]['errors']['qotd_errors']['no_file'].format(modDate), color=config.failColor)
    else:
        embed=discord.Embed(description=config.text_file[profile['language']]['errors']['qotd'] + config.text_file[profile['language']]['errors']['qotd_errors']['invalid_function'], color=config.failColor)
    
    t2 = time.time()
    tDelta = round(t2 - t1, 3)
    
    if config.debug:
        embed.set_footer(text="Executed in {} seconds.".format(str(tDelta)))
    
    await ctx.send(embed=embed)

##                                                                               The Neytiri Project Command Grouping
##------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Accepts a submitted request for a teacher
@kelutralBot.command(name='accept')
async def accept(ctx, user_id):
    teacher = ctx.message.author
    student = ctx.guild.get_member(int(user_id))
    
    # Retrieves the necessary profiles
    student_profile = admin.readDirectory(student)
    teacher_profile = admin.readDirectory(teacher)
    
    # Checks for a registration message from the student
    if type(student_profile['tnp']['registration']) == int:
        reg_id = student_profile['tnp']['registration']
        student_profile['tnp']['accepted_by'] = user.id
        
        # Retrieves the registration channel
        channel = kelutralBot.get_channel(768627265037664257) #new-registrations
        
        # Retrieves the registration message
        message = await channel.fetch_message(reg_id)
        
        # Edits the registration message to confirm acceptance
        embed = discord.Embed(title="{}: {}".format(student.name, student.id), description="{} was accepted by {}!".format(student.name, teacher.name), color=config.successColor)
        await message.edit(embed=embed)
        
        # Retrieves the teacher's channel
        teacher_channel = kelutralBot.get_channel(teacher_profile['tnp']['channel'])
        
        # Updates the student's permissions in the teacher's channel and sends them a confirmation message
        await teacher_channel.set_permissions(student, send_messages = True, read_messages = True)
        await teacher_channel.send("{} has accepted you ma {}!".format(teacher.mention, student.mention))

## Registers for The Neytiri Project
@kelutralBot.command(name='tnp')
async def accessTNP(ctx):
    user = ctx.message.author
    channel = kelutralBot.get_channel(config.regChannel) # Registration Channel
    guild = ctx.message.guild
    
    profile = admin.readDirectory(user)
    
    if get(guild.roles, id=config.teacherID) in user.roles:
        embed_role = get(guild.roles, id=config.teacherID)
        embed_channel = guild.get_channel(769027341857849435)
    else:
        embed_role = get(guild.roles, id=715044972436389890)
        embed_channel = channel
    
    # Tries to retrieve the Neytiri Project subdict from the profile
    try:
        theNeytiriProject = profile['tnp']
    except KeyError:
        profile['tnp'] = {
            'channel' : '',
            'registration' : ''
            }
        theNeytiriProject = profile['tnp']
    
    # If the user has the teacher role, registers them as a teacher
    if get(ctx.guild.roles, id=config.teacherID) in user.roles:
        # Adds the TNP roles
        tnpRole = get(ctx.guild.roles, id=config.tnpID)
        await user.add_roles(tnpRole, get(guild.roles, id=config.tnpKaryuID))
        
        # Creates the teacher channel and sets perms for the user
        new_channel = await guild.create_text_channel("{}'s-channel".format(user.name), category = get(guild.categories, id=768591895227007016))
        
        perms = new_channel.overwrites_for(tnpRole)
        perms.view_channel = False
        await new_channel.set_permissions(tnpRole, overwrite=perms)
        await new_channel.set_permissions(user, send_messages = True, read_messages = True)
        
        # Adds the new channel id to the teacher's profile.
        theNeytiriProject['channel'] = new_channel.id
        
        admin.updateDirectory()
    
    # If the user does not have the teacher role, registers them as a learner
    else:
        # Adds TNP role and sets permissions for the #registration channel
        await user.add_roles(get(guild.roles, id =config.tnpID))
        await channel.set_permissions(user, send_messages = True, read_messages = True)
    
    # Tries to DM the user
    try:
        embed = discord.Embed(title="Welcome to The Neytiri Project", description="Please read this information before continuing.\n\nThe Neytiri Project is a 1 on 1 teaching program where teachers can pair with dedicated students based on shared qualities like time-zone or learning style.\n\nYou have been accepted as a **{}** based on your existing roles in Kelutral.org.\n\nProspective teacher's availability to teach is determined by them, and they are under no obligation to teach if they are busy or have other responsibilites to attend to. To get started with registration, use !register in {}.".format(embed_role.name, embed_channel.mention), color=config.reportColor)
        embed.set_footer(text="To leave the Neytiri Project, use !unregister at any time.")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/539428806558220308/539429072422436895/TNP2.png")
        await user.send(embed=embed)
    except:
        embed = discord.Embed(description="Unable to DM. Please allow DMs from the bot to continue.", color=config.failColor)
        await ctx.send(embed=embed)
        return
    
    # Sends the confirmation
    embed = discord.Embed(title="The Neytiri Project", description="Accepted your registration! Check your DMs for more the next steps.")
    
    await ctx.send(embed=embed)

## Requests a teacher for The Neytiri Project
@kelutralBot.command(name='register')
async def register(ctx):
    channel = ctx.message.channel
    author = ctx.message.author
    profile = admin.readDirectory(author)
    
    # Conditional check for the registration process
    def check(c):
        return c.channel == channel and c.author == author
        
    if type(profile['tnp']['registration']) == int:
        embed = discord.Embed(description="You already have a teacher request on file. To change your request, use `!unregister` and start over.")
        await ctx.send(embed=embed)
        return
        
    if get(ctx.guild.roles, id=config.teacherID) in author.roles:
        teacher_channel = ctx.guild.get_channel(profile['tnp']['channel'])
        
        embed = discord.Embed(title="Create a Teacher Profile", description="Thanks for signing up to teach in **The Neytiri Project**! I just need a little bit of information from you to get your teacher bio set up. To get started, tell me a little bit about yourself.")
        message = await ctx.send(embed=embed)
        
        master_loop = True
        while master_loop:
            
            step_one = True
            while step_one:
                about_me = await kelutralBot.wait_for('message', check=check)
                await about_me.delete()
                
                embed = discord.Embed(title=author.name, description="Here's what I received:\n\n'{}'\n\nDoes that look correct? Let me know with 'yes' or 'no'".format(about_me.content), color=config.reportColor)
                embed.set_footer(text="Step 1/4")
                await message.edit(embed=embed)
                
                response = await kelutralBot.wait_for('message', check=check)
                if response.content.lower() == 'yes':
                    step_one = False
                    embed = discord.Embed(title=author.name, description="Great! What is your time-zone?", color=config.reportColor)
                    embed.set_footer(text="Step 2/4")
                    await message.edit(embed=embed)
                else:
                    embed = discord.Embed(title=author.name, description="Okay, let's try again. Tell me a little bit about yourself.", color=config.welcomeColor)
                    embed.set_footer(text="Step 1/4")
                    await message.edit(embed=embed)
                
                await response.delete()
            
            step_two = True
            while step_two:
                time_zone = await kelutralBot.wait_for('message', check=check)
                await time_zone.delete()
                embed = discord.Embed(title=author.name, description="Great! So your time-zone is '{}', correct? Let me know with 'yes' or 'no'".format(time_zone.content), color=config.reportColor)
                embed.set_footer(text="Step 2/4")
                await message.edit(embed=embed)
                
                response = await kelutralBot.wait_for('message', check=check)
                if response.content.lower() == 'yes':
                    step_two = False
                    embed = discord.Embed(title=author.name, description="Great! Moving on. How would you describe your teaching style?", color=config.reportColor)
                    embed.set_footer(text="Step 3/4")
                    await message.edit(embed=embed)
                else:
                    embed = discord.Embed(title=author.name, description="Okay, let's try again. What is your time-zone?", color=config.welcomeColor)
                    embed.set_footer(text="Step 2/4")
                    await message.edit(embed=embed)
                
                await response.delete()
            
            step_three = True
            while step_three:
                teaching = await kelutralBot.wait_for('message', check=check)
                await teaching.delete()
                embed = discord.Embed(title=author.name, description="Great! Making sure I got that, you said '{}', correct? Let me know with 'yes' or 'no'.".format(teaching.content), color=config.reportColor)
                embed.set_footer(text="Step 3/4")
                await message.edit(embed=embed)
            
                response = await kelutralBot.wait_for('message', check=check)
                if response.content.lower() == 'yes':
                    step_three = False
                    embed = discord.Embed(title=author.name, description="Great! Moving on. What is your favorite Na'vi word and why?", color=config.reportColor)
                    embed.set_footer(text="Step 4/4")
                    await message.edit(embed=embed)
                else:
                    embed = discord.Embed(title=author.name, description="Okay, let's try again. How would you describe your teaching style?", color=config.welcomeColor)
                    embed.set_footer(text="Step 3/4")
                    await message.edit(embed=embed)
                
                await response.delete()
                
            step_four = True
            while step_four:
                fav_word = await kelutralBot.wait_for('message', check=check)
                await fav_word.delete()
                embed = discord.Embed(title=author.name, description="Great! Making sure I got that, you said '{}', correct? Let me know with 'yes' or 'no'.".format(fav_word.content), color=config.reportColor)
                embed.add_field(name="Favorite Na'vi Word:", value=fav_word.content)
                embed.set_footer(text="Step 3/4")
                await message.edit(embed=embed)
            
                response = await kelutralBot.wait_for('message', check=check)
                if response.content.lower() == 'yes':
                    step_four = False
                    embed = discord.Embed(title=author.name, description="Great! Moving on. What is your favorite Na'vi word and why?", color=config.reportColor)
                    embed.set_footer(text="Step 4/4")
                    await message.edit(embed=embed)
                else:
                    embed = discord.Embed(title=author.name, description="Okay, let's try again. What is your favorite Na'vi word and why?", color=config.welcomeColor)
                    embed.set_footer(text="Step 3/4")
                    await message.edit(embed=embed)
                
                await response.delete()
                
            # Prompts the user to confirm all their submitted information is correct
            step_five = True
            while step_five:
                embed = discord.Embed(title=author.name, description="Does everything look correct? Let me know with 'yes' or 'no'.", color=config.reportColor)
                embed.add_field(name="About Me:", value=about_me.content, inline=False)
                embed.add_field(name="Time Zone:", value=time_zone.content, inline=True)
                embed.add_field(name="Teaching Style:", value=teaching.content, inline=True)
                embed.add_field(name="Favorite Na'vi Word:", value=fav_word.content, inline=True)
                embed.set_footer(text="Step 4/4")
                await message.edit(embed=embed)
            
                response = await kelutralBot.wait_for('message', check=check)
                if response.content.lower() == 'yes':
                    # Ends both loops
                    step_five = False
                    master_loop = False
                    
                    await response.delete()
                    
                    # Builds the registration embed for #new-registrations
                    embed = discord.Embed(title="{}: {}".format(author.name, author.id))
                    embed.add_field(name="About Me:", value=about_me.content, inline=False)
                    embed.add_field(name="Time Zone:", value=time_zone.content, inline=True)
                    embed.add_field(name="Teaching Style:", value=teaching.content, inline=True)
                    embed.add_field(name="Favorite Na'vi Word:", value=fav_word.content, inline=True)
                    embed.set_thumbnail(url=author.avatar_url)
                    
                    try:
                        registration_message = await teacher_channel.fetch_message(profile['tnp']['registration'])
                        await registration_message.edit(embed=embed)
                    except:
                        registration_message = await teacher_channel.send(embed=embed)
                        profile['tnp']['registration'] = registration_message.id
                        await registration_message.pin()
                    
                    admin.updateDirectory()
                    
                    embed = discord.Embed(title=author.name, description="Alright! You're all set. Your profile has been automatically posted and pinned in your teaching channel for prospective learners to read. If at any point you wish to update your profile, simply run this command again.", color=config.reportColor)
                    await message.edit(embed=embed)
                    await asyncio.sleep(120)
                    await message.delete()
                else:
                    embed = discord.Embed(title=author.name, description="Okay, let's go back to the top. Tell me a little bit about yourself.", color=config.welcomeColor)
                    embed.set_footer(text="Step 1/3")
                    await message.edit(embed=embed)
                    await response.delete()
                    
    else:
        embed = discord.Embed(title="Registration Form: {}".format(author.name), description="Thanks for registering for The Neytiri Project ma {}. Please answer a few short questions to help give teachers a better idea of whether or not you would be a good fit for them.\n\nTo start, what is your time-zone?".format(author.mention), color=config.reportColor)
        message = await ctx.send(embed=embed)
        
        master_loop = True
        while master_loop:
            # Prompts the user for their time zone
            step_one = True
            while step_one:
                time_zone = await kelutralBot.wait_for('message', check=check)
                await time_zone.delete()
                embed = discord.Embed(title=author.name, description="Great! So your time zone is '{}', correct? Let me know with 'yes' or 'no'".format(time_zone.content), color=config.reportColor)
                embed.set_footer(text="Step 1/3")
                dict_embed = embed.to_dict()
                await message.edit(embed=embed)
                
                response = await kelutralBot.wait_for('message', check=check)
                if response.content.lower() == 'yes':
                    step_one = False
                    dict_embed['description'] = "Great! Moving on. When are you available during the week? As much detail as possible will help the teachers."
                    dict_embed['footer'] = {'text' : "Step 2/3"}
                    dict_embed['fields'] = [{'name' : "Time Zone",'value' : time_zone.content}]
                    await message.edit(embed=discord.Embed.from_dict(dict_embed))
                else:
                    dict_embed['description'] = "Okay, let's try again. What is your time-zone?"
                    dict_embed['color'] = config.welcomeColor
                    await message.edit(embed=discord.Embed.from_dict(dict_embed))
                
                await response.delete()
            
            # Prompts the user for their availability
            step_two = True
            while step_two:
                availability = await kelutralBot.wait_for('message', check=check)
                await availability.delete()
                dict_embed['description'] = "Great! So your availability is '{}', correct? Let me know with 'yes' or 'no'".format(availability.content)
                dict_embed['color'] = config.reportColor
                await message.edit(embed=discord.Embed.from_dict(dict_embed))
            
                response = await kelutralBot.wait_for('message', check=check)
                if response.content.lower() == 'yes':
                    step_two = False
                    dict_embed['description'] = "Great! Moving on. How would you describe your learning style?"
                    dict_embed['fields'].append({'name' : "Availability", 'value' : availability.content})
                    dict_embed['footer'] = {'text' : "Step 3/3"}
                    await message.edit(embed=discord.Embed.from_dict(dict_embed))
                else:
                    dict_embed['description'] = "Okay, let's try again. What is your availability during the week?"
                    dict_embed['color'] = config.welcomeColor
                    await message.edit(embed=discord.Embed.from_dict(dict_embed))
                
                await response.delete()
            
            # Prompts the user for their learning style
            step_three = True
            while step_three:
                learning = await kelutralBot.wait_for('message', check=check)
                await learning.delete()
                dict_embed['description'] = "Great! Making sure I got that, you said '{}', correct? Let me know with 'yes' or 'no'.".format(learning.content)
                dict_embed['color'] = config.reportColor
                await message.edit(embed=discord.Embed.from_dict(dict_embed))
            
                response = await kelutralBot.wait_for('message', check=check)
                if response.content.lower() == 'yes':
                    step_three = False
                    dict_embed['fields'].append({'name' : "Learning Style", 'value' : learning.content})
                    await message.edit(embed=discord.Embed.from_dict(dict_embed))
                else:
                    dict_embed['description'] = "Okay, let's try again. How would you describe your learning style?"
                    dict_embed['color'] = config.welcomeColor
                    await message.edit(embed=discord.Embed.from_dict(dict_embed))
                
                await response.delete()
            
            # Prompts the user to confirm all their submitted information is correct
            step_four = True
            while step_four:
                dict_embed['description'] = "Does everything look correct? Let me know with 'yes' or 'no'."
                await message.edit(embed=discord.Embed.from_dict(dict_embed))
            
                response = await kelutralBot.wait_for('message', check=check)
                if response.content.lower() == 'yes':
                    # Ends both loops
                    step_four = False
                    master_loop = False
                    
                    await response.delete()
                    
                    # Builds the registration embed for #new-registrations
                    registration_channel = kelutralBot.get_channel(768627265037664257)
                    dict_embed['title'] = "{}: {}".format(author.name, author.id)
                    dict_embed['description'] = ""
                    dict_embed['footer'] = {'text' : "Use !accept <id> to accept this registration"}
                    
                    embed = discord.Embed.from_dict(dict_embed)
                    embed.set_thumbnail(url=author.avatar_url)
                    # Sends the registration
                    registration_message = await registration_channel.send(embed=embed)
                    
                    admin.writeDirectory(author, 'tnp', {"channel" : "", "registration" : registration_message.id})
                    admin.updateDirectory()
                    
                    dict_embed['title'] = author.name
                    dict_embed['description'] = "Alright! You're all set. Available teachers have been notified of your registration. If one decides that you are a good match for them, you will be notified."
                    await message.edit(embed=discord.Embed.from_dict(dict_embed))
                    await asyncio.sleep(120)
                    await channel.set_permissions(author, send_messages = False, read_messages = False)
                    await message.delete()
                
                elif response.content.lower() == 'no':
                    dict_embed['description'] = "Okay, let's go back to the top. what is your time-zone?"
                    dict_embed['color'] = config.welcomeColor
                    dict_embed['footer'] = {'text' : "Step 1/3"}
                    dict_embed['fields'] = []
                    await message.edit(embed=discord.Embed.from_dict(dict_embed))
                    step_four = False
                
                await response.delete()

## Unregisters from The Neytiri Project
@kelutralBot.command(name='unregister')
async def unregisterTNP(ctx):
    user = ctx.message.author
    channel = kelutralBot.get_channel(config.regChannel) #registration
    reg_channel = kelutralBot.get_channel(768627265037664257) #new-registrations
    
    profile = admin.readDirectory(user)
    
    # Checks registered users for the command author's id
    if type(profile['tnp']['registration']) == int:
        # Removes registration entry in #new-registrations
        try:
            message = await reg_channel.fetch_message(profile['tnp']['registration'])
            await message.delete()
        except discord.errors.NotFound:
            print("Original message has been deleted!")
        
        profile['tnp']['registration'] = ''
        
        # Removes relevant roles
        await user.remove_roles(get(ctx.guild.roles, id=config.tnpID)) # @TNP
    
    elif type(profile['tnp']['channel']) == int:
        # Removes the teacher's channel
        teacher_channel = kelutralBot.get_channel(profile['tnp']['channel'])
        await teacher_channel.delete()
        
        # Removes relevant roles 
        await user.remove_roles(get(ctx.guild.roles, id=config.tnpKaryuID)) # @TNPKaryu
    
    try:
        if type(profile['tnp']['accepted_by']) == int:
            teacher_profile = admin.readDirectory(ctx.guild.get_member(profile['tnp']['accepted_by']))
            teacher_channel = kelutralBot.get_channel(teacher_profile['tnp']['channel'])
            
            await teacher_channel.set_permissions(user, send_messages = False, read_messages = False)
    except:
        profile['tnp']['accepted_by'] = ""
    
    # Revokes access to #registration if accessible
    await channel.set_permissions(user, send_messages = False, read_messages = False)
    
    embed = discord.Embed(description="Unregistered you.")
    await ctx.send(embed=embed)
    
    admin.updateDirectory()

##------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## About the bot
@kelutralBot.command(name='about', aliases=['teri'])
async def about(ctx):
    mako = ctx.message.guild.get_member(config.makoID)
    self = ctx.message.guild.get_member(config.botID)
    fileName = config.botFile
    t1 = time.time()
    
    ## -- Pulls current number of generated names.
    with open(fileName, 'r') as fh:
        names = json.load(fh)
        
    embed=discord.Embed(title="About Eytukan",description="Eytukan is a custom bot coded in Python 3 for use on Kelutral.org's Discord Server. It is primarily coded and maintained by " + str(mako.mention) + ".", color=config.botColor)
    embed.set_author(name=self.name,icon_url=self.avatar_url)
    embed.add_field(name="Version: ", value=config.version, inline=True)
    embed.add_field(name="Website: ", value="http://kelutral.org/", inline=True)
    embed.add_field(name="Discord.py:", value="Version " + str(discord.__version__))
    embed.add_field(name="Na'vi Names Generated: ", value=names[0], inline=True)
    embed.set_thumbnail(url=ctx.guild.icon_url)
    
    t2 = time.time()
    tDelta = round(t2-t1,3)
    
    ## -- Checks debug output toggle
    if config.debug == True:
        embed.set_footer(text="Use !help to learn more about the available commands.  |  Executed in " + str(tDelta) + " seconds.")
    else:
        embed.set_footer(text="Use !help to learn more about the available commands.")
        
    await ctx.send(embed=embed)

## Ban Command
@kelutralBot.command(name='ban', aliases=['yitx'])
async def ban(ctx, user: discord.Member):
    if user.top_role.id in config.modRoles: # If the user is allowed to use this command
        await user.ban()
        embed=discord.Embed(description=str(user.mention) + "** was banned**", colour=config.failColor)
        await ctx.send(embed=embed)

## FAQ Command
@kelutralBot.command(name="faq",aliases=['sìpawm'])
async def faq(ctx, *topic):
    user = ctx.message.author
    output = ""
    
    if user.top_role.id in config.allowedRoles:
        try:
            # Tries to find the first header
            requested_topic = config.faq[topic[0]]
            
            # Returns all topics for the specified header
            for entry in config.faq[topic[0]]:
                output += "- **" + entry + "** \n"
           
            try:
                # If requested topic found, try subtopic
                requested_subtopic = requested_topic[topic[1]]
                
                # If requested subtopic found, send
                await ctx.send(embed=discord.Embed(description=requested_subtopic, color=config.reportColor))
            
            except IndexError:
                if type(requested_topic) == str:
                    await ctx.send(embed=discord.Embed(description=requested_topic, color=config.reportColor))
                else:
                    await ctx.send(embed=discord.Embed(description="Here are all of the available topics for **{}**: \n{}".format(topic[0], output), color=config.reportColor))
                
            except KeyError:
                # If a subtopic is specified and cannot be found, sends the error embed
                await ctx.send(embed=discord.Embed(description="Could not find an entry for **{}**. Perhaps you meant one of these: \n{}".format(topic[1], output), color=config.failColor))
                
        except IndexError:
            # If no header exists, sends all of the top-level headers
            if topic == ():
                for entry in config.faq:
                    output += "- **" + entry + "** \n"
            
                await ctx.send(embed=discord.Embed(description="Here are all of the available topics for `!faq`: \n{}".format(output), color=config.reportColor))
        
        except KeyError:
            # If topic is specified and cannot be found, sends the error embed
            await ctx.send(embed=discord.Embed(description="Could not find an entry for **{}**.".format(topic[0]), color=config.failColor))

## Generate # of random names
@kelutralBot.command(name="generate",aliases=['ngop'])
async def generate(ctx, numOut, numSyllables, *letterPrefs):
    user = ctx.message.author
    n = int(numOut)
    i = int(numSyllables)
    output = []
    c = 0
    language = admin.readDirectory(user, "language")
    
    if not n <= 0 and not i <= 0:
            if not i <= 5:
                embed=discord.Embed(description=config.text_file[language]["errors"]["generate_error"] + config.text_file[language]["errors"]["generate_errors"]["syllables"], colour=config.failColor) 
                await ctx.send(embed=embed)
                
            elif not n <= 20:
                embed=discord.Embed(description=config.text_file[language]["errors"]["generate_error"] + config.text_file[language]["errors"]["generate_errors"]["names"], colour=config.failColor) 
                await ctx.send(embed=embed)
                
            else:
                nameCount = update(n)
                game = discord.Game("ngamop " + "{:,}".format(nameCount) + " tstxoti.")
        
                await kelutralBot.change_presence(status=discord.Status.online, activity=game)

                embed=discord.Embed(color=config.successColor)
                embed.set_author(name=config.text_file[language]["generate"]["success"].format(ctx.message.author.name))
                
                while c < n:
                    output.append(namegen.nameGen(numSyllables, letterPrefs))
                    embed.add_field(name=config.text_file[language]["generate"]["name"] + str(c + 1) + ":", value=output[c], inline=True)
                    c += 1
                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                
                await ctx.send(embed=embed)

    else:
        embed=discord.Embed(description=config.text_file[language]["errors"]["generate_error"] + config.text_file[language]["errors"]["generate_errors"]["zero"], color=config.failColor)
        await ctx.send(embed=embed)
    
    now = datetime.strftime(datetime.now(),'%H:%M')
    print(now + " -- " + ctx.author.name + " generated " + str(n) + " names.")

## Display Server Leaderboard
@kelutralBot.command(name='leaderboard')
async def leaderboard(ctx, variant):
    i = 0
    leaderboard = ""
    
    # Checks for a valid variant and builds the overall server leaderboard list
    if variant.lower() == "messages" or variant.lower() == "thanks":
        output = await buildLeaderboard(ctx, ctx.message.author.id, variant, "full")
    else:
        await ctx.send(embed=config.syntax)
        return
    
    # Builds the top 10 list
    while i <= 9:
        leaderboard = leaderboard + "**" + output[0][i] + "**\n" + str(output[1][i]) + " messages  |  Rank: #" + str(i + 1) + "\n\n"
        i += 1
    
    # Builds final embed
    embed=discord.Embed(title="Server Leaderboard:", description=leaderboard, color=config.reportColor)
    if config.debug == True:
        embed.set_footer(text="You are ranked #" + str(output[2]) + " overall.  |  Executed in " + str(output[3]) + " seconds.")
    else:
        embed.set_footer(text="You are ranked #" + str(output[2]) + " overall.")
    
    # Sends results
    await ctx.send(embed=embed)
    
## Display User Message Count
@kelutralBot.command(name='profile', aliases=['yì'])
async def profile(ctx, user: discord.Member, *setting):
    preference = ''.join(setting).lower()
    variant = "messages"
    
    # Function for building the final profile output
    async def buildEmbed(user, language_pref, to_next_level, active_roles):
        # Checks if the user has a nickname
        try:
            nickname = " AKA \"" + user.nick + "\""
        except:
            nickname = ""
            
        # Checks if the user has 'unspecified'
        if type(admin.readDirectory(user, "pronouns")) == int:
            pronoun_role = get(user.guild.roles, id=admin.readDirectory(user, "pronouns")).name
        else:
            pronoun_role = admin.readDirectory(user, "pronouns")
            
        # Builds the embed
        embed=discord.Embed(color=get(user.guild.roles, id=active_roles["id"]).color, title=user.name + nickname)
        embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["join_date"], value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
        embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["language"], value=language_pref, inline=True)
        embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["pronouns"], value=pronoun_role, inline=True)
        embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["current_rank"], value=get(user.guild.roles, id=active_roles["id"]).mention + ", \"" + active_roles["translation"] + "\"")
        embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["message_count"], value=to_next_level, inline=False)
        embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["server_leaderboard"], value=await buildLeaderboard(ctx, user.id, variant, "position"))
        embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["times_thanked"], value=admin.readDirectory(user, "thanks"))
        embed.set_footer(text=config.text_file[language_pref]["profile"]["embed"]["footer"])
        embed.set_thumbnail(url=user.avatar_url) 
        
        return embed
    
    # Time start
    t1 = time.time()
    
    # Pulls necessary information from the user profile
    message_count = admin.readDirectory(user, "message count")
    language_pref = admin.readDirectory(user, "language")
    active_roles = admin.readDirectory(user, "rank")
    
    # Retrieves the current and next rank from Discord
    current_rank = get(ctx.guild.roles, id=active_roles["id"])
    next_rank_index = config.activeRoleIDs.index(current_rank.id) - 1
    next_rank = get(ctx.guild.roles, id=config.activeRoleIDs[next_rank_index])
    for entry in config.activeRoleDict:
        if entry[0] == next_rank.id:
            next_rank_translation = entry[1]
            break
    
    # Checks the total messages sent against the threshold.
    for i, count in enumerate(config.activeRoleThresholds):
        if message_count >= count and i == 0:
            toNextLevel = 0
            break
        elif message_count >= count:
            toNextLevel = config.activeRoleThresholds[i - 1] - int(message_count)
            break
        elif message_count <= 8:
            toNextLevel = 8 - int(message_count)
            break
    
    output2 = str(toNextLevel)
        
    # Checks the command arguments for updated language preference
    # No update
    if preference == "":
        preference = language_pref
        if preference == "Na'vi":
            str_message_count = wordify(str(oct(message_count))[2:]).capitalize()
            output2 = wordify(str(oct(toNextLevel))[2:])
        elif preference == "English":
            str_message_count = str(message_count)
            
        if toNextLevel < 0:
            to_next_level = config.text_file[language_pref]["profile"]["max_rank"].format(str_message_count)
        else:
            to_next_level = config.text_file[language_pref]["profile"]["rank_progress"].format(str_message_count, output2, next_rank.mention, next_rank_translation)
        
        embed = await buildEmbed(user, language_pref, to_next_level, active_roles)
    # Update
    elif user.id == ctx.message.author.id:
        if preference.capitalize() == "Na'vi":
            str_message_count = wordify(str(oct(message_count))[2:]).capitalize()
            output2 = wordify(str(oct(toNextLevel))[2:])
        elif preference.capitalize() == "English":
            str_message_count = str(message_count)
        else:
            await ctx.send(embed=discord.Embed(description=config.text_file[language_pref]["errors"]["profile"] + config.text_file[language_pref]["errors"]["profile_errors"]["invalid_language"], color=config.failColor))
            return
        
        language_pref = preference.capitalize()
        admin.writeDirectory(user, "language", language_pref)

        if toNextLevel < 0:
            to_next_level = config.text_file[language_pref]["profile"]["max_rank"].format(str_message_count)
        else:
            to_next_level = config.text_file[language_pref]["profile"]["rank_progress"].format(str_message_count, output2, next_rank.mention, next_rank_translation)
        
        embed = await buildEmbed(user, language_pref, to_next_level, active_roles)
    # Invalid entry
    else:
        embed=discord.Embed(description=config.text_file[language_pref]["errors"]["profile"] + config.text_file[language_pref]["errors"]["profile_errors"]["missing_perms"], color=config.failColor)
    
    # Time stop
    t2 = time.time()
    
    # Calculates execution time
    tDelta = round(t2 - t1, 3)
    
    # Checks debug state and sends final embed.
    if config.debug == True:
        embed.set_footer(text="Executed in " + str(tDelta) + " seconds.")
    await ctx.send(embed=embed)

## Retrieve the next Available Date for a Question of the Day
@kelutralBot.command(name='nextday', aliases=['hayasrr'])
async def nextDay(ctx):
    user = ctx.message.author
    
    profile = admin.readDirectory(user)
    langCheck = profile['language']
    
    answer = nextAvailableDate()
    
    for role in config.allowedRoles:
        if user.top_role.id == role:
            if langCheck == "English":
                embed=discord.Embed(description="The next day that a QOTD can be created for is " + answer + ".", colour=config.successColor) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description="Haya trr a fkol tsun ngivop tìpawmit lu " + answer + ".", colour=config.successColor)
                
            await ctx.send(embed=embed)
            
        return

## Thank the Bot
@kelutralBot.command(name="thanks", aliases=['irayo'])
async def thanks(ctx):
    language = admin.readDirectory(ctx.message.author, "language")
    await ctx.send(config.text_file[language]["thanks"].format(ctx.message.author.mention))
        
## Help Command
@kelutralBot.command(name="help", aliases=['srung'])
async def help(ctx, *query):
    lepChannel = kelutralBot.get_channel(config.lepChannel)
    guild = lepChannel.guild
    t1 = time.time()
    
    reykcommands = [('**run**','Translates a Na\'vi word into English.\n'),
                    ('**find**','Finds words whose English definitions contain the query.\n'),
                    ('**tslam**','Runs a grammar analyzer on your sentence.\n',)]
                    
    if len(query) > 1:
        await ctx.send(embed=config.syntax)
        return
    elif len(query) == 0:
        query = ""
    else:
        query = query[0].strip("*")
    
    if len(query) > 0:
        try:
            command = config.helpFile[query]
            embed = discord.Embed(title=command['name'], description="Aliases: {}\nUsage: {}\nExample: {}\nDescription: {}".format(''.join(command['aliases']), command['usage'], command['example'], command['description']))
        except KeyError:
            embed = config.helpError
            await ctx.send(embed=embed)
            return
        
    else:
        output = ""
        
        # Eytukan's command list
        for entry in config.helpFile.values():
            output = output + entry['name'] + ": " + entry['short']
        
        # Reykunyu's command list
        output = output + "\n\nHere are {}'s available commands. Use `!run help` for additional support for Reykunyu's commands.\n\n".format(guild.get_member(config.reykID).mention)
        
        for command in reykcommands:
            output = output + command[0] + ": " + command[1]
        
        embed = discord.Embed(title="!help",description="Here are {}'s available commands. Use `!help <command>` for more information about that command.\n\n".format(guild.get_member(config.botID).mention) + output)
        embed.set_thumbnail(url=guild.icon_url)
    
    t2 = time.time()
    tDelta = round(t2 - t1, 3)
    
    if config.debug:
        embed.set_footer(text="Executed in " + str(tDelta) + " seconds.")
        
    await ctx.send(embed=embed)
         
## Quiz Command
@kelutralBot.command(name="quiz",aliases=['fmetok'])
async def quiz(ctx, *args):
    iteration = 0
    needStudy = []
    
    if len(args) > 2:
        await ctx.send(embed=config.arguments)
        return
    elif len(args) == 2:
        for test in args:
            try:
                val = int(test)
                rounds = val
            except ValueError:
                lang = test
    elif len(args) == 1:
        for test in args:
            try:
                val = int(test)
                rounds = val
                lang = "English"
            except ValueError:
                lang = test
                rounds = 1
    else:
        lang = "English"
        rounds = 1
    
    if rounds > 10 or rounds < 1:
        await ctx.send(embed=config.syntax)
    else:
        correct = 0
        incorrect = 0
        while iteration < abs(int(rounds)):
            i = 0
            allDefinitions = []

            fileLen = len(config.words)
            correctEntry = random.randint(1,fileLen)
            selectedEntry = config.words[correctEntry]
            
            if lang.lower() == "english":
                nv = selectedEntry[0]
                correctDef = selectedEntry[1]
                
                embed=discord.Embed(title="Na'vi to English: " + nv, description="React with the appropriate letter to submit your answer for the correct definition.", color=config.quizColor)
                
                while i < 3:
                    index = random.randint(1,fileLen)
                    if index == correctEntry:
                        while index == correctEntry:
                            index = random.randint(1,fileLen)
                    else:
                        randomDef = config.words[index]
                        randomDef = randomDef[1]
                        allDefinitions.append(randomDef)
                        i += 1
                        
            elif lang.lower() == "na'vi":
                nv = selectedEntry[1]
                correctDef = selectedEntry[0]

                embed=discord.Embed(title="English to Na'vi: " + nv, description="React with the appropriate letter to submit your answer for the Na'vi counterpart.", color=config.quizColor)
                
                while i < 3:
                    index = random.randint(1,fileLen)
                    if index == correctEntry:
                        while index == correctEntry:
                            index = random.randint(1,fileLen)
                    else:
                        randomDef = config.words[index]
                        randomDef = randomDef[0]
                        allDefinitions.append(randomDef)
                        i += 1

            else:
                value = "{}".format("**Error: Invalid language** \n Please use `English` or `Na'vi`.")
                embed = discord.Embed(description=value, color=config.failColor)
                await ctx.send(embed=embed)
                return
            
            allDefinitions.append(correctDef)
            
            random.shuffle(allDefinitions)
            
            message = await ctx.send(embed=embed)
            
            emojis = ['\U0001F1E6','\U0001F1E7','\U0001F1E8','\U0001F1E9']
            for emoji in emojis:
                await message.add_reaction(emoji)
            
            alphabet = ['A', 'B', 'C', 'D']
            for i, letter in enumerate(alphabet):
                embed.add_field(name="Definition {}".format(letter), value=allDefinitions[i],inline=False)
            await message.edit(embed=embed)
                
            def check(reaction, user):
                for emoji in emojis:
                    if str(reaction.emoji) == emoji:
                        foundEmoji = True
                        break
                    else:
                        foundEmoji = False

                return user == ctx.message.author and foundEmoji
            
            try:
                reaction, user = await kelutralBot.wait_for('reaction_add', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                embed=discord.Embed(title="Word: " + nv, description="Sorry, you took too long to answer! The correct answer was " + nv + ", **" + correctDef + "**. Try again!", color=config.failColor)
                needStudy.append("**" + nv + "**, *" + correctDef + "*\n")
                
                await message.clear_reactions()
                await message.edit(embed=embed)
            else:
                i = 0
                while i < 4:
                    if str(reaction) == emojis[i]:
                        v = 0
                        for emoji in emojis:
                            if emojis[v] == str(reaction):
                                response = v
                            else:
                                v += 1

                        
                        if allDefinitions[v] == correctDef:
                            if ctx.message.guild:
                                await message.clear_reactions()
                            embed=discord.Embed(title="Word: " + nv, description="Congratulations ma " + str(ctx.message.author.mention)+ ", you were correct!", color=config.successColor)
                            embed.add_field(name="Definition " + alphabet[v], value=correctDef,inline=False)
                            await message.edit(embed=embed)
                            
                            correct += 1
                        else:
                            if ctx.message.guild:
                                await message.clear_reactions()
                            embed=discord.Embed(title="Word: " + nv, description="Sorry ma " + str(ctx.message.author.mention)+ ", the correct answer was **" + correctDef + "**. Your answer was: ", color=config.failColor)
                            embed.add_field(name="Definition " + alphabet[v], value=allDefinitions[v],inline=False)
                            await message.edit(embed=embed)
                            
                            incorrect += 1
                            needStudy.append("**" + nv + "**, *" + correctDef + "*\n")
                        break
                    else:
                        i += 1
            iteration += 1

        if correct == 0:
            embed = discord.Embed(title="Results", description="You got " + str(correct) + " out of " + str(rounds) + " correct, try again! \n\n Here are the words you need to work on:")
            for i in needStudy:
                embed.add_field(name="Word:", value=i)
        elif correct == rounds:
            embed = discord.Embed(title="Results", description="Nice work! You got " + str(correct) + " out of " + str(rounds) + " correct!")
        else:
            embed = discord.Embed(title="Results", description="You got " + str(correct) + " out of " + str(rounds) + " correct, not bad! \n\n Here are the words you need to work on:")
            for i in needStudy:
                embed.add_field(name="Word:", value=i)
        await ctx.send(embed=embed)

## 8 Ball Command
@kelutralBot.command(name="8ball")
async def eightBall(ctx, *args):
    user = ctx.message.author
    question = " ".join(args)
    
    index = random.randint(0,11)
    options = config.text_file[admin.readDirectory(user, "language")]["8ball"]["options"]
    embed = discord.Embed(description=config.text_file[admin.readDirectory(user, "language")]["8ball"]["response"].format(user.mention, question, config.text_file[admin.readDirectory(user, "language")]["8ball"]["options"][index]))
    
    await ctx.send(embed=embed)

## LEP Command
@kelutralBot.command(name="lep")
async def lepCommand(ctx, *args):
    user = ctx.message.author.id
    msg_channel = kelutralBot.get_channel(715988382706303038)
    modLog_channel = kelutralBot.get_channel(config.modLog)
    
    if isinstance(ctx.channel, discord.DMChannel):
        message = " ".join(args)
        for i, value in enumerate(config.lepArchive):
            if config.lepArchive[i][0] == user:
                randColor = config.lepArchive[i][1]
        
        try:
            randColor
        except NameError:
            randColor = random.randint(0,0xffffff)
            config.lepArchive.append([user,randColor])
        
        embed = discord.Embed(description=ctx.message.author.name + " sent the following message to the LEP Channel: \n\n" + message)
        await modLog_channel.send(embed=embed)
        
        embed = discord.Embed(title="Anonymous LEP Submission",description=message,color=randColor)
        await msg_channel.send(embed=embed)
        await ctx.send(embed=config.success)
    else:
        message = ctx.message
        await ctx.send(embed=config.dm_only)
        await message.delete()

##-----------------------Error Handling-------------------##
# Error Handling for !generate
@generate.error
async def generate_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(embed=config.syntax)

# Error Handling for !profile
@profile.error
async def profile_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(embed=config.syntax)
        
# Error Handling for !quiz
@quiz.error
async def quiz_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(embed=config.syntax)

# Error Handling for !help
@help.error
async def help_error(ctx, error):
   if isinstance(error, commands.CommandError):
       await ctx.send(embed=config.syntax)

# Replace token with your bot's token
kelutralBot.run(config.token)
