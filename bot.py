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
import glob

import json

import config
import admin
import namegen # namegen.py update courtesy of Yayayr
import watcher
import feedparser

## -- Initialize Client
kelutral = discord.Client()

## -- Initialize Bot
intents = discord.Intents.default()
intents.members = True
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

## -- RSS Feed Troller
async def rssfeedreader():
    feedurl_1 = "http://naviteri.org/feed/"
    feedurl_2 = "https://www.kelutral.org/2/feed"
    previousfeed_1 = feedparser.parse(feedurl_1)
    previousfeed_2 = feedparser.parse(feedurl_2)
    currentfeed_1 = feedparser.parse(feedurl_1)
    if currentfeed_1.entries[0].title != previousfeed_1.entries[0].title:
        channel = kelutralBot.get_channel(715049263842721792)
        await channel.send("New Post: " + currentfeed_1.entries[0].title+"\n"+currentfeed_1.entries[0].link)
        previousfeed_1 = currentfeed_1
    currentfeed_2 = feedparser.parse(feedurl_2)
    if currentfeed_2.entries[0].title != previousfeed_2.entries[0].title:
        channel = kelutralBot.get_channel(715049263842721792)
        await channel.send("New Post: " + currentfeed_2.entries[0].title+"\n"+currentfeed_2.entries[0].link)
        previousfeed_2 = currentfeed_2
    
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
                             "One moment please\n*checks the report*\n*turns a few pages*\nOK, so the answer is no."]
                index = random.randint(0,len(responses)-1)
                print(now + " -- Sending Tweet to @avatarsequels")
                api.update_status(responses[index])
                time = 120
        else:
            time = 60
            
        await asyncio.sleep(time)

## -- English - Na'vi numberical conversion courtesy of Tirea Aean.
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
    dateTimeObj = datetime.now()
    tomorrow = datetime.today() + timedelta(days=1)
    nextDay = tomorrow.strftime("%d-%m-%Y")
    fileName = 'files/qotd/' + str(nextDay) + '.tsk'
    
    while os.path.exists(fileName) == True: # Iterates through the directory to find the first file that doesn't exist. That file is the next available date.
        tomorrow = tomorrow + timedelta(days=1)
        nextDay = tomorrow.strftime("%d-%m-%Y")
        fileName = 'files/qotd/' + str(nextDay) + '.tsk'
    return nextDay

## -- Reads the necessary files and builds the output for the Leaderboard command.
def buildLeaderboard(ctx, profile, variant):
    messageCounts = []
    userNames = []
    search_user = ctx.message.guild.get_member(profile[0])
    t1 = time.time()
    
    ## -- Builds the Current Leaderboard
    for entry in config.directory:
        profile = entry
        currentMember = ctx.message.guild.get_member(profile[0])
        
        if currentMember == None: # If member has left the server, builds a dummy user object.
            user = type('user', (), {})()
            user.id = profile[0]
            user.nick = None
            user.name = profile[2]
            userNames.append(profile[2].encode('unicode-escape').decode('utf-8'))
            user = ""
        elif currentMember.nick == None:
            userNames.append(str(currentMember.name))
            user = ""
        else:
            userNames.append(str(currentMember.nick))
            user = ""
        
        ## -- Checks the variant of leaderboard to build.
        if variant.lower() == "messages":
            messageCounts.append(int(profile[1]))
        elif variant.lower() == "thanks":
            try:
                messageCounts.append(int(profile[7]))
            except:
                messageCounts.append(0)
        
    sortedUserNames = [x for _,x in sorted(zip(messageCounts, userNames))]
    sortedMessageCounts = sorted(messageCounts)
    sortedUserNames.reverse()
    sortedMessageCounts.reverse()

    ## -- Indexes by the user who is being searched, command author for !leaderboard and requested profile for !profile
    if search_user.nick == None:
        pos = sortedUserNames.index(search_user.name) + 1
    else:
        pos = sortedUserNames.index(search_user.nick) + 1
        
    t2 = time.time()
    tDelta = round(t2 - t1, 3)

    return sortedUserNames, sortedMessageCounts, pos, tDelta
    
## -- Clear screen function
def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')
    
##-----------------------Bot Events-----------------------##
##--------------------Uses Watcher.py---------------------##

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
async def on_reaction_add(reaction, user):
    emoji = ['<:irayo:715054886714343455>'] 
    fileName = 'files/config/reactions.txt'
    
    if reaction.message.author.id == user.id: # If reaction was added by the message author (sneaky sneaky!)
        return
    else:
        with open(fileName, 'r') as fh:
            contents = json.load(fh)
        
        if str(reaction.emoji) in emoji: # Checks to see if the reaction adder has already added a reaction to that message (prevents duplication)
            check = [reaction.message.id, user.id]
            if check not in contents:
                contents.append([reaction.message.id, user.id])
                
                for entry in config.directory: # Iterates the user directory to find the reaction adder
                    if reaction.message.author.id == entry[0]:
                        try: # Tries to pull the thanks data from the user profile
                            timesThanked = entry[6]
                            break
                        except IndexError: # If no thanks data exists, appends a blank field
                            timesThanked = 0
                            entry.append(timesThanked)
                entry[6] += 1
                
                with open(fileName, 'w') as fh:
                    json.dump(contents, fh)
        
        ## -- Updates the directory
        with open(config.directoryFile, 'w', encoding='utf-8') as fh:
            json.dump(config.directory, fh)
            
        config.directory = config.reloadDir()
            
##                                            profile index cheatsheet
## [user.id, message count, user.name, output language, pronoun id, [current rank id, translation], thanks recieved]
## {   0   ,       1      ,     2    ,        3       ,     4     ,              5                ,        6       ]

##-----------------------Bot Functions--------------------##
## 
@kelutralBot.command(name='fix')
async def fixDirectory(ctx):
    user = ctx.message.author
    # Retrieves the user profile
    profile = admin.getProfile(user)
    
    # Unpacks the relevant parts of the user profile
    language_pref = profile[3]
    current_rank = get(user.guild.roles, id=profile[5][0])
    next_rank_index = config.activeRoleIDs.index(current_rank.id) - 1
    next_rank = get(user.guild.roles, id=config.activeRoleIDs[next_rank_index])
    
    print(current_rank.name)
    print(next_rank.name)
            
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

## Add a Question of the Day to a specified or the next available date
@kelutralBot.command(name='addqotd', aliases=['tìpawm'])
async def qotd(ctx, question, *date):
    user = ctx.message.author
    profile = admin.getProfile(user)
    langCheck = profile[3]
    t1 = time.time()
    
    if user.top_role.id in config.allowedSet: # If the user is allowed to use this command
        if date: # If a date is specified
            date = str(date).strip("(),' ")
            fileName = config.qotdFile.format(str(date))
        else: # If the date field is left blank
            date = nextAvailableDate()
            fileName = config.qotdFile.format(str(date))
                
        if not os.path.exists(fileName):       
            with open(fileName, "w") as fh:
                fh.write(str(question))

            now = datetime.strftime(datetime.now(),'%H:%M')
            print(now + " -- Created question of the day for " + str(date) + ".")
            
            with open(config.calendarFile, 'a') as fh:
                fh.write("\n" + str(date))
            
            if langCheck == "English":
                embed=discord.Embed(description='Created.', colour=config.successColor) 
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Ngolop.', colour=config.successColor) 
            
        else: # If a QOTD already exists for that date
            modDate = nextAvailableDate()
            
            if langCheck == "English":
                embed=discord.Embed(description="A QOTD for this day already exists. The next available day to create a QOTD is " + modDate + ".", colour=config.failColor)
            elif langCheck == "Na'vi":
                embed=discord.Embed(description="Fìtìpawm mi fkeytok! Haya trr a fkol tsun ngivop tìpawmit lu " + modDate + ".", colour=config.failColor)
        
        t2 = time.time()
        tDelta = round(t2 - t1, 3)
        
        if config.debug == True:
            embed.set_footer(text="Executed in " + str(tDelta) + " seconds.")

        await ctx.send(embed=embed)

## Ban Command
@kelutralBot.command(name='ban', aliases=['yitx'])
async def ban(ctx, user: discord.Member):
    if user.top_role.id in config.modSet: # If the user is allowed to use this command
        await user.ban()
        embed=discord.Embed(description=str(user.mention) + "** was banned**", colour=config.failColor)
        await ctx.send(embed=embed)

## Delete a specific Question of the Day
@kelutralBot.command(name='deleteqotd', aliases=['ska\'a'])
async def deleteQuestion(ctx, date):
    user = ctx.message.author
    fileName = config.qotdFile.format(str(date))
    profile = admin.getProfile(user)
    langCheck = profile[3]
    t1 = time.time()
    
    if user.top_role.id in config.allowedSet:
        if os.path.exists(fileName):
            os.remove(fileName)
            
            with open(config.calendarFile,'r') as fh:
                fileContents = fh.read()
            
            removeDate = fileContents.replace("\n" + str(date),'')
            
            with open(config.calendarFile,'w') as fh:
                fh.write(removeDate)

            if langCheck == "English":
                embed=discord.Embed(description='Removed.', colour=config.successColor) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Olaku\'.', colour=config.successColor)
                
        else:
            if langCheck == "English":
                embed=discord.Embed(description='No QOTD exists on that day.', colour=config.failColor) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Kea tìpawm mi ke fkeytok mì satrr.', colour=config.failColor)
        
        t2 = time.time()
        tDelta = round(t2 - t1, 3)
        
        if config.debug == True:
            embed.set_footer(text="Executed in " + str(tDelta) + " seconds.")
        
        await ctx.send(embed=embed)
        return

## Update Rules
@kelutralBot.command(name='donotuse')
async def updateRules(ctx):
    user = ctx.message.author
    if user.top_role.id == config.adminID:
        await admin.adminMsgs(ctx, kelutralBot)

## Change a specific Question of the Day
@kelutralBot.command(name='editqotd', aliases=['latem'])
async def changeQuestion(ctx, question, date):
    user = ctx.message.author
    fileName = config.qotdFile.format(str(date))
    profile = admin.getProfile(user)
    langCheck = profile[3]
    t1 = time.time()
    
    if user.top_role.id in config.allowedSet:
        if os.path.exists(fileName):
            with open(fileName, 'w') as fh:
                fh.write(question)
            
            if langCheck == "English":
                embed=discord.Embed(description='Edited.', colour=config.successColor) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Lolatem.', colour=config.successColor)
            
        else:

            if langCheck == "English":
                embed=discord.Embed(description='No QOTD exists on that day.', colour=config.failColor) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Kea tìpawm mi ke fkeytok mì satrr.', colour=config.failColor)
        
        t2 = time.time()
        tDelta = round(t2 - t1, 3)
        
        if config.debug == True:
            embed.set_footer(text="Executed in " + str(tDelta) + " seconds.")
            
        await ctx.send(embed=embed)

## FAQ Command
@kelutralBot.command(name="faq",aliases=['sìpawm'])
async def faq(ctx, *topic):
    user = ctx.message.author
    topic = ' '.join(topic)
    topics = ['**beginner**','- \'efu','- lu','- tok','- with','**case**','- agent','- patient','- dative','- topic','**howto**','- pronounce','- start','**hrh**']
    
    if user.top_role.id in config.allowedSet:
        if topic == 'beginner \'efu':
            await ctx.send(embed=config.lu_efu)
        elif topic == 'beginner tok':
            await ctx.send(embed=config.lu_tok)
        elif topic == 'beginner lu':
            await ctx.send(embed=config.lu_verb)
        elif topic == 'beginner with':
            await ctx.send(embed=config.hu_fa)
        elif topic == 'case agent':
            await ctx.send(embed=config.agent)
        elif topic == 'case patient':
            await ctx.send(embed=config.patient)
        elif topic == 'case dative':
            await ctx.send(embed=config.dative)
        elif topic == 'case topic':
            await ctx.send(embed=config.topic)
        elif topic == 'hrh':
            await ctx.send(embed=config.hrh)
        elif topic == 'howto pronounce':
            await ctx.send(embed=config.pronounce)
        elif topic == 'howto start':
            await ctx.send(embed=config.start)
        elif topic == "":
            output = "Headers with sub-topics are marked in **bold**\n\n"
            for value in topics:
                output = output + value + "\n"
            embed = discord.Embed(title="Available FAQ topics:", description=output, color=config.reportColor)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=config.faqError)

## Generate # of random names
@kelutralBot.command(name="generate",aliases=['ngop'])
async def generate(ctx, numOut, numSyllables):
    n = int(numOut)
    i = int(numSyllables)
    output = []
    c = 0
    profile = admin.getProfile(ctx.message.author)
    langCheck = profile[3]
    
    if not n <= 0 and not i <= 0:
        if langCheck == "English":
            if not i <= 5:
                embed=discord.Embed(description="**Error: Value Error** \n Maximum syllable count allowed by the bot is 5. It is highly recommended that you select a name between 1 and 3 syllables in length.", colour=config.failColor) 
                await ctx.send(embed=embed)
                
            elif not n <= 20:
                embed=discord.Embed(description="**Error: Value Error** \n Maximum name count is 20.", colour=config.failColor) 
                await ctx.send(embed=embed)
                
            else:
                nameCount = update(n)
                game = discord.Game("ngamop " + "{:,}".format(nameCount) + " tstxoti.")
        
                await kelutralBot.change_presence(status=discord.Status.online, activity=game)

                embed=discord.Embed(color=config.successColor)
                embed.set_author(name="Here are your names:")
                while c < n:
                    output.append(namegen.nameGen(numSyllables))
                    embed.add_field(name="Name " + str(c + 1) + ":", value=output[c], inline=True)
                    c += 1
                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                
                await ctx.send(embed=embed)
                
        elif langCheck == "Na'vi":
            if not i <= 5:
                await ctx.send()
                embed=discord.Embed(description="**Error: Value Error** \n Lì'kongä txantewä holpxay lu mrr. Sweylu txo ngal ftxivey tstxoti a lu tsa'ur lì'kong apxey, lì'kong amune, fu lìkong a'aw.", colour=config.failColor) 
                await ctx.send(embed=embed)
                
            elif not n <= 20:
                await ctx.send()
                embed=discord.Embed(description="**Error: Value Error** \n Stxoä txantxewä holpxay lu mevotsìng.", colour=config.failColor) 
                await ctx.send(embed=embed)
                
            else:
                nameCount = update(n)
                game = discord.Game("ngamop " + "{:,}".format(nameCount) + " tstxoti.")
        
                await kelutralBot.change_presence(status=discord.Status.online, activity=game)
                
                embed=discord.Embed(color=config.successColor)
                embed.set_author(name="Faystxo lu ngaru ma " + ctx.message.author.name + ":")
                while c < n:
                    output.append(namegen.nameGen(numSyllables))
                    embed.add_field(name="Tstxo "+ str(c + 1) + ":", value=output[c], inline=True)
                    c += 1
                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                
                await ctx.send(embed=embed)

    else:
        if langCheck == "English":
            await ctx.send(embed=config.syntax)
            
        elif langCheck == "Na'vi":
            embed=discord.Embed(description="**Error: Value Error** \n Rutxe sar holpxayti a to kew lu apxa. Txo kivin srungti ngal, `!help generate`ri pamrel si nga.", color=config.failColor)
            await ctx.send(embed=embed)
    
    now = datetime.strftime(datetime.now(),'%H:%M')
    print(now + " -- " + ctx.author.name + " generated " + str(n) + " names.")

## Kill Command
@kelutralBot.command(name='quit', aliases=['ftang'])
async def botquit(ctx):
    user = ctx.message.author

    if user.top_role.id == config.adminID:
        embed=discord.Embed(description="Shutting down...", colour=config.failColor)
        await ctx.send(embed=embed)
        await kelutralBot.close()
        await kelutralBot.close()
        quit()
    else:
        await ctx.send(embed=config.denied)

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

## Display Server Leaderboard
@kelutralBot.command(name='leaderboard')
async def leaderboard(ctx, variant):
    i = 0
    
    profile = admin.getProfile(ctx.message.author)
    
    if variant.lower() == "messages" or variant.lower() == "thanks":
        sortedUserNames, sortedMessageCounts, pos, tDelta = buildLeaderboard(ctx, profile, variant)
    else:
        await ctx.send(embed=config.syntax)
        return
 
    value = ""
    while i <= 9:
        value = value + "**" + sortedUserNames[i] + "**\n" + str(sortedMessageCounts[i]) + " messages  |  Rank: #" + str(i + 1) + "\n\n"
        i += 1
    embed=discord.Embed(title="Server Leaderboard:", description=value, color=config.reportColor)
    
    if config.debug == True:
        embed.set_footer(text="You are ranked #" + str(pos) + " overall.  |  Executed in " + str(tDelta) + " seconds.")
    else:
        embed.set_footer(text="You are ranked #" + str(pos) + " overall.")
        
    await ctx.send(embed=embed)
    
## Display User Message Count
@kelutralBot.command(name='profile', aliases=['yì'])
async def profile(ctx, user: discord.Member, *setting):
    setting = ''.join(setting)
    preference = str(setting).lower()
    variant = "messages"
    
    # Gets the specified profile
    profile = admin.getProfile(user)

    # Unpacks the profile
    message_count = profile[1]
    user_name = profile[2]
    language_pref = profile[3]
    if type(profile[4]) == str:
        pronouns = profile[4]
    elif type(profile[4]) == int:
        pronouns = get(ctx.guild.roles, id=profile[4]).name
    active_roles = profile[5]
    thanks_count = profile[6]
    
    # Retrieves the current and next rank
    current_rank = get(ctx.guild.roles, id=profile[5][0])
    next_rank_index = config.activeRoleIDs.index(current_rank.id) - 1
    next_rank = get(ctx.guild.roles, id=config.activeRoleIDs[next_rank_index])
    for entry in config.activeRoleDict:
        if entry[0] == next_rank.id:
            next_rank_translation = entry[1]
            break
    
    sortedUserNames, sortedMessageCounts, pos, tDelta = buildLeaderboard(ctx, profile, variant)
    t1 = time.time()
    
    def buildEmbed(ctx, profile, message_count, pos):
        user = ctx.guild.get_member(profile[0])
        try:
            nickname = " AKA \"" + user.nick + "\""
        except:
            nickname = ""
        embed=discord.Embed(color=user.color, title=user.name + nickname)
        embed.add_field(name=text[0], value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
        embed.add_field(name=text[1], value=language_pref, inline=True)
        embed.add_field(name=text[2], value=pronouns, inline=True)
        embed.add_field(name=text[3], value=get(ctx.guild.roles, id=active_roles[0]).mention + ", \"" + active_roles[1] + "\"")
        embed.add_field(name=text[4], value=message_count, inline=False)
        embed.add_field(name=text[5], value=pos)
        embed.add_field(name=text[7], value=thanks_count)
        embed.set_footer(text=text[6])
        embed.set_thumbnail(url=user.avatar_url) 
        
        return embed
    
    ## -- Checks the total messages sent against the threshold.
    i = 0
    for role in config.activeRoleThresholds:
        if message_count >= config.activeRoleThresholds[i]:
            toNextLevel = config.activeRoleThresholds[i - 1] - int(message_count)
            break
        elif message_count <= 16:
            toNextLevel = 16 - int(message_count)
            break
        i += 1

    if i == 0:
        i = -1
    
    output2 = str(toNextLevel)
        
    ## -- Updates the user profile and sends.
    if preference == "":
        preference = language_pref
        if preference == "Na'vi":
            output1 = wordify(str(oct(message_count))[2:])
            output2 = wordify(str(oct(toNextLevel))[2:])
            
            if toNextLevel < 0:
                line5 = "'Upxare aketsuktiam."
            else:
                line5 = output1.capitalize() + " 'upxare. Kin pol **" + output2 + " 'upxareti** fte slivu " + next_rank.mention
            text = config.nvText
            embed = buildEmbed(ctx, profile, line5, pos)
            
        elif preference == "English":
            if toNextLevel < 0:
                line5 = str(message_count) + " messages."
            else:
                line5 = str(message_count) + " messages. They need **" + output2 + " more messages** in order to reach " + next_rank.mention + " (" + next_rank_translation + ")"
            text = config.enText
            embed = buildEmbed(ctx, profile, line5, pos)

    elif user.id == ctx.message.author.id:
        if preference == "na'vi":
            profile[3] = "Na'vi"
            output1 = wordify(str(oct(message_count))[2:])
            output2 = wordify(str(oct(toNextLevel))[2:])

            if toNextLevel < 0:
                line5 = "'Upxare aketsuktiam."
            else:
                line5 = output1.capitalize() + " 'upxare. Kin pol **" + output2 + " 'upxareti** fte slivu " + next_rank.mention
            text = config.nvText
            embed = buildEmbed(ctx, profile, line5, pos)
        elif preference == "english":
            profile[3] = "English"
            
            if toNextLevel < 0:
                line5 = str(message_count) + " messages."
            else:
                line5 = str(message_count) + " messages. They need **" + output2 + " more messages** in order to reach " + next_rank.mention + " (" + next_rank_translation + ")"
            text = config.enText
            embed = buildEmbed(ctx, profile, line5, pos)
        else:
            embed=discord.Embed(description="**Error: Invalid criteria entered.** \n Please select `English` or `Na'vi` to update your current settings.", color=config.failColor)
    else:
        embed=discord.Embed(description="**Error: Denied** \n You can only change your own output settings.", color=config.failColor)

    with open(config.directoryFile, 'w', encoding='utf-8') as fh:
        json.dump(config.directory, fh)
        
    config.directory = config.reloadDir()
    
    t2 = time.time()
    tDelta = round(t2 - t1, 3)
    if config.debug == True:
        embed.set_footer(text="Executed in " + str(tDelta) + " seconds.")
        
    await ctx.send(embed=embed)

## Retrieve the next Available Date for a Question of the Day
@kelutralBot.command(name='nextday', aliases=['hayasrr'])
async def nextDay(ctx):
    user = ctx.message.author
    
    profile = admin.getProfile(user)
    langCheck = profile[3]
    
    answer = nextAvailableDate()
    
    for role in config.allowedRoles:
        if user.top_role.id == role:
            if langCheck == "English":
                embed=discord.Embed(description="The next day that a QOTD can be created for is " + answer + ".", colour=config.successColor) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description="Haya trr a fkol tsun ngivop tìpawmit lu " + answer + ".", colour=config.successColor)
                
            await ctx.send(embed=embed)
            
        return

## Check the Scheduled Dates for Questions of the Day
@kelutralBot.command(name='schedule', aliases=['srr'])
async def checkDates(ctx):
    user = ctx.message.author
    
    profile = admin.getProfile(user)
    langCheck = profile[3]
    
    if user.top_role.id in config.allowedSet:
        dates = []
        questions = []
        if os.path.exists(config.calendarFile) and not os.path.getsize(config.calendarFile) == 10:
            with open(config.calendarFile, 'r') as fh:
                for line in fh:
                    filePath = config.qotdFile.format(line.strip())
                    if os.path.exists(filePath):
                        dates.append(line.strip())
                        with open(filePath, 'r') as fp:
                            questions.append(fp.read())

            if langCheck == "English":
                embed=discord.Embed(description="**Upcoming Questions of the Day:**", color=config.QOTDColor)
            elif langCheck == "Na'vi":
                embed=discord.Embed(description="**Haya srrä sìpawm:**", color=config.QOTDColor)
            i = 0
            while i < len(dates):
                if i <= 20:
                    embed.add_field(name=str(dates[i]), value="\"" + str(questions[i]) + "\"", inline=True)
                    i += 1
                else:
                    break
                
            await ctx.send(embed=embed)
            
        else:
            if langCheck == "English":
                embed=discord.Embed(description='There are no scheduled QOTDs.', colour=config.failColor) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Kea srrur ke lu sìpawm.', colour=config.failColor) 
                
            await ctx.send(embed=embed)

## View a specific Question of the Day
@kelutralBot.command(name='viewqotd', aliases=['inan'])
async def readQuestion(ctx, date):
    user = ctx.message.author
    fileName = config.qotdFile.format(str(date))
    
    profile = admin.getProfile(user)
    langCheck = profile[3]
    
    if user.top_role.id in config.allowedSet:
        if os.path.exists(fileName):
            with open(fileName, 'r') as fh:
                contents = fh.read()
            
            if langCheck == "English":
                embed=discord.Embed(description='That question of the day is \"' + contents + '\"', colour=config.QOTDColor)
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Tsatìpawm lu \"' + contents + '\"', colour=config.QOTDColor)
                
            else:
                await ctx.send("Somehow, and god knows how, you fucked up.")
            
            await ctx.send(embed=embed)
                
        else:

            if langCheck == "English":
                embed=discord.Embed(description='No QOTD exists on that day.', colour=config.failColor) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Kea tìpawm mi ke fkeytok mì satrr.', colour=config.failColor) 
                
            else:
                await ctx.send("Somehow, and god knows how, you fucked up.")
            
            await ctx.send(embed=embed)

## Thank the Bot
@kelutralBot.command(name="thanks", aliases=['irayo'])
async def thanks(ctx):
    user = ctx.message.author
    profile = admin.getProfile(user)
    langCheck = profile[3]
    
    if langCheck == "English":
        await ctx.send("You're welcome, " + str(user.mention))
    elif langCheck == "Na'vi":
        await ctx.send("Tstunwi ma " + str(user.mention))
    else:
        await ctx.send("Whoops!")
        
## Help Command
@kelutralBot.command(name="help", aliases=['srung'])
async def help(ctx, *args):
    lepChannel = ctx.guild.get_channel(config.lepChannel)
    t1 = time.time()
    
    reykcommands = [('**run**','Translates a Na\'vi word into English.\n'),
                    ('**find**','Finds words whose English definitions contain the query.\n'),
                    ('**tslam**','Runs a grammar analyzer on your sentence.\n',)]
                    
    if len(args) > 1:
        await ctx.send(embed=config.syntax)
        return
    elif len(args) == 0:
        arg = ""
    else:
        arg = args[0].strip("*")
    
    if len(arg) > 0:
        for entry in config.helpFile:
            if arg == command[0].strip("*") or arg == command[1]:
                embed = discord.Embed(title="!help " + entry[0], description=config.helpFile[5] + "\n**Aliases:** " + entry[1] + "\n**Usage:** " + entry[3] + "\n**Example:** " + entry[4])
        if embed == None:
            await ctx.send(embed=config.help_error)
            return
    else:
        output = ""
        
        # Eytukan's command list
        for entry in config.helpFile:
            output = output + entry[0] + ": " + entry[2]
        
        # Reykunyu's command list
        output = output + "\n\nHere are {}'s available commands. Use `!run help` for additional support for Reykunyu's commands.\n\n".format(ctx.message.guild.get_member(config.reykID).mention)
        
        for command in reykcommands:
            output = output + command[0] + ": " + command[1]
        
        embed = discord.Embed(title="!help",description="Here are {}'s available commands. Use `!help <command>` for more information about that command.\n\n".format(ctx.message.guild.get_member(config.botID).mention) + output)
        embed.set_thumbnail(url=ctx.guild.icon_url)
    t2 = time.time()
    tDelta = round(t2 - t1, 3)
    
    if config.debug == True:
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
    responses = ["Seems unlikely.","Probably not.","Try again later.","Outlook is favorable.","Yes","No","Unclear","Not on your life.","Definitely","Without a doubt.","Try asking that question a different way.","Skxawng."]
    nvResponses = ["Ke fpìl oe tsafya.", "Skxakep kehe.", "Fmi nìmun.", "Lam tsafya.", "Srane.", "Kehe.", "Ke lu law.", "Sto oe 'iveyng.", "Kezemplltxe.", "Am'ake.", "Pawm tsat nìfya'o alahe.", "Skxawng."]
    question = " ".join(args)
    
    profile = admin.getProfile(ctx.message.author)
    langCheck = profile[3]
    
    if langCheck == "English":
        index = random.randint(0,len(responses)-1)
        embed = discord.Embed(description=ctx.message.author.mention + " says: \"**" + question + "**\"\n\n" + "Eytukan says: \"" + responses[index] + "\"")
        
    elif langCheck == "Na'vi":
        index = random.randint(0,len(nvResponses)-1)
        embed = discord.Embed(description=ctx.message.author.mention + " says: \"**" + question + "**\"\n\n" + "Eytukan says: \"" + nvResponses[index] + "\"")
    
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
            randColor = random.randint(0, 0xffffff)
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
