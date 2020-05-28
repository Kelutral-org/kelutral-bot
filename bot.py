# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import random

from datetime import datetime

import asyncio
import os

## Initialize Client
kelutral = discord.Client()

## Initialize Bot
kelutralBot = commands.Bot(command_prefix="!")

##--------------------Global Variables--------------------##

versionNumber = "Alpha 0.6"
modRoleNames = ["Olo'eyktan (Admin)","Eyktan (Moderator)","Karyu (Teacher)","Numeyu (Learner)","'Eylan (Friend)","Tìkanu Atsleng (Bot)"]

## For Progression
activeRoleNames = ["Koaktu","Tsamsiyu","Tsamsiyutsyìp","Eykyu","Ikran Makto","Taronyu","Taronyutsyìp","Hapxìtu","Hapxìtutsyìp","Zìma'uyu","Ketuwong"]
activeRoleThresholds = [16384, 8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16]

## For Q/MOTD
send_time = '08:00'
message_channel_id = 715296162394931340
            #Ja, Fe, Ma, Ap, Ma, Ju, Jl, Au, Se, Oc, No, De
monthDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

## Na'vi Alphabet
vowels = ["a","ä","e","i","ì","o","u","aw","ay","ew","ey"]
vowelProbabilities = [10,10,10,10,10,10,10,2,2,2,2]
consonants = ["'","f","h","k","kx","l","m","n","ng","p","px","r","s","t","tx","ts","v","w","y","z"]
consonantProbabilities = [1,6,6,6,3,6,6,6,4,6,3,4,6,6,3,6,5,5,5,5]
pseudovowels = ["ll","rr"]
diphthongs = ["aw","ay","ew","ey"]

preconsonants = ["f","s","ts"]
onsets_withpre = ["k","kx","l","m","n","ng","p","px","r","t","tx","w","y"]
onsetProbabilities = [5,2,5,5,5,4,5,2,4,5,2,3,3]
codas = ["'","k","kx","l","m","n","ng","p","px","r","t","tx"]
codaProbabilities = [50,8,3,8,8,8,3,8,3,8,8,3]

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

# Language Rules #
# A syllable may start with a vowel
# A syllable may end with a vowel
# A consonant may start a syllable
# A consonant cluster comprised of f, s, or ts + p, t, k, px, tx, kx, m, n, ng, r, l, w, or y may start a syllable
# Px, tx, kx, p, t, k, ', m, n, l, r, or ng may occur in syllable-final position
# Ts, f, s, h, v, z, w, or y may not occur in syllable-final position
# No consonant clusters in syllable-final position
# A syllable with a pseudovowel must start with a consonant or consonant cluster and must not have a final consonant

# Valid Syllables #
# Just one vowel
# Consonant and vowel
# Consonant cluster and vowel
# Vowel and coda
# Consonant, vowel and coda
# Consonant cluster, vowel and coda
# Consonant and pseudovowel
# Consonant cluster, pseudovowel

##--------------------Global Functions--------------------##

## Syllable Creation Functions

def ruleOne():
    vowel = random.choices(vowels, weights=vowelProbabilities)
    return vowel[0]

def ruleTwo():
    vowel = random.choices(vowels, weights=vowelProbabilities)
    consonant = random.choices(consonants, weights=consonantProbabilities)
    s = consonant[0] + vowel[0]
    return s

def ruleThree():
    vowel = random.choices(vowels, weights=vowelProbabilities)
    onset = random.choices(onsets_withpre, weights=onsetProbabilities)
    s = preconsonants[random.randint(0,2)] + onset[0] + vowel[0]
    return s

def ruleFour():
    vowel = random.choices(vowels, weights=vowelProbabilities)
    s = vowel[0] + codas[random.randint(0,11)]
    return s

def ruleFive():
    consonant = random.choices(consonants, weights=consonantProbabilities)
    vowel = random.choices(vowels, weights=vowelProbabilities)
    coda = random.choices(codas, weights=codaProbabilities)
    s = consonant[0] + vowel[0] + coda[0]
    return s

def ruleSix():
    vowel = random.choices(vowels, weights=vowelProbabilities)
    onset = random.choices(onsets_withpre, weights=onsetProbabilities)
    coda = random.choices(codas, weights=codaProbabilities)
    s = preconsonants[random.randint(0,2)] + onset[0] + vowel[0] + coda[0]
    return s

def ruleSeven():
    consonant = random.choices(consonants, weights=consonantProbabilities)
    s = consonant[0] + pseudovowels[random.randint(0,1)]
    return s

def ruleEight():
    onset = random.choices(onsets_withpre, weights=onsetProbabilities)
    s = preconsonants[random.randint(0,2)] + onset[0] + pseudovowels[random.randint(0,1)]
    return s

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
    
# Name Generation Function

def nameGen(numOut, numSyllables):
    names = []
    name = ""
    output = " "

    n = int(numOut)
    i = int(numSyllables)

    # Conditional Loop for Number of Names
    while n>0:
        i = int(numSyllables)

        # Conditional Loop for Number of Syllables
        while i>0:
            syllables = [1, 2, 3, 4, 5, 6, 7, 8]
            p = [50, 50, 7.5, 7.5, 7.5, 4, .5, .5]
            rule = random.choices(syllables, weights = p)
            rule = int(rule[0])
            # rule = random.randint(0,7)
            if rule == 1 and not i == 1:
                name = name + ruleOne()
                i-=1
            elif rule == 2:
                name = name + ruleTwo()
                i-=1
            elif rule == 3:
                name = name + ruleThree()
                i-=1
            elif rule == 4:
                name = name + ruleFour()
                i-=1
            elif rule == 5:
                name = name + ruleFive()
                i-=1
            elif rule == 6:
                name = name + ruleSix()
                i-=1
            elif rule == 7:
                name = name + ruleSeven()
                i-=1
            else:
                name = name + ruleEight()
                i-=1

        # Building the Output
        name = name.replace("''", "'")
        name = name.replace("kk","k")
        name = name.replace("kxkx", "kx")
        name = name.replace("mm", "m")
        name = name.replace("nn", "n")
        name = name.replace("ngng", "ng")
        name = name.replace("pp", "p")
        name = name.replace("pxpx", "px")
        name = name.replace("tt", "t")
        name = name.replace("txtx", "tx")
        name = name.replace("yy","y")
        name = name.replace("aa", "a")
        name = name.replace("ää", "ä")
        name = name.replace("ee", "e")
        name = name.replace("ii", "i")
        name = name.replace("ìì", "ì")
        name = name.replace("oo", "o")
        name = name.replace("uu", "u")
        name = name.replace("lll","ll")
        name = name.replace("rrr","rr")
        name = name.capitalize()
        names.append(name)

        # Resetting for next loop
        name = ""
        n-=1

    # Finalizing the Output    
    n = int(numOut)
    for num in names:
        output = output + names[n-1]
        if n > 1:
            output = output + "\n"
        n -= 1
    return output

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
async def roleUpdate(count, check, message, user):
    i = 0
    activeRoles = message.guild.roles            
    for roles in activeRoleNames:
            if count >= activeRoleThresholds[i] and check.name != roles:
                    newRole = get(activeRoles, name=activeRoleNames[i])
                    await user.add_roles(newRole)
                    print('Tìmìng txintìnit alu ' + newRole.name + ' tuteru alu ' + user.display_name + '.')
                    if message.author.dm_channel is None:
                            await message.author.create_dm()
                    await message.author.send('**Seykxel sì nitram!** Set lu ngaru txintìn alu ' + newRole.name + '.')
                    if check.name != "@everyone":
                            await user.remove_roles(check)
                            print("'olaku txintìnit alu " + check.name + " ta " + user.display_name + ".")
                    break
            elif count >= activeRoleThresholds[i]:
                    break
            i += 1

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
    
##-----------------------Bot Functions--------------------##

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
        # This will automatically give anyone the 'frapo' role when they join the server.
        fileName = 'blacklist.txt'
        count = 0
        i = 0

        print(member.name + " zola'u.")
        fh = open(fileName, 'r')
        lines = fh.readlines()
        count = len(lines)
        while i < count:
                line = ''.join(lines[i])
                line.strip()
                if int(lines[i]) == member.id:
                       print("Found this user in the blacklist.")
                       if member.dm_channel is None:
                               await member.create_dm()
                       await member.send("Sorry, you are forbidden from joining this server.")
                       target = member.guild.get_member(81105065955303424)
                       name = member.name
                       await member.ban()
                       print(member.name + " was banned.")
                       await target.send(name + " attempted to join Kelutral.org.")
                       
                       break
                i += 1
        fh.close()
        
        newRole = get(member.guild.roles, name="frapo")
        await member.add_roles(newRole)
        print("Gave " + member.name + " the role " + newRole.name + ".")
        if member.dm_channel is None:
                await member.create_dm()

        embed=discord.Embed()
        embed.add_field(name="Welcome to the Kelutral.org Discord Server!", value="**Fwa ngal fìtsengti sunu ayoeru!** We are glad that you are here!\n\nWhen you get the chance, please read our rules and information channels to familiarize yourself with our code of conduct and roles. After that, please introduce yourself in #hell's-gate so that a moderator can assign you the proper role.\n\n**Zola'u nìprrte' ulte siva ko!** Welcome, let's go!", inline=False)
        await member.send(embed=embed)

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
                                      fh.write(user.name)
                                      fh.write("English")
                                      fh.close()
                                else:
                                    fh = open(fileName, "r")
                                    content = fh.readlines()
                                    strMessageCount = content[0]
                                    pref = content[2].strip()
                                    userMessageCount = int(strMessageCount)
                                    fh.close()
                                    
                                    fh = open(fileName, "w")
                                    fh.write(str(userMessageCount + 1) + "\n")
                                    fh.write(user.name + "\n")
                                    fh.write(pref)
                                    fh.close()
                                        
                                await roleUpdate(userMessageCount, currentRole, message, user)
       
        await kelutralBot.process_commands(message)
        
## Kill Command
@kelutralBot.command(name='quit', aliases=['ftang'])
async def botquit(ctx):
        user = ctx.message.author
        if user.top_role.name == "Olo'eyktan (Admin)":
                await ctx.send("Herum. Hayalovay!")
                await kelutralBot.close()
                await kelutralBot.close()
                quit()

## Version
@kelutralBot.command(name='version', aliases=['srey'])
async def version(ctx):
        displayversion = ["Version: ", versionNumber]
        await ctx.send(''.join(displayversion))

## Fuck off, LN.org
@kelutralBot.command(name='käneto', aliases=['fuckyou'])
async def goAway(ctx):
        await ctx.send("https://youtu.be/7JEbbihUCLw")

# Tskxekengsiyu functions
## Display User Message Count
@kelutralBot.command(name='level', aliases=['yì'])
async def messages(ctx, user: discord.Member):
        fileName = 'users/' + str(user.id) + '.tsk'
        fh = open(fileName, "r")
        fileContents = fh.readlines(1)
        strippedContents = fileContents[0].strip("\n")
        fh.close()
        i = 0
        langCheck = outputCheck(ctx.message.author)
        for role in activeRoleThresholds:
                if int(fileContents[0]) >= activeRoleThresholds[i]:
                        toNextLevel = activeRoleThresholds[i - 1] - int(fileContents[0])
                        break
                elif int(fileContents[0]) <= 16:
                        toNextLevel = 16 - int(fileContents[0])
                        break
                i += 1
        if langCheck.lower() == "english":
            output1 = strippedContents
            output2 = str(toNextLevel)
            embed=discord.Embed(color=0x3154cc, title=user.name, description=user.name + " has sent **" + output1 + " messages**. They need **" + output2 + " more messages** in order to reach " + activeRoleNames[i - 1])
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)
        elif langCheck.lower() == "na'vi":
            output1 = wordify(str(oct(int(strippedContents)))[2:])
            output2 = wordify(str(oct(toNextLevel))[2:])
            embed=discord.Embed(color=0x3154cc, title=user.name, description="Lu tsatuteru **" + output1 + " 'upxare**. Kin pol **" + output2 + " 'upxareti** fte slivu " + activeRoleNames[i - 1])
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Somehow, and god knows how, you fucked up.")
        

## Add a Question of the Day to a specified or the next available date
@kelutralBot.command(name='addqotd', aliases=['tìpawm'])
async def qotd(ctx, question, *date):
        langCheck = outputCheck(ctx.message.author)
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
        langCheck = outputCheck(ctx.message.author)
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
        langCheck = outputCheck(ctx.message.author)
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
        langCheck = outputCheck(ctx.message.author)
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
        langCheck = outputCheck(ctx.message.author)
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
        langCheck = outputCheck(ctx.message.author)
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

    langCheck = outputCheck(ctx.message.author)
    
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

    langCheck = outputCheck(ctx.message.author)

    if not n <= 0 and not i <= 0:
        if langCheck.lower() == "english":
            if not i <= 5:
                await ctx.send("Maximum syllable count allowed by the bot is 5. It is highly recommended that you select a name that is between 1 and 3 syllables.")
            elif not n <= 20:
                await ctx.send("Maximum name count allowed is 20.")
            else:
                output = nameGen(n, numSyllables)
                nameCount = update(n)
                game = discord.Game("ngamop " + "{:,}".format(nameCount) + " tstxoti.")
        
                await kelutralBot.change_presence(status=discord.Status.online, activity=game)

                embed=discord.Embed(color=0x00c600)
                embed.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
                embed.add_field(name="Here are your names:", value=output, inline=True)

                await ctx.send(embed=embed)
        elif langCheck.lower() == "na'vi":
            if not i <= 5:
                await ctx.send("Lì'kongä txantewä holpxay lu mrr. Sweylu txo ngal ftxivey tstxoti a lu tsa'ur lì'kong apxey, lì'kong amune, fu lìkong a'aw.")
            elif not n <= 20:
                await ctx.send("Stxoä txantxewä holpxay lu mevotsìng.")
            else:
                output = nameGen(n, numSyllables)
                nameCount = update(n)
                game = discord.Game("ngamop " + "{:,}".format(nameCount) + " tstxoti.")
        
                await kelutralBot.change_presence(status=discord.Status.online, activity=game)
                embed=discord.Embed(color=0x00c600)
                embed.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
                embed.add_field(name="Faystxo lu ngaru:", value=output, inline=True)

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

# User Preferences
@kelutralBot.command(name='language',aliases=['lì\'fya'])
async def profile(ctx, *setting):
    user = ctx.message.author
    fileName = 'users/' + str(user.id) + '.tsk'
    setting = ''.join(setting)
    preference = str(setting).lower()

    fh = open(fileName, 'r')
    content = fh.readlines()
    messages = content[0].strip()
    fh.close()
    
    # Updates the user profile.
    if preference == "":
        if profile == "Na'vi":
            embed=discord.Embed(color=0x3154cc, title=user.name, description="Nulnawnewa Lì'fya: **" + profile + "**")
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(color=0x3154cc, title=user.name, description="Language Preference: **" + profile + "**")
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)
    elif preference == "na'vi":
        fh = open(fileName, 'w')
        fh.write(messages + "\n")
        fh.write(user.name + "\n")
        fh.write(preference.capitalize() + "\n")
        fh.close()

        await ctx.send("Nulnawnewa lì'fya set lu " + preference.capitalize() + ".")
        
    elif preference == "english":
        fh = open(fileName, 'w')
        fh.write(messages + "\n")
        fh.write(user.name + "\n")
        fh.write(preference.capitalize() + "\n")
        fh.close()

        await ctx.send("Language preference updated to " + preference.capitalize() + ".")
        
    else:
        await ctx.send("Invalid criteria entered. Please select `English` or `Na'vi` to update your current settings.")

# Error Handling for !profile
@profile.error
async def profile_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send("Invalid syntax. If you need help with the `+profile` command, type `+howto`")

# Replace token with your bot's token
kelutralBot.run("private key")
