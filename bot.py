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
import uuid
from datetime import datetime
from datetime import timedelta
from os import listdir
from os.path import isfile, join

import config
import admin

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
            
            onlyfiles = [f for f in listdir('files/config/splashes') if isfile(join('files/config/splashes', f))]
            randomSplash = 'files/config/splashes/' + onlyfiles[random.randint(0,len(onlyfiles)-1)]
            
            with open(randomSplash, "rb") as image:
                f = image.read()
            
            guild = await kelutralBot.fetch_guild(715043968886505484).edit(banner=f)
            
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
async def on_command(ctx):
    now = datetime.now().strftime('%H:%M')
    command = ctx.message.content.split(" ")[0]
    arguments = ctx.message.content.replace(command, "")
    print(now + " -- {}: {} executed the {} command with arguments:{}".format(ctx.message.author.name, ctx.message.author.id, command, arguments))

@kelutralBot.command(name='inquiries', aliases=['inq'])
async def inquiries(ctx, *inquiry):
    inquiry = list(inquiry)
    remove_mode = False
    write_mode = False
    update_mode = False
    update_response = True
    update_tags = False
    search_mode = False
    search_author = False
    search_hex = False
    search_tags = False
    
    with open('cogs/shared/files/inquirydatabase.json', 'r', encoding='utf-8') as fh:
        inquiry_database = json.load(fh)
    
    if "-r" in inquiry:
        inquiry.remove("-r")
        remove_mode = True
    elif "-w" in inquiry:
        inquiry.remove("-w")
        write_mode = True
    elif "-s" in inquiry:
        inquiry.remove("-s")
        search_mode = True
        if "-a" in inquiry:
            inquiry.remove("-a")
            search_author = True
        elif "-id" in inquiry:
            inquiry.remove("-id")
            search_hex = True
        elif "-t" in inquiry:
            inquiry.remove("-t")
            search_tags = True
    elif "-u" in inquiry:
        inquiry.remove("-u")
        update_mode = True
        if "-a" in inquiry:
            inquiry.remove("-a")
            update_response = True
        elif "-t" in inquiry:
            inquiry.remove("-t")
            update_tags = True
        entry_id = inquiry[0]
        inquiry.remove(entry_id)
        
    else:
        await ctx.send("No operating flag provided. Please use `-r`, `-w` or `-s`.")
        return
    
    if [remove_mode, write_mode, search_mode, update_mode].count(True) > 1:
        await ctx.send("Too many operating flags provided. Please only use one of `-r`, `-w` or `-s`.")
        return
        
    joined_inquiry = ' '.join(inquiry)
    
    def search_function(ctx, key, value, search_term, search_item, slim):
        results = ''
        search = re.search(r""+search_term, str(search_item))
        if search != None:
            if slim:
                results += "Inquiry: {}\nAuthor: {}\nResponse: {}\nEntry ID: {}\n\n".format((key[0:40]+"`[...]`").replace("*","").replace("_", ""), ctx.guild.get_member(value['author']).mention, value['response'], value['id'])
            else:
                try:
                    results += "Inquiry: {}\nAuthor: {}\nResponse: {}\nDate Added: {} EST\nTags: {}\nEntry ID: {}\n\n".format(key, ctx.guild.get_member(value['author']).mention, value['response'], value['date'], value['tags'], value['id'])
                except KeyError:
                    results += "Inquiry: {}\nAuthor: {}\nResponse: {}\nDate Added: {} EST\nEntry ID: {}\n\n".format(key, ctx.guild.get_member(value['author']).mention, value['response'], value['date'], value['id'])
        return results
    
    if search_mode:
        results = ''
        if search_author:
            tag = 'author'
            for key, value in inquiry_database.items():
                results += search_function(ctx, key, value, joined_inquiry, value[tag], False)
        elif search_hex:
            tag = 'id'
            for key, value in inquiry_database.items():
                results += search_function(ctx, key, value, joined_inquiry, value[tag], False)
        elif search_tags:
            tag = 'tags'
            for key, value in inquiry_database.items():
                try:
                    results += search_function(ctx, key, value, joined_inquiry, value[tag], False)
                except KeyError:
                    continue
        else:
            tag = ''
            for key, value in inquiry_database.items():
                results += search_function(ctx, key, value, joined_inquiry, key, False)
        
        if results != '':
            if len(results) > 2048:
                results = ''
                for key, value in inquiry_database.items():
                    if tag != '':
                        results += search_function(ctx, key, value, joined_inquiry, value[tag], True)
                    else:
                        results += search_function(ctx, key, value, joined_inquiry, key, True)
                try:    
                    await ctx.send(embed=discord.Embed(title="Too many entries found, unable to show full descriptions.", description=results, color=config.reportColor))
                except HTTPException:
                    await ctx.send(embed=discord.Embed(description="**Error: Too many entries!**\nTry narrowing your search terms.", color=config.failColor))
            else:
                await ctx.send(embed=discord.Embed(title="Found Entries:", description=results, color=config.reportColor))
        else:
            await ctx.send(embed=config.database)
        
    elif write_mode:
        entry_id = uuid.uuid1()
        with open('cogs/shared/files/inquirydatabase.json', 'w', encoding='utf-8') as fh:
            inquiry_database[joined_inquiry] = {"date" : datetime.now().strftime("%m-%d-%Y, %H:%M.%S"), "author" : ctx.message.author.id, "response" : "", "tags" : "", "id" : entry_id.hex}
            json.dump(inquiry_database, fh)
        await ctx.send(embed=discord.Embed(title="Created Entry", description="Inquiry: {}\nAuthor: {}\nDate Added: {} EST\nEntry ID: {}\n\n".format(joined_inquiry, ctx.guild.get_member(inquiry_database[joined_inquiry]['author']).mention, inquiry_database[joined_inquiry]['date'], inquiry_database[joined_inquiry]['id'])))
            
    elif remove_mode:
        for key, value in inquiry_database.items():
            if joined_inquiry == value['id']:
                removed_value = inquiry_database.pop(key)
                with open('cogs/shared/files/inquirydatabase.json', 'w', encoding='utf-8') as fh:
                    json.dump(inquiry_database, fh)
                await ctx.send(embed=config.success)
                return
        await ctx.send(embed=config.database)
    
    elif update_mode:
        for key, value in inquiry_database.items():
            if entry_id == value['id']:
                if update_tags:
                    value['tags'] = joined_inquiry
                elif update_response:
                    value['response'] = joined_inquiry
                with open('cogs/shared/files/inquirydatabase.json', 'w', encoding='utf-8') as fh:
                    json.dump(inquiry_database, fh)
                await ctx.send(embed=config.success)
                return
        await ctx.send(embed=config.database)

@kelutralBot.command(name='naviteri', aliases=['nt'])
async def naviteri(ctx, *search):
    user = ctx.message.author
    results = ''
    search = list(search)
    searchTags = False
    results_list = []
    
    if "-t" in search:
        search.remove("-t")
        searchTags = True
        
    with open('cogs/shared/files/naviteri.json', 'r', encoding='utf-8') as fh:
        naviteri = json.load(fh)
    
    for query in search:
        print(query)
        for key, value in naviteri.items():
            if searchTags:
                if query in value['tags']:
                    results += "**{}**\n{}\n\n".format(key, value['link'])
            else:
                res = re.search(r"."+query+".", value['content'].lower())
                if res != None:
                    results += "**{}**\n{}\n\n".format(key, value['link'])
            
            if 1800 < len(results) < 2048:
                results_list.append(results)
                results = ''
    
    results_list.append(results)
    
    if len(results_list) > 1:
        await ctx.send("More than 20 results found. DMing you the results.")
        for n, result in enumerate(results_list):
            embed=discord.Embed(title="Search Results {}/{}".format(n+1, len(results_list)), description=result, color=config.reportColor)
            await user.send(embed=embed)
    else:
        for n, result in enumerate(results_list):
            embed=discord.Embed(title="Search Results {}/{}".format(n+1, len(results_list)), description=result, color=config.reportColor)
            await ctx.send(embed=embed)

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
    query = list(query)
    isTag = False
    
    if "-t" in query:
        query.remove("-t")
        isTag = True
    
    reykcommands = [('**run**','Translates a Na\'vi word into English.\n'),
                    ('**find**','Finds words whose English definitions contain the query.\n'),
                    ('**tslam**','Runs a grammar analyzer on your sentence.\n',)]
                    
    if len(query) > 1:
        await ctx.send(embed=config.syntax)
        return
    elif len(query) == 0:
        query = ""
    else:
        query = query[0]
    
    if len(query) > 0:
        if not isTag:
            try:
                command = config.helpFile[query]
                embed = discord.Embed(title=command['name'], description="Aliases: {}\nUsage: {}\nExample: {}\nDescription: {}".format(''.join(command['aliases']), command['usage'], command['example'], command['description']))
                embed.set_footer(text="Tags: {}".format(', '.join(command['tags'])))
            except KeyError:
                embed = config.helpError
                await ctx.send(embed=embed)
                return
        else:
            output = ""
            for entry in config.helpFile.values():
                if query in entry['tags']:
                    output = output + entry['name'] + ": " + entry['short']
            embed = discord.Embed(title="!help {}".format(query), description="Here are {}'s available commands with tag `{}`.\n\nUse `!help <command>` for more information about that command.\n\n".format(guild.get_member(config.botID).mention, query) + output)

    else:
        output = ""
        
        # Eytukan's command list
        for entry in config.helpFile.values():
            output = output + entry['name'] + ": " + entry['short']
        
        if ctx.guild.id == config.KTID:
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

##-----------------------Error Handling-------------------##
# Error Handling for !help
@help.error
async def help_error(ctx, error):
   if isinstance(error, commands.CommandError):
       await ctx.send(embed=config.syntax)

kelutralBot.load_extension('cogs.kelutral.main')
kelutralBot.load_extension('cogs.pandora_rising.main')
kelutralBot.load_extension('cogs.shared.main')
kelutralBot.load_extension('cogs.shared.kelutral_listener')
kelutralBot.load_extension('cogs.shared.pandora_rising_listener')

kelutralBot.run(config.token)
