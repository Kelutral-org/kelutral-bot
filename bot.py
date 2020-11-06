# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands

import asyncio
import random
import time
import os
import json
import re
from datetime import datetime
from datetime import timedelta

import config
import admin
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
    def update(newNameCount):
        fileName = config.botFile
        if os.path.exists(fileName): # If bot file exists
            with open(fileName, 'r') as fh:
                nameCount = json.load(fh)
            
            nameCount[0] = nameCount[0] + newNameCount
            
            with open(fileName, 'w') as fh:
                json.dump(nameCount, fh)
            
        return nameCount[0]
        
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

##------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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

## LEP Command
@kelutralBot.command(name="lep")
async def lepCommand(ctx, *args):
    user = ctx.message.author.id
    msg_channel = kelutralBot.get_channel(config.lepChannel)
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
        
@kelutralBot.command(name="type")
async def typeWord(ctx, *words):
    list_words = []
    for i, word in enumerate(words):
        if word == 'si':
            list_words[i-1] += " {}".format(word)
        else:
            list_words.append(word)
    
    output_list = []
    mod = ""
    output = ""
    cases = {
        "agentive" : ["l\Z","ìl\Z"],
        "patientive" : ["t\Z","ti\Z","it\Z"],
        "dative" : ["r\Z","ur\Z","ru\Z"],
        "genitive" : ["ä\Z","yä\Z"],
        "topical" : ["ri\Z","ìri\Z"]
        }
    
    infixes = [{"general past" : 'am'},{"near past" : 'ìm'},{"general future" : 'ay'},{"near future" : 'ìy'},{"general future intent" : 'asy'},{"near future intent" : 'ìsy'},{"general past perfective" : 'alm'},{"near past perfective" : 'ìlm'},{"general future perfective" : 'aly'},{"near future perfective" : 'ìly'},{"general past progressive" : 'arm'},{"near past progressive" : 'ìrm'},{"general future progressive" : 'ary'},{"near future progressive" : 'ìry'},{"positive mood" : 'ei'},{"negative mood" : 'äng'},{"perfective" : 'ol'},{"progressive" : 'er'}]
    
    with open('files/dictionary.json', 'r', encoding='utf-8') as fh:
        dictionary = json.load(fh)
    
    for word in list_words:
        isverb = False
        isnoun = False
        isadj = False
        try:
            dictionary[word]
            pos = dictionary[word][0]['partOfSpeech']
            core_word = word
            if pos == "adj.":
                isadj = True
                if word.endswith("a"):
                    mod = "right"
                elif mod != "right":
                    if word.startswith("a") or word.startswith("le"):
                        mod = "left"
            await ctx.send("{} is an unmodified {}".format(word, pos))
            
        except KeyError:
            # Noun Checking
            for key, value in cases.items():
                for suffix in value:
                    case = re.search(r""+suffix, word)
                    if case != None:
                        isnoun = True
                        core_word = re.sub(r""+suffix, '', word)
                        case_name = key
                        pos = dictionary[core_word][0]['partOfSpeech']
                        break
            # Verb Checking
            if not isnoun:
                if " s.i " in word:
                    for infix in infixes:
                        if not isverb:
                            for key, value in infix.items():
                                verb = re.search(r"s"+value+"i", word)
                                if verb != None:
                                    isverb = True
                                    core_word = re.sub(r"s"+value+"i", 'si', word)
                                    tense = key
                                    pos = dictionary[core_word][0]['partOfSpeech']
                                    break
                else:
                    for infix in infixes:
                        if not isverb:
                            for key, value in infix.items():
                                verb = re.search(r""+value, word)
                                if verb != None:
                                    isverb = True
                                    core_word = re.sub(r""+value, '', word)
                                    tense = key
                                    pos = dictionary[core_word][0]['partOfSpeech']
                                    break
            # Adjective Checking
            if not isnoun and not isverb:
                adj = re.search(r"\Aa|\Ale|a\Z", word)
                if adj != None:
                    isadj = True
                    if word.endswith("a"):
                        mod = "right"
                    elif mod != "right":
                        if word.startswith("a") or word.startswith("le"):
                            mod = "left"
                    core_word = re.sub(r"\Aa|a\Z", '', word)
                    pos = dictionary[core_word][0]['partOfSpeech']
                
        if isnoun:
            await ctx.send("{} is in the {} case.".format(core_word, case_name))
        elif isverb:
            if pos == 'vin.':
                await ctx.send("{} is an intransitive verb in the {}.".format(core_word, tense))
            elif pos == 'vtr.':
                await ctx.send("{} is a transitive verb in the {}.".format(core_word, tense))
            elif pos == 'vim.':
                await ctx.send("{} is an intransitive modal verb in the {}.".format(core_word, tense))
            elif pos == 'vtrm.':
                await ctx.send("{} is a transitive modal verb in the {}.".format(core_word, tense))
            elif pos == 'v.':
                await ctx.send("{} is a verb in the {}.".format(core_word, tense))
        elif isadj:
            if mod == "left":
                indexmod = -1
            elif mod == "right":
                indexmod = 1
            await ctx.send("{} is an adjective modifying the noun on the {}.".format(core_word, mod))

##-----------------------Error Handling-------------------##
# Error Handling for !help
@help.error
async def help_error(ctx, error):
   if isinstance(error, commands.CommandError):
       await ctx.send(embed=config.syntax)
       
kelutralBot.load_extension('cogs.utility.main')
kelutralBot.load_extension('cogs.games.main')
kelutralBot.load_extension('cogs.tnp.main')
kelutralBot.load_extension('cogs.server.main')

# Replace token with your bot's token
kelutralBot.run(config.token)
