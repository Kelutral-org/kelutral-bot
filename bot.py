# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import random

from datetime import datetime

import asyncio
import os
import glob

import admin
import namegen
import watcher

## Initialize Client
kelutral = discord.Client()

## Initialize Bot
kelutralBot = commands.Bot(command_prefix="!")

##--------------------Global Variables--------------------##

versionNumber = "Stable 1.0"
modRoleNames = ["Olo'eyktan (Admin)","Eyktan (Moderator)","Karyu (Teacher)","Numeyu (Learner)","'Eylan (Friend)","Tìkanu Atsleng (Bot)"]

## For Progression
activeRoleNames = ["Koaktu","Tsamsiyu","Tsamsiyutsyìp","Eykyu","Ikran Makto","Taronyu","Taronyutsyìp","Hapxìtu","Hapxìtutsyìp","Zìma'uyu","Ketuwong"]
activeRoleThresholds = [16384, 8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16]

## For Q/MOTD
send_time = '08:00'
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

# Updates the Visible Stat for 'names generated'
def update(newNameCount):
    fileName = 'users/bot.tsk'
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
        
# Updates roles based on activity.
# async def roleUpdate(count, check, message, user):
#     i = 0
#     activeRoles = message.guild.roles
#     langCheck = admin.outputCheck(message.author)
#     for roles in activeRoleNames:
#         if count >= activeRoleThresholds[i] and check.name != roles:
#             newRole = get(activeRoles, name=activeRoleNames[i])
#             await user.add_roles(newRole)
#             print('Tìmìng txintìnit alu ' + newRole.name + ' tuteru alu ' + user.display_name + '.')
#             if message.author.dm_channel is None:
#                 await message.author.create_dm()
#
#             if langCheck == "English":
#                 embed=discord.Embed()
#                 embed=discord.Embed(colour=0x1e3626)
#                 embed.add_field(name="New Rank Achieved on Kelutral.org", value="**Congratulations!** You're now a " + newRole.name + ".", inline=False)
#                 # embed.set_thumbnail(ctx.guild.icon_url)
#
#             elif langCheck == "Na'vi":
#                 embed=discord.Embed()
#                 embed=discord.Embed(colour=0x1e3626)
#                 embed.add_field(name="Mipa txìntin lu ngaru mì Helutral.org", value="**Seykxel si nitram!** Nga slolu " + newRole.name + ".", inline=False)
#                 # embed.set_thumbnail(ctx.guild.icon_url)
#
#             await message.author.send(embed=embed)
#
#             if check.name != "@everyone":
#                 await user.remove_roles(check)
#                 print("'olaku txintìnit alu " + check.name + " ta " + user.display_name + ".")
#             break
#         elif count >= activeRoleThresholds[i]:
#             break
#         i += 1

# System time check to know when to post a Question/Message of the Day, if available.
async def time_check():
    await kelutralBot.wait_until_ready()
    
    message_channel = kelutralBot.get_channel(message_channel_id)
    bot_ready = kelutralBot.is_closed()
    
    while not bot_ready:
        now = datetime.strftime(datetime.now(),'%H:%M')
        if now == send_time:
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%d-%m-%Y")
            fileName = 'qotd/' + timestampStr + '.tsk'
            if os.path.exists(fileName):
                fh = open(fileName, 'r')
                fileContents = fh.readlines(1)
                strippedContents = fileContents[0].strip("['")
                strippedContents = fileContents[0].strip("']")
                fh.close()
                os.remove(fileName)
                await message_channel.send(strippedContents)
                await message_channel.edit(topic=strippedContents,reason="Mipa tìpawm fìtrrä.")

                fh = open('qotd/calendar.tsk','r')
                fileContents = fh.read()
                fh.close()
                removeDate = fileContents.replace("\n" + timestampStr,'')
                fh = open('qotd/calendar.tsk','w')
                fh.write(removeDate)
                fh.close()
                
                time = 90
            else:
                time = 1
        else:
            time = 1
        await asyncio.sleep(time)

def reverse(s): 
    if len(s) == 0: 
        return s 
    else: 
        return reverse(s[1:]) + s[0] 

# English - Na'vi numberical conversion courtesy of Tirea Aean.
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

# Function for finding the next available date relative to the current date.
def nextAvailableDate(date):
    dateTimeObj = datetime.now()
    today = dateTimeObj.strftime("%d-%m-%Y")
    todayDate = today
    
    day = int(todayDate[0:2])
    month = int(todayDate[3:5])
    year = int(todayDate[-4:])

    fileName = 'qotd/' + str(date) + '.tsk'
    modDate = todayDate # This is included in case no date is passed to the function and no qotds exist
    
    while os.path.exists(fileName) == True:
        # Manages Output for single-digit days due to int()
        if day <= 8:
            day = day + 1
            day = "0" + str(day)
            
        elif day < 28:
            day = day + 1
                
        # If February, updates to the next month at 28 days.
        elif day == 28:
            thisMonthDays = monthDays[month - 1]
            if day == thisMonthDays:
                day = "01"
                month = month + 1
                if month < 10:
                    month = "0" + str(month)
            else:
                day = day + 1
                        
        elif day < 30:
            day = day + 1
            
            fileName = 'qotd/' + modDate + '.tsk'
                
        # If September, April, June or November, updates to the next month at 30 days.
        elif day == 30:
            thisMonthDays = monthDays[month - 1]
            if day == thisMonthDays:
                day = "01"
                month = month + 1
                if month < 10:
                    month = "0" + str(month)
            else:
                day = day + 1
                        
        # Updates to the next month at 31 days.
        elif day == 31:
            day = "01"
            if month < 10:
                month = month + 1
                month = "0" + str(month)
            elif month > 10 and not month == 12:
                month = month + 1
            elif month == 12:
                month = "01"
                year = year + 1
                        
        if int(month) < 10:
            month = str(month).strip("0")
            month = "0" + str(month)
        
        modDate = str(day) + "-" + str(month) + "-" + str(year)
        fileName = 'qotd/' + modDate + '.tsk'
        
        day = int(day)
        month = int(month)
    return modDate
    
##-----------------------Bot Events-----------------------##

@kelutralBot.event
async def on_ready():
    # This will be called when the bot connects to the server.
    nameCount = update(0)
    game = discord.Game("generated " + "{:,}".format(nameCount) + " names!")
    
    await kelutralBot.change_presence(status=discord.Status.online, activity=game)
    
    print("Kelutral Bot is ready.\nKelutral alaksi lu.")
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
    # If message is in-server
    if message.guild:
        if not message.content.startswith("!"):
            # If message is in guild and isn't from the bot.
            if len(message.content) >= 5 and message.author.top_role.id != 715094486992027699:
                user = message.author
                currentRole = user.top_role
                userRoles = user.roles
                isMod = False
                userMessageCount = 0
                fileName = 'users/' + str(user.id) + '.tsk'
                
                ## Check if author.top_role is moderator.
                if currentRole.name in modRoleNames:
                    isMod = True

                ## Assigns correct role to currentRole if mod.
                if isMod:
                    for role in userRoles:
                        if role.name not in modRoleNames:
                            currentRole = role

                ## Updates the user profile.
                if not os.path.exists(fileName):
                    fh = open(fileName, 'w')
                    fh.write(str(userMessageCount + 1) + "\n")
                    fh.write(user.name + "\n")
                    fh.write("English")
                    fh.close()
                    content = str(userMessageCount + 1)
                else:
                    content = admin.checkProfile(user, "Messages", "User Name", "Language Preference")

                    fh = open(fileName, "w")
                    fh.write(str(int(content[0]) + 1) + "\n")
                    fh.write(content[1] + "\n")
                    fh.write(content[2])
                    fh.close()
                        
                await roleUpdate(int(content[0]) + 1, currentRole, message, user)
    await kelutralBot.process_commands(message)
    
##-----------------------Bot Functions--------------------##
        
## Kill Command
@kelutralBot.command(name='quit', aliases=['ftang'])
async def botquit(ctx):
    user = ctx.message.author
    if user.top_role.name == "Olo'eyktan (Admin)":
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
    langCheck = admin.outputCheck(ctx.message.author)

    if langCheck == "English":
        displayversion = ["Version: ", versionNumber]
    elif langCheck == "Na'vi":
        displayversion = ["Srey: ", versionNumber]

    embed=discord.Embed(description=''.join(displayversion), colour=0x113f78)    
    await ctx.send(embed=embed)

## Update Rules
@kelutralBot.command(name='donotuse')
async def updateRules(ctx):
    await admin.adminMsgs(ctx, kelutralBot)

## Fuck off, LN.org
@kelutralBot.command(name='käneto', aliases=['fuckyou'])
async def goAway(ctx):
    await ctx.send("https://youtu.be/7JEbbihUCLw")
    
## Ban Command
@kelutralBot.command(name='ban', aliases=['yitx','kxanì'])
async def ban(ctx, user: discord.Member):
    if user.top_role.name == "Olo'eyktan (Admin)" or "Eyktan (Moderator)":
            await user.ban()
            embed=discord.Embed(description=str(user.mention) + "** was banned**", colour=0xff0000)
            await ctx.send(embed=embed)
   
## Member Join Stats   
@kelutralBot.command(name='showdata', aliases=['sd','rep'])
async def showData(ctx, *date):
    user = ctx.message.author
    if user.top_role.name == "Olo'eyktan (Admin)":
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
        # embed.set_footer(text="Use !find mm-dd-yyyy to query specific dates, or replace letters with ** to search all dates in that category.")
        
        await ctx.send(embed=embed)
    else:
        embed=discord.Embed(title="DENIED!", description="You do not have access to run this command!", colour=0xff0000)
        await ctx.send(embed=embed)

# Tskxekengsiyu functions
## Display User Message Count
@kelutralBot.command(name='profile', aliases=['yì'])
async def profile(ctx, user: discord.Member, *setting):
    ## -- Variables
    fileName = 'users/' + str(user.id) + '.tsk'
    setting = ''.join(setting)
    preference = str(setting).lower()
    
    output1 = admin.checkProfile(user, "Messages", "Language Preference")
    messages = int(output1[0])
    langCheck = output1[1]
    
    #langCheck = admin.outputCheck(ctx.message.author)
    userProf = ctx.message.guild.get_member(user.id)
    userCheck = admin.outputCheck(userProf)
    pronouns = admin.checkPronouns(ctx, user)
    
    ## -- Checks the total messages sent against the threshold.
    i = 0
    for role in activeRoleThresholds:
        if int(messages) >= activeRoleThresholds[i]:
            toNextLevel = activeRoleThresholds[i - 1] - int(messages)
            break
        elif int(messages) <= 16:
            toNextLevel = 16 - int(messages)
            break
        i += 1

    output2 = str(toNextLevel)
        
    ## -- Updates the user profile and sends.
    if preference == "":
        embed=discord.Embed(color=user.color, title=user.name)
        preference = langCheck
        if langCheck == "Na'vi":
            output1 = wordify(str(oct(messages))[2:])
            output2 = wordify(str(oct(toNextLevel))[2:])

            embed.add_field(name="Trr a tsatute zola'u: ", value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
            embed.add_field(name="Nulnawnewa Lì'fya: ", value=userCheck, inline=True)
            embed.add_field(name="Preferred Pronouns: ", value=pronouns, inline=True)
            if toNextLevel < 0:
                embed.add_field(name="Txìntin: ", value="Lu tsatuteru **'upxare aketsuktiam**.", inline=False)
            else:
                embed.add_field(name="Txìntin: ", value="Lu tsatuteru **" + output1[0] + " 'upxare**. Kin pol **" + output2 + " 'upxareti** fte slivu " + activeRoleNames[i - 1], inline=False)
            embed.set_footer(text='Sar !profile @user [English/Na\'vi] fte livatem lì\'fyati ngeyä.')
            embed.set_thumbnail(url=user.avatar_url) 
        elif langCheck == "English":
            embed.add_field(name="Join Date: ", value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
            embed.add_field(name="Preferred Language: ", value=userCheck, inline=True)
            embed.add_field(name="Preferred Pronouns: ", value=pronouns, inline=True)
            if toNextLevel < 0:
                embed.add_field(name="Current Rank: ", value=user.name + " has sent **" + output1[0] + " messages**.", inline=False)
            else:
                embed.add_field(name="Current Rank: ", value=user.name + " has sent **" + output1[0] + " messages**. They need **" + output2 + " more messages** in order to reach " + activeRoleNames[i - 1], inline=False)  
            embed.set_footer(text='Use !profile @user [English/Na\'vi] to change your output settings.')
            embed.set_thumbnail(url=user.avatar_url) 
    elif user.id == ctx.message.author.id:
        embed=discord.Embed(color=user.color, title=user.name)
        if preference == "na'vi":
            output1 = wordify(str(oct(messages))[2:])
            output2 = wordify(str(oct(toNextLevel))[2:])

            embed.add_field(name="Trr a tsatute zola'u: ", value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
            embed.add_field(name="Nulnawnewa Lì'fya: ", value=userCheck, inline=True)
            embed.add_field(name="Preferred Pronouns: ", value=pronouns, inline=True)
            if toNextLevel < 0:
                embed.add_field(name="Txìntin: ", value="Lu tsatuteru **'upxare aketsuktiam**.", inline=False)
            else:
                embed.add_field(name="Txìntin: ", value="Lu tsatuteru **" + output1[0] + " 'upxare**. Kin pol **" + output2 + " 'upxareti** fte slivu " + activeRoleNames[i - 1], inline=False)
            embed.set_footer(text='Sar !profile @user [English/Na\'vi] fte livatem lì\'fyati ngeyä.')
            embed.set_thumbnail(url=user.avatar_url) 
        elif preference == "english":
            embed.add_field(name="Join Date: ", value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
            embed.add_field(name="Preferred Language: ", value=userCheck, inline=True)
            embed.add_field(name="Preferred Pronouns: ", value=pronouns, inline=True)
            if toNextLevel < 0:
                embed.add_field(name="Current Rank: ", value=user.name + " has sent **" + output1[0] + " messages**.", inline=False)
            else:
                embed.add_field(name="Current Rank: ", value=user.name + " has sent **" + output1[0] + " messages**. They need **" + output2 + " more messages** in order to reach " + activeRoleNames[i - 1], inline=False)
            embed.set_footer(text='Use !profile @user [English/Na\'vi] to change your output settings.')
            embed.set_thumbnail(url=user.avatar_url) 
        else:
            embed=discord.Embed(color=0xff0000)
            embed.add_field(name='Error', value="Invalid criteria entered. Please select `English` or `Na'vi` to update your current settings.")
    else:
        embed=discord.Embed(color=0xff0000)
        embed.add_field(name="Error...", value="Sorry, you can only change your own output settings.")

    fh = open(fileName, 'w')
    fh.write(str(messages) + "\n")
    fh.write(user.name + "\n")
    fh.write(preference.capitalize() + "\n")
    fh.close()
       
    await ctx.send(embed=embed)

## Add a Question of the Day to a specified or the next available date
@kelutralBot.command(name='addqotd', aliases=['tìpawm'])
async def qotd(ctx, question, *date):
    langCheck = admin.outputCheck(ctx.message.author)
    if date:
        date = str(date).strip("(),' ")

        fileName = 'qotd/' + str(date) + '.tsk'
    else:
        dateTimeObj = datetime.now()
        today = dateTimeObj.strftime("%d-%m-%Y")
        todayDate = today

        date = nextAvailableDate(todayDate)

        fileName = 'qotd/' + str(date) + '.tsk'
            
    if not os.path.exists(fileName):        
        fh = open(fileName, "w")
        fh.write(str(question))
        fh.close()
        
        print("Created question of the day for " + str(date) + ".")
        
        fh = open('qotd/calendar.tsk', 'a')
        fh.write("\n" + str(date))
        fh.close()
        
        if langCheck.lower() == "english":
            await ctx.send("Created.")
        elif langCheck.lower() == "na'vi":
            await ctx.send("Ngolop.")
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")
    else:
        modDate = nextAvailableDate(date)
        
        if langCheck.lower() == "english":
            await ctx.send("A QOTD for this day already exists. The next available day to create a QOTD is " + modDate + ".")
        elif langCheck.lower() == "na'vi":
            await ctx.send("Fìtìpawm mi fkeytok! Haya trr a fkol tsun ngivop tìpawmit lu " + modDate + ".")
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")

## Retrieve the next Available Date for a Question of the Day
@kelutralBot.command(name='nextday', aliases=['hayasrr'])
async def nextDay(ctx):
    dateTimeObj = datetime.now()
    today = dateTimeObj.strftime("%d-%m-%Y")
    todayDate = today
    langCheck = admin.outputCheck(ctx.message.author)
    answer = nextAvailableDate(todayDate)


    if langCheck.lower() == "english":
        await ctx.send("The next day that a QOTD can be created for is " + answer + ".")
    elif langCheck.lower() == "na'vi":
        await ctx.send("Haya trr a fkol tsun ngivop tìpawmit lu " + answer + ".")
    else:
        await ctx.send("Somehow, and god knows how, you fucked up.")

## Check the Scheduled Dates for Questions of the Day
@kelutralBot.command(name='schedule', aliases=['srr'])
async def checkDates(ctx):
    fileName = 'qotd/calendar.tsk'
    fileSize = os.path.getsize(fileName)
    langCheck = admin.outputCheck(ctx.message.author)
    if os.path.exists(fileName) and not fileSize == 0:
        fh = open(fileName, 'r')
        contents = fh.read()
        fh.close()
        await ctx.send(contents)
    else:
        if langCheck.lower() == "english":
            await ctx.send("There are no scheduled QOTDs.")
        elif langCheck.lower() == "na'vi":
            await ctx.send("Kea srrur ke lu sìpawm.")
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")

## View a specific Question of the Day
@kelutralBot.command(name='viewqotd', aliases=['inan'])
async def readQuestion(ctx, date):
    fileName = 'qotd/' + str(date) + '.tsk'
    langCheck = admin.outputCheck(ctx.message.author)
    if os.path.exists(fileName):
        fh = open(fileName, 'r')
        contents = fh.read()
        fh.close()
        
        if langCheck.lower() == "english":
            await ctx.send("That question of the day is \"" + contents + "\"")
        elif langCheck.lower() == "na'vi":
            await ctx.send("Tsatìpawm lu \"" + contents + "\"")
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")
    else:

        if langCheck.lower() == "english":
            await ctx.send("No QOTD exists on that day.")
        elif langCheck.lower() == "na'vi":
            await ctx.send("Kea tìpawm mi ke fkeytok mì satrr.'.")
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")

## Change a specific Question of the Day
@kelutralBot.command(name='editqotd', aliases=['latem'])
async def changeQuestion(ctx, question, date):
    fileName = 'qotd/' + str(date) + '.tsk'
    langCheck = admin.outputCheck(ctx.message.author)
    if os.path.exists(fileName):
        fh = open(fileName, 'w')
        fh.write(question)
        fh.close()
        
        if langCheck.lower() == "english":
            await ctx.send("Edited.")
        elif langCheck.lower() == "na'vi":
            await ctx.send("Lolatem.")
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")
    else:

        if langCheck.lower() == "english":
            await ctx.send("No QOTD exists on that day.")
        elif langCheck.lower() == "na'vi":
            await ctx.send("Kea tìpawm mi ke fkeytok mì satrr.'.")
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")

## Delete a specific Question of the Day
@kelutralBot.command(name='deleteqotd', aliases=['ska\'a'])
async def deleteQuestion(ctx, date):
    fileName = 'qotd/' + str(date) + '.tsk'
    langCheck = admin.outputCheck(ctx.message.author)
    if os.path.exists(fileName):
        os.remove(fileName)
        
        fh = open('qotd/calendar.tsk','r')
        fileContents = fh.read()
        fh.close()
        
        removeDate = fileContents.replace("\n" + str(date),'')
        
        fh = open('qotd/calendar.tsk','w')
        fh.write(removeDate)
        fh.close()

        if langCheck.lower() == "english":
            await ctx.send("Removed.")
        elif langCheck.lower() == "na'vi":
            await ctx.send("Olaku'.")
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")
    else:
        if langCheck.lower() == "english":
            await ctx.send("No QOTD exists on that day.")
        elif langCheck.lower() == "na'vi":
            await ctx.send("Kea tìpawm mi ke fkeytok mì satrr.'.")
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")
                
# NameGenBot Functions
# Help Module
@kelutralBot.command(name="howto", aliases=['srung'])
async def howto(ctx):
    langCheck = admin.outputCheck(ctx.message.author)
    if langCheck.lower() == "english":
        await ctx.send("Syntax for the command is `!generate <number of names> <number of syllables>`. Maximum number of names is capped at 20 and syllables is capped at 5.")
    elif langCheck.lower() == "na'vi":
        await ctx.send("Fte sivar `!generate`ti, fìkem si: `!generate <stxoä holpxay> <aylì'kongä holpxay>`. Stxoä txantewä holpxay lu mevotsìng ulte lì'kongä txantewä holpxay lu mrr.")
    else:
        await ctx.send("Somehow, and god knows how, you fucked up.")

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
        if langCheck.lower() == "english":
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
        elif langCheck.lower() == "na'vi":
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
        if langCheck.lower() == "english":
            await ctx.send("Please enter a value greater than zero. If you need help with the `+generate` command, type `+howto`")
        elif langCheck.lower() == "na'vi":
            await ctx.send("Rutxe sar holpxayti a to kew lu apxa. Txo kivin srungti ngal, `+howto`ri pamrel si nga.")

    print(ctx.author.name + " generated " + str(n) + " names.")

# Error Handling for !generate
@generate.error
async def generate_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send("Invalid syntax. If you need help with the `!generate` command, type `!howto`")

# Error Handling for !profile
#@profile.error
# async def profile_error(ctx, error):
    # if isinstance(error, commands.CommandError):
        # await ctx.send("Invalid syntax. If you need help with the `!profile` command, type `!howto`")

# Replace token with your bot's token
kelutralBot.load_extension('roleupdate')
with open('token.txt','r') as file:
    token = file.read().strip()
kelutralBot.run(token)
