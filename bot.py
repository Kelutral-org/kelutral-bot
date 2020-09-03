# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import random

from datetime import datetime
from datetime import timedelta
import time

import asyncio
import os
import glob

import admin
import namegen
import watcher
import feedparser

## -- Initialize Client
kelutral = discord.Client()

## -- Initialize Bot
kelutralBot = commands.Bot(command_prefix="!")

##--------------------Global Variables--------------------##

versionNumber = "Stable 1.11"
adminName = "Olo'eyktan (Admin)"

## -- -- For Q/MOTD
send_time = '14:00'
message_channel_id = 715296162394931340
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
    if os.path.exists(fileName):
        fh = open(fileName, 'r')
        nameCount = int(fh.read())
        fh.close()
        
        nameCount = nameCount + newNameCount
        
        fh = open(fileName, 'w')
        fh.write(str(nameCount))
        fh.close()
        
    else:
        fh = open(fileName, 'w')
        fh.write(str(newNameCount))
        fh.close()
        nameCount = newNameCount
        
    return nameCount

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
    
    message_channel = kelutralBot.get_channel(message_channel_id)
    bot_ready = kelutralBot.is_closed()
    
    while not bot_ready:
    
        await rssfeedreader()
        
        now = datetime.strftime(datetime.now(),'%H:%M')
        if now == send_time:
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%d-%m-%Y")
            fileName = 'files/qotd/' + timestampStr + '.tsk'
            if os.path.exists(fileName):
                fh = open(fileName, 'r')
                fileContents = fh.readlines(1)
                strippedContents = fileContents[0].strip("['")
                strippedContents = fileContents[0].strip("']")
                fh.close()
                os.remove(fileName)
                
                await message_channel.send(strippedContents)
                await message_channel.edit(topic=strippedContents,reason="Mipa tìpawm fìtrrä.")

                fh = open('files/qotd/calendar.tsk','r')
                fileContents = fh.read()
                fh.close()
                removeDate = fileContents.replace("\n" + timestampStr,'')
                fh = open('files/qotd/calendar.tsk','w')
                fh.write(removeDate)
                fh.close()
                
                time = 90
            else:
                time = 1
        else:
            time = 1
            
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
    
    while os.path.exists(fileName) == True:
        tomorrow = tomorrow + timedelta(days=1)
        nextDay = tomorrow.strftime("%d-%m-%Y")
        fileName = 'files/qotd/' + str(nextDay) + '.tsk'
    return nextDay

## -- Reads the necessary files and builds the output for the Leaderboard command.
def buildLeaderboard(ctx, *user):
    ## -- Variables
    messageCounts = []
    userNames = []
    fileList = []
    i = 0
    
    if user:
        search_user = user[0]
        user = user[0]
    else:
        search_user = ctx.message.author
    
    ## -- Builds the Current Leaderboard
    for file in glob.glob('files/users/*.tsk'):
        fileList.append(file.strip('files/\\users.tsk'))
    for file in fileList:
        if file != 'bo':
            if not user:
                currentMember = ctx.message.guild.get_member(int(file))
            else:
                currentMember = ctx.message.guild.get_member(user.id)
                profile = admin.checkProfile(user, "Messages", "User Name")
            
            if currentMember == None:
                user = type('user', (), {})()
                user.id = int(file)
                user.nick = None
                profile = admin.checkProfile(user, "Messages", "User Name")
                user.name = profile[1]
                userNames.append(profile[1].encode('unicode-escape').decode('utf-8'))
                user = ""
            elif currentMember.nick == None:
                userNames.append(str(currentMember.name))
                profile = admin.checkProfile(currentMember, "Messages", "User Name")
                user = ""
            else:
                userNames.append(str(currentMember.nick))
                profile = admin.checkProfile(currentMember, "Messages", "User Name")
                user = ""
            messageCounts.append(int(profile[0]))
        
    sortedUserNames = [x for _,x in sorted(zip(messageCounts, userNames))]
    sortedMessageCounts = sorted(messageCounts)
    sortedUserNames.reverse()
    sortedMessageCounts.reverse()

    if search_user.nick == None:
        pos = sortedUserNames.index(search_user.name) + 1
    else:
        pos = sortedUserNames.index(search_user.nick) + 1

    return sortedUserNames, sortedMessageCounts, pos
    
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
    # This will be called when the bot connects to the server.
    nameCount = update(0)
    game = discord.Game("generated " + "{:,}".format(nameCount) + " names!")
    
    await kelutralBot.change_presence(status=discord.Status.online, activity=game)
    
    fileName = 'files/startup.txt'
    
    fh = open(fileName, 'r')
    lines = fh.readlines()
    
    for line in lines:
        print(line.strip('\n'))
        time.sleep(.025)
    fh.close()
    
    time.sleep(5)
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
    
##-----------------------Bot Functions--------------------##     
## Kill Command
@kelutralBot.command(name='quit', aliases=['ftang'])
async def botquit(ctx):
    user = ctx.message.author
    if user.top_role.name == adminName:
        embed=discord.Embed(description="Shutting down...", colour=0xff0000)
        
        await ctx.send(embed=embed)
        
        await kelutralBot.close()
        
        await kelutralBot.close()
        
        quit()
    else:
        embed=discord.Embed(title="DENIED!", description="You do not have access to run this command!", colour=0xff0000)
        
        await ctx.send(embed=embed)

## Version
@kelutralBot.command(name='version', aliases=['srey'])
async def version(ctx):
    user = ctx.message.author
    if user.top_role.name == adminName:
        langCheck = admin.outputCheck(user)

        if langCheck == "English":
            displayversion = ["Version: ", versionNumber]
        elif langCheck == "Na'vi":
            displayversion = ["Srey: ", versionNumber]

        embed=discord.Embed(description=''.join(displayversion), colour=0x113f78)  
        
        await ctx.send(embed=embed)

## Update Rules
@kelutralBot.command(name='donotuse')
async def updateRules(ctx):
    user = ctx.message.author
    if user.top_role.name == adminName:
        await admin.adminMsgs(ctx, kelutralBot)
    
## Ban Command
@kelutralBot.command(name='ban', aliases=['yitx','kxanì'])
async def ban(ctx, user: discord.Member):
    if user.top_role.name == adminName or "Eyktan (Moderator)":
            await user.ban()
            
            embed=discord.Embed(description=str(user.mention) + "** was banned**", colour=0xff0000)
            
            await ctx.send(embed=embed)
   
## Member Join Stats   
@kelutralBot.command(name='showdata', aliases=['sd','rep'])
async def showData(ctx, *date):
    user = ctx.message.author
    if user.top_role.name == adminName:
        if date:
            date = ''.join(date)
            joins1, leaves1, rds1 = admin.getStats(date)
        else:
            date = datetime.now().strftime('%m-%d-%Y')
            joins1, leaves1, rds1 = admin.getStats(date)
        
        embed=discord.Embed(title="Requested report for " + date, color=0x5Da9E9)
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
        embed.set_footer(text="Use !find mm-dd-yyyy to query specific dates, or replace \nletters with ** to search all dates in that category.")
        
        await ctx.send(embed=embed)
        
    else:
        embed=discord.Embed(title="DENIED!", description="You do not have access to run this command!", colour=0xff0000)
        
        await ctx.send(embed=embed)

## Display Server Leaderboard
@kelutralBot.command(name='leaderboard')
async def leaderboard(ctx):
    i = 0

    sortedUserNames, sortedMessageCounts, pos = buildLeaderboard(ctx)

    embed=discord.Embed(title="Server Leaderboard:", color=0x5Da9E9)
    
    while i <= 9:
        embed.add_field(name=sortedUserNames[i], value=str(sortedMessageCounts[i]) + " messages \n Rank: #" + str(i + 1), inline=False)
        i += 1
    embed.set_footer(text="You are ranked #" + str(pos) + " overall.")
    await ctx.send(embed=embed)
    
## Display User Message Count
@kelutralBot.command(name='profile', aliases=['yì'])
async def profile(ctx, user: discord.Member, *setting):
    ## -- Variables
    fileName = 'files/users/' + str(user.id) + '.tsk'
    setting = ''.join(setting)
    preference = str(setting).lower()
    maxmc = 0
    
    output1 = admin.checkProfile(user, "Messages", "Language Preference")
    messages = int(output1[0])
    langCheck = output1[1]
    
    userProf = ctx.message.guild.get_member(user.id)
    userCheck = admin.outputCheck(userProf)
    pronouns = admin.checkPronouns(ctx, user)
    
    sortedUserNames, sortedMessageCounts, pos = buildLeaderboard(ctx, user)
    
    ## -- Checks the total messages sent against the threshold.
    i = 0
    for role in admin.activeRoleThresholds:
        if int(messages) >= admin.activeRoleThresholds[i]:
            toNextLevel = admin.activeRoleThresholds[i - 1] - int(messages)
            break
        elif int(messages) <= 16:
            toNextLevel = 16 - int(messages)
            break
        i += 1

    if i == 0:
        i = -1
    
    output2 = str(toNextLevel)
        
    ## -- Updates the user profile and sends.
    if preference == "":
        embed=discord.Embed(color=user.color, title=user.name)
        preference = langCheck
        if langCheck == "Na'vi":
            output1 = wordify(str(oct(messages))[2:])
            output2 = wordify(str(oct(toNextLevel))[2:])

            embed.add_field(name="Trr a tsatute zola'u: ", value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
            embed.add_field(name="Nulnawnewa Lì'fya: ", value=langCheck, inline=True)
            embed.add_field(name="Preferred Pronouns: ", value=pronouns, inline=True)
            embed.add_field(name="Txìntin: ", value=admin.activeRoleNames[i])
            if toNextLevel < 0:
                embed.add_field(name="Ayupxare: ", value="'Upxare aketsuktiam.", inline=False)
            else:
                embed.add_field(name="Ayupxare: ", value=output1[0] + " 'upxare. Kin pol **" + output2 + " 'upxareti** fte slivu " + admin.activeRoleNames[i - 1], inline=False)
            embed.add_field(name="Server Leaderboard Rank: ", value=pos)
            embed.set_footer(text='Sar fayluta !profile @user [English/Na\'vi] fte leykivatem lì\'fyati ngeyä.')
            embed.set_thumbnail(url=user.avatar_url) 
        elif langCheck == "English":
            embed.add_field(name="Join Date: ", value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
            embed.add_field(name="Preferred Language: ", value=langCheck, inline=True)
            embed.add_field(name="Preferred Pronouns: ", value=pronouns, inline=True)
            embed.add_field(name="Current Rank: ", value=admin.activeRoleNames[i])
            if toNextLevel < 0:
                embed.add_field(name="Message Count: ", value=output1[0] + " messages.", inline=False)
            else:
                embed.add_field(name="Message Count: ", value=output1[0] + " messages. They need **" + output2 + " more messages** in order to reach " + admin.activeRoleNames[i - 1], inline=False)  
            embed.add_field(name="Server Leaderboard Rank: ", value=pos)
            embed.set_footer(text='Use !profile @user [English/Na\'vi] to change your output settings.')
            embed.set_thumbnail(url=user.avatar_url) 
    elif user.id == ctx.message.author.id:
        embed=discord.Embed(color=user.color, title=user.name)
        if preference == "na'vi":
            output1 = wordify(str(oct(messages))[2:])
            output2 = wordify(str(oct(toNextLevel))[2:])

            embed.add_field(name="Trr a tsatute zola'u: ", value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
            embed.add_field(name="Nulnawnewa Lì'fya: ", value=preference.capitalize(), inline=True)
            embed.add_field(name="Preferred Pronouns: ", value=pronouns, inline=True)
            embed.add_field(name="Txìntin: ", value=admin.activeRoleNames[i])
            if toNextLevel < 0:
                embed.add_field(name="Ayupxare: ", value="'Upxare aketsuktiam.", inline=False)
            else:
                embed.add_field(name="Ayupxare: ", value=output1[0] + " 'upxare. Kin pol **" + output2 + " 'upxareti** fte slivu " + admin.activeRoleNames[i - 1], inline=False)
            embed.add_field(name="Server Leaderboard Rank: ", value=pos)
            embed.set_footer(text='Sar fayluta !profile @user [English/Na\'vi] fte leykivatem lì\'fyati ngeyä.')
            embed.set_thumbnail(url=user.avatar_url) 
        elif preference == "english":
            embed.add_field(name="Join Date: ", value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
            embed.add_field(name="Preferred Language: ", value=preference.capitalize(), inline=True)
            embed.add_field(name="Preferred Pronouns: ", value=pronouns, inline=True)
            embed.add_field(name="Current Rank: ", value=admin.activeRoleNames[i])
            if toNextLevel < 0:
                embed.add_field(name="Message Count: ", value=output1[0] + " messages.", inline=False)
            else:
                embed.add_field(name="Message Count: ", value=output1[0] + " messages. They need **" + output2 + " more messages** in order to reach " + admin.activeRoleNames[i - 1], inline=False)  
            embed.add_field(name="Server Leaderboard Rank: ", value=pos)
            embed.set_footer(text='Use !profile @user [English/Na\'vi] to change your output settings.')
            embed.set_thumbnail(url=user.avatar_url) 
        else:
            embed=discord.Embed(color=0xff0000)
            embed.add_field(name='Error', value="Invalid criteria entered. Please select `English` or `Na'vi` to update your current settings.")
    else:
        embed=discord.Embed(color=0xff0000)
        embed.add_field(name="Error", value="Sorry, you can only change your own output settings.")

    fh = open(fileName, 'w')
    fh.write(str(messages) + "\n")
    fh.write(user.name + "\n")
    fh.write(preference.capitalize() + "\n")
    fh.close()
       
    await ctx.send(embed=embed)

## Add a Question of the Day to a specified or the next available date
@kelutralBot.command(name='addqotd', aliases=['tìpawm'])
async def qotd(ctx, question, *date):
    user = ctx.message.author
    langCheck = admin.outputCheck(user)
    if user.top_role.name == adminName or "Eyktan (Moderator)" or "Karyu (Teacher)":
        if date:
            date = str(date).strip("(),' ")
            fileName = 'files/qotd/' + str(date) + '.tsk'
        else:
            date = nextAvailableDate()
            fileName = 'files/qotd/' + str(date) + '.tsk'
                
        if not os.path.exists(fileName):        
            fh = open(fileName, "w")
            fh.write(str(question))
            fh.close()

            now = datetime.strftime(datetime.now(),'%H:%M')
            print(now + " -- Created question of the day for " + str(date) + ".")
            
            fh = open('files/qotd/calendar.tsk', 'a')
            fh.write("\n" + str(date))
            fh.close()
            
            if langCheck == "English":
                embed=discord.Embed(description='Created.', colour=0x00c600) 
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Ngolop.', colour=0x00c600) 
            else:
                await ctx.send("Somehow, and god knows how, you fucked up.")
                
            await ctx.send(embed=embed)
            
        else:
            modDate = nextAvailableDate()
            
            if langCheck == "English":
                embed=discord.Embed(description="A QOTD for this day already exists. The next available day to create a QOTD is " + modDate + ".", colour=0xff0000)
            elif langCheck == "Na'vi":
                embed=discord.Embed(description="Fìtìpawm mi fkeytok! Haya trr a fkol tsun ngivop tìpawmit lu " + modDate + ".", colour=0xff0000)
            else:
                await ctx.send("Somehow, and god knows how, you fucked up.")
                
            await ctx.send(embed=embed)

## Retrieve the next Available Date for a Question of the Day
@kelutralBot.command(name='nextday', aliases=['hayasrr'])
async def nextDay(ctx):
    user = ctx.message.author
    langCheck = admin.outputCheck(user)
    answer = nextAvailableDate()
    if user.top_role.name == adminName or "Eyktan (Moderator)" or "Karyu (Teacher)":
        if langCheck == "English":
            embed=discord.Embed(description="The next day that a QOTD can be created for is " + answer + ".", colour=0x00c600) 
            
        elif langCheck == "Na'vi":
            embed=discord.Embed(description="Haya trr a fkol tsun ngivop tìpawmit lu " + answer + ".", colour=0x00c600)
            
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")
            
        await ctx.send(embed=embed)

## Check the Scheduled Dates for Questions of the Day
@kelutralBot.command(name='schedule', aliases=['srr'])
async def checkDates(ctx):
    user = ctx.message.author
    fileName = 'files/qotd/calendar.tsk'
    fileSize = os.path.getsize(fileName)
    langCheck = admin.outputCheck(user)
    if user.top_role.name == adminName or "Eyktan (Moderator)" or "Karyu (Teacher)":
        dates = []
        questions = []
        
        if os.path.exists(fileName) and not fileSize == 10:
            fh = open(fileName, 'r')
            for line in fh:
                filePath = 'files/qotd/' + line.strip() + '.tsk'
                if os.path.exists(filePath):
                    dates.append(line.strip())
                    fp = open(filePath, 'r')
                    questions.append(fp.read())
                    fp.close()
            fh.close()

            if langCheck == "English":
                embed=discord.Embed(description="**Upcoming Questions of the Day:**", color=0x8f6593)
            elif langCheck == "Na'vi":
                embed=discord.Embed(description="**Haya srrä sìpawm:**", color=0x8f6593)
            else:
                now = datetime.strftime(datetime.now(),'%H:%M')
                print(now + " -- Whoops!")
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
                embed=discord.Embed(description='There are no scheduled QOTDs.', colour=0xff0000) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Kea srrur ke lu sìpawm.', colour=0xff0000) 
                
            else:
                await ctx.send("Somehow, and god knows how, you fucked up.")
                
            await ctx.send(embed=embed)

## View a specific Question of the Day
@kelutralBot.command(name='viewqotd', aliases=['inan'])
async def readQuestion(ctx, date):
    user = ctx.message.author
    fileName = 'files/qotd/' + str(date) + '.tsk'
    langCheck = admin.outputCheck(user)
    if user.top_role.name == adminName or "Eyktan (Moderator)" or "Karyu (Teacher)":
        if os.path.exists(fileName):
            fh = open(fileName, 'r')
            contents = fh.read()
            fh.close()
            
            if langCheck == "English":
                embed=discord.Embed(description='That question of the day is \"' + contents + '\"', colour=0x00c600)
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Tsatìpawm lu \"' + contents + '\"', colour=0x00c600)
                
            else:
                await ctx.send("Somehow, and god knows how, you fucked up.")
            
            await ctx.send(embed=embed)
                
        else:

            if langCheck == "English":
                embed=discord.Embed(description='No QOTD exists on that day.', colour=0xff0000) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Kea tìpawm mi ke fkeytok mì satrr.', colour=0xff0000) 
                
            else:
                await ctx.send("Somehow, and god knows how, you fucked up.")
            
            await ctx.send(embed=embed)

## Change a specific Question of the Day
@kelutralBot.command(name='editqotd', aliases=['latem'])
async def changeQuestion(ctx, question, date):
    user = ctx.message.author
    fileName = 'files/qotd/' + str(date) + '.tsk'
    langCheck = admin.outputCheck(user)
    if user.top_role.name == adminName or "Eyktan (Moderator)" or "Karyu (Teacher)":
        if os.path.exists(fileName):
            fh = open(fileName, 'w')
            fh.write(question)
            fh.close()
            
            if langCheck == "English":
                embed=discord.Embed(description='Edited.', colour=0x00c600) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Lolatem.', colour=0x00c600) 
                
            else:
                await ctx.send("Somehow, and god knows how, you fucked up.")
                
            await ctx.send(embed=embed)
            
        else:

            if langCheck == "English":
                embed=discord.Embed(description='No QOTD exists on that day.', colour=0xff0000) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Kea tìpawm mi ke fkeytok mì satrr.', colour=0xff0000)
                
            else:
                await ctx.send("Somehow, and god knows how, you fucked up.")
                
            await ctx.send(embed=embed)

## Delete a specific Question of the Day
@kelutralBot.command(name='deleteqotd', aliases=['ska\'a'])
async def deleteQuestion(ctx, date):
    user = ctx.message.author
    fileName = 'files/qotd/' + str(date) + '.tsk'
    langCheck = admin.outputCheck(user)
    if user.top_role.name == adminName or "Eyktan (Moderator)" or "Karyu (Teacher)":
        if os.path.exists(fileName):
            os.remove(fileName)
            
            fh = open('files/qotd/calendar.tsk','r')
            fileContents = fh.read()
            fh.close()
            
            removeDate = fileContents.replace("\n" + str(date),'')
            
            fh = open('files/qotd/calendar.tsk','w')
            fh.write(removeDate)
            fh.close()

            if langCheck == "English":
                embed=discord.Embed(description='Removed.', colour=0x00c600) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Olaku\'.', colour=0x00c600) 
                
            else:
                await ctx.send("Somehow, and god knows how, you fucked up.")
             
            await ctx.send(embed=embed)
                
        else:
            if langCheck == "English":
                embed=discord.Embed(description='No QOTD exists on that day.', colour=0xff0000) 
                
            elif langCheck == "Na'vi":
                embed=discord.Embed(description='Kea tìpawm mi ke fkeytok mì satrr.', colour=0xff0000)
                
            else:
                await ctx.send("Somehow, and god knows how, you fucked up.")
                
            await ctx.send(embed=embed)

# Generate # of random names
@kelutralBot.command(name="generate",aliases=['ngop'])
async def generate(ctx, numOut, numSyllables):
    # Initializing Variables
    n = int(numOut)
    i = int(numSyllables)
    output = []
    c = 0
    langCheck = admin.outputCheck(ctx.message.author)
    if not n <= 0 and not i <= 0:
        if langCheck == "English":
            if not i <= 5:
                await ctx.send("Maximum syllable count allowed by the bot is 5. It is highly recommended that you select a name that is between 1 and 3 syllables.")
                
            elif not n <= 20:
                await ctx.send("Maximum name count allowed is 20.")
                
            else:
                nameCount = update(n)
                game = discord.Game("ngamop " + "{:,}".format(nameCount) + " tstxoti.")
        
                await kelutralBot.change_presence(status=discord.Status.online, activity=game)

                embed=discord.Embed(color=0x00c600)
                embed.set_author(name="Here are your names:")
                while c < n:
                    output.append(namegen.nameGen(numSyllables))
                    embed.add_field(name="Name " + str(c + 1) + ":", value=output[c], inline=True)
                    c += 1
                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                
                await ctx.send(embed=embed)
                
        elif langCheck == "Na'vi":
            if not i <= 5:
                await ctx.send("Lì'kongä txantewä holpxay lu mrr. Sweylu txo ngal ftxivey tstxoti a lu tsa'ur lì'kong apxey, lì'kong amune, fu lìkong a'aw.")
                
            elif not n <= 20:
                await ctx.send("Stxoä txantxewä holpxay lu mevotsìng.")
                
            else:
                nameCount = update(n)
                game = discord.Game("ngamop " + "{:,}".format(nameCount) + " tstxoti.")
        
                await kelutralBot.change_presence(status=discord.Status.online, activity=game)
                
                embed=discord.Embed(color=0x00c600)
                embed.set_author(name="Faystxo lu ngaru ma " + ctx.message.author.name + ":")
                while c < n:
                    output.append(namegen.nameGen(numSyllables))
                    embed.add_field(name="Tstxo "+ str(c + 1) + ":", value=output[c], inline=True)
                    c += 1
                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                
                await ctx.send(embed=embed)
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")
    else:
        if langCheck == "English":
            await ctx.send("Please enter a value greater than zero. If you need help with the `+generate` command, type `+howto`")
            
        elif langCheck == "Na'vi":
            await ctx.send("Rutxe sar holpxayti a to kew lu apxa. Txo kivin srungti ngal, `+howto`ri pamrel si nga.")
    
    now = datetime.strftime(datetime.now(),'%H:%M')
    print(now + " -- " + ctx.author.name + " generated " + str(n) + " names.")

## Thank the Bot
@kelutralBot.command(name="thanks", aliases=['irayo'])
async def thanks(ctx):
    user = ctx.message.author
    langCheck = admin.outputCheck(user)
    if langCheck == "English":
        await ctx.send("You're welcome, " + str(user.mention))
    elif langCheck == "Na'vi":
        await ctx.send("Tstunwi ma " + str(user.mention))
    else:
        await ctx.send("Whoops!")

# Error Handling for !generate
@generate.error
async def generate_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send("Invalid syntax. If you need help with the `!generate` command, type `!help generate`")

# Error Handling for !profile
# @profile.error
# async def profile_error(ctx, error):
    # if isinstance(error, commands.CommandError):
        # await ctx.send("Invalid syntax. If you need help with the `!profile` command, type `!help profile` " + str(error))

# Replace token with your bot's token
kelutralBot.run("token")
