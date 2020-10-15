# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import os
import glob
from datetime import datetime

import json

import config

## -- Variables

kelutralBot = commands.Bot(command_prefix=config.prefix)

## -- Functions

def getStats(date): 
    def checkFile(path):
        stat1 = 0
        fileList = []
        for file in glob.glob(path):
            fileList.append(file)
        for file in fileList:
            if os.path.exists(file):
                with open(file, 'r', encoding='utf-8') as fh:
                    stat = fh.read()
                    stat1 = stat1 + int(stat)
            else:
                stat = stat
        
        return stat1

    joins1 = checkFile('files/logs/join_data/'+ date + '*.tsk')
    leaves1 = checkFile('files/logs/leave_data/'+ date + '*.tsk')
    rds1 = checkFile('files/logs/rds/'+ date + '*.tsk')
    
    return joins1, leaves1, rds1

def getProfile(user):
    for entry in config.directory:
        if entry[0] == user.id:
            profile = entry
            return profile
        else:
            profile = None
            
    return profile

def checkPronouns(message, user):
    pronounsRole = ['He/Him', 'She/Her', 'They/Them']
    n = 0
        
    while n < len(pronounsRole):
        role = discord.utils.find(lambda r: r.name == pronounsRole[n], message.guild.roles)
        if role in user.roles:
            pronouns = pronounsRole[n]
            break
        else:
            pronouns = "Unspecified"
            n += 1
    
    return pronouns
                    
async def roleUpdate(user):
    i = 0
    activeRoles = user.guild.roles
    
    # Retrieves the user profile
    profile = getProfile(user)
    
    # Unpacks the relevant parts of the user profile
    message_count = profile[1]
    language_pref = profile[3]
    
    # Retrieves the current and next rank
    current_rank = get(activeRoles, id=profile[5][0])
    next_rank_index = config.activeRoleIDs.index(current_rank.id) - 1
    next_rank = get(activeRoles, id=config.activeRoleIDs[next_rank_index])
    
    now = datetime.strftime(datetime.now(), '%H:%M')
    if message_count >= config.activeRoleThresholds[next_rank_index]:
        await user.add_roles(next_rank)
        await user.remove_roles(current_rank)
        print(now + ' -- Gave ' + user.name + ' the ' + next_rank.name + ' role and removed the ' + current_rank.name + ' role.')
        
        if language_perf == "English":
            embed=discord.Embed(colour=config.rankColor)
            embed.add_field(name="New Rank Achieved on Kelutral.org", value="**Congratulations!** By participating in the community, you've leveled up! You're now a " + newRole.name + " (" + config.activeRoleTranslations[i] + ").", inline=False)
            embed.set_thumbnail(url=ctx.guild.icon_url)
        elif language_perf == "Na'vi":
            embed=discord.Embed(colour=config.rankColor)
            embed.add_field(name="Mipa txìntin lu ngaru mì Helutral.org", value="**Seykxel si nitram!** Nga slolu " + newRole.name + ".", inline=False)
            embed.set_thumbnail(url=ctx.guild.icon_url)
        
        try:
            if user.dm_channel is None:
                await user.create_dm()
            await message.author.send(embed=embed)
        except:
            print(now + ' -- Cannot DM this user.')
        
        # Updates the directory count.
        for entry in config.directory:
            if user.id == entry[0]:
                entry[5] = config.activeRoleDict[next_rank_index]
        
        with open(config.directoryFile, 'w', encoding='utf-8') as fh:
            json.dump(config.directory, fh)
            
        config.directory = config.reloadDir()
        
async def adminMsgs(ctx, bot):
    user = ctx.message.author
    rulesChannel = 715727832063410207
    infoChannel = 715049168984473671
    resourcesChannel = 715050231967776778
    if user.top_role.name == "Olo'eyktan (Admin)":
        path1 = 'files/rules1.txt'
        path2 = 'files/rules2.txt'
        path3 = 'files/rules3.txt'

        fh = open(path1, 'r', encoding='utf-8')
        file1 = fh.read()
        fh.close()

        fh = open(path2, 'r', encoding='utf-8')
        file2 = fh.read()
        fh.close()

        fh = open(path3, 'r', encoding='utf-8')
        file3 = fh.read()
        fh.close()

        channel = bot.get_channel(rulesChannel)

        await channel.send(file1)
        await channel.send(file2)
        await channel.send(file3)

        oloEyktan = 715044138864607334
        Eyktan = 715048580334878732
        Karyu = 715044889049563147
        Numeyu = 715044972436389890
        Eylan = 715048542468833321

        pre = ["{} : Administrators, responsible for upkeep of the Kelutral network of resources.\n".format(ctx.guild.get_role(oloEyktan).mention),
               "{} : Moderators, responsible for monitoring content in the Kelutral Discord.\n".format(ctx.guild.get_role(Eyktan).mention),
               "\n",
               "{} : Teacher, a capable, volunteer teacher who has shown willingness to share their knowledge of the Na'vi Language with other learners.\n".format(ctx.guild.get_role(Karyu).mention),
               "\n",
               "{} : Someone who is learning the Na'vi language.\n".format(ctx.guild.get_role(Numeyu).mention),
               "{} : Inactive or non-language-learning Avatar enthusiasts.\n".format(ctx.guild.get_role(Eylan).mention)]
               
        value = ""
        
        for line in pre:
            value = value + line
        
        embeda = discord.Embed(title="Role Descriptions\n――――――――――――――――――――――――――――――", description=value, color=config.reportColor)    
        
        path1 = 'files/info1.txt'
        path2 = 'files/info2.txt'
        
        serverInfo = ["{} - Rules".format(bot.get_channel(rulesChannel).mention),
                      "• Explains our community values, and the rules that arise from them.\n",
                      "{} - Information".format(bot.get_channel(715049168984473671).mention),
                      "• You're here!",
                      "• Translations and explanations of roles and channels.\n",
                      "{} - Hello".format(bot.get_channel(718309284705861647).mention),
                      "• A space for new members to introduce themselves and get assigned appropriate roles based on whether they want to receive notifications for learners (such as class meetups, new vocabulary, etc.)\n",
                      "{} - News".format(bot.get_channel(715049263842721792).mention),
                      "• News concerning Kelutral, new Na'vi vocabulary, and other AVATAR happenings.\n",
                      "{} - Suggestions".format(bot.get_channel(715314466312683612).mention),
                      "• Suggestions or other help requests from the community can be asked here.\n",
                      "{} - Bot Spam".format(bot.get_channel(718309398048538687).mention),
                      "• The channel to use spammy commands like `!generate` or `!leaderboard`.\n",
                      "{}".format(bot.get_channel(740554812961325129).mention),
                      "• A daily countdown to the release of AVATAR 2, courtesy of the Based Counter **Calzone**.\n",
                      "{}".format(bot.get_channel(746446354196201553).mention),
                      "• News and releases from other AVATAR fan projects.\n"]
        
        value1 = ""
        for entry in serverInfo:
            value1 = value1 + entry + "\n"
            
        embedb = discord.Embed(title="{}\n――――――――――――――――――――――――――――――".format(bot.get_channel(715048353876017252).name), description=value1, color=config.reportColor)
        
        naviLanguage = ["{} - Lessons".format(bot.get_channel(715050231967776778).mention),
                        "• Links to useful resources for learners.\n",
                        "{} - Classroom".format(bot.get_channel(715046084837376061).mention),
                        "• A place for learners to ask questions, practice, and help others learn the Na'vi language.\n"
                        "{} - In Na'vi Only".format(bot.get_channel(715050499203661875).mention),
                        "• A place for learners to hone their skills in a Na'vi-only environment.",
                        "• Non-Na'vi messages will be deleted without warning.\n",
                        "{} - Let's Go!".format(bot.get_channel(724724850278531103).mention),
                        "• Community challenges, meant to encourage participation and practice.\n",
                        "{}".format(bot.get_channel(715050363740487782).mention),
                        "• A place for requesting translations, or help with finding vocabulary or alternate wordings.\n",
                        "{}".format(bot.get_channel(715988382706303038).mention),
                        "• Anonymous discussion of proposed words to be submitted to the LEP.\n"]
                        
        value2 = ""
        for entry in naviLanguage:
            value2 = value2 + entry + "\n"
            
        embedc = discord.Embed(title="{}\n――――――――――――――――――――――――――――――".format(bot.get_channel(715049915524448316).name), description=value2, color=config.reportColor)
        
        hobbies = ["{} - Conversation".format(bot.get_channel(715296162394931340).mention),
                   "• General chat! Any topic of discussion is allowed here in any language, so long as it does not violate our rules or belong in another channel.\n",
                   "{} - Games".format(bot.get_channel(715046135357636652).mention),
                   "• Discussion of all varieties of games belong here.\n"
                   "{} - Art".format(bot.get_channel(715051480293572669).mention),
                   "• Share and discuss artworks of all kinds. Please limit it to artwork you have personally created.\n",
                   "{} - Science".format(bot.get_channel(715301718967058496).mention),
                   "• For conversations surrounding anything science or mathematics related.\n",
                   "{} - Beloved Creatures".format(bot.get_channel(715344553204514817).mention),
                   "• Photos and discussion of plants and animals, such as pets.\n",
                   "{} - Mature Art (**18+ Only**)".format(bot.get_channel(751162981957501089).mention),
                   "• For tasteful, mature art and anatomy studies. Pornography is *strictly* forbidden and will result in an immediate ban.\n"]
                   
        value3 = ""
        for entry in hobbies:
            value3 = value3 + entry + "\n"
        
        embedd = discord.Embed(title="{}\n――――――――――――――――――――――――――――――".format(bot.get_channel(715043968886505485).name), description=value3, color=config.reportColor)
        
        roleplay = ["{}".format(bot.get_channel(739559785665396828).mention),
                    "• Community hub for Roleplay servers.\n"]
        
        value5 = ""
        for entry in roleplay:
            value5 = value5 + entry + "\n"
            
        embedg = discord.Embed(title="{}\n――――――――――――――――――――――――――――――".format(bot.get_channel(739559504097837169).name), description=value5, color=config.reportColor)
        
        other_languages = ["{}".format(bot.get_channel(718237500216442902).mention),
                           "• German / Deutsch\n",
                           "{}".format(bot.get_channel(737445777508401273).mention),
                           "• French / Français\n",
                           "{}".format(bot.get_channel(743531137586167913).mention),
                           "• Dutch / Nederlands\n"]
                           
        value6 = ""
        for entry in other_languages:
            value6 = value6 + entry + "\n"
            
        embedh = discord.Embed(title="{}\n――――――――――――――――――――――――――――――".format(bot.get_channel(718237458994561044).name), description=value6, color=config.reportColor)
        
        voice = ["{} - Voice".format(bot.get_channel(715290369314521099).mention),
                 "• For text communication with voice channels, for when you are unable to speak.",
                 "• Should also be used for sharing relevant images or links during conversation.\n",
                 "{} - Converse".format(bot.get_channel(715060309836169300).mention),
                 "• General conversation channel. If it doesn't belong in the other channels, it goes here.\n"
                 "{} - Classroom".format(bot.get_channel(715060388517118023).mention),
                 "• Voice channel for lessons and practice .\n",
                 "{} - In Na'vi Only".format(bot.get_channel(715060555013947492).mention),
                 "• For those who want to practice in Na'vi-only.\n",
                 "{} - Play a Game".format(bot.get_channel(737748050445074623).mention),
                 "• For those who want to play games together.\n",
                 "{} - Hammock".format(bot.get_channel(740378369413087393).mention),
                 "• The AFK timeout channel.\n"]
                 
        value4 = ""
        for entry in voice:
            value4 = value4 + entry + "\n"
            
        embede = discord.Embed(title="{}\n――――――――――――――――――――――――――――――".format(bot.get_channel(715048420691148830).name), description=value4, color=config.reportColor)
        
        games = ["{} - Word Game".format(bot.get_channel(757026975696027688).mention),
                 "• A game in which you try to think of a word that begins with the previously submitted word. Use `?help wordgame` for more info.\n",
                 "{} - Word Test".format(bot.get_channel(757082428673228838).mention),
                 "• Your standard vocabulary quiz game. Use `!help quiz` for more info.\n"]
                 
        value7 = ""
        for entry in games:
            value7 = value7 + entry + "\n"
            
        embedi = discord.Embed(title="{}\n――――――――――――――――――――――――――――――".format(bot.get_channel(757026924307415086).name), description=value7, color=config.reportColor)
        
        after_hours = ["{}".format(bot.get_channel(759900745733505024).mention),
                       "• A channel for mature discussion. (**18+ Only**) It carries its own set of rules, which are pinned in the channel.\n",
                       "{}".format(bot.get_channel(759896770988998687).mention),
                       "• Corresponding voice channel for the After Hours channel.\n"]
                       
        value8 = ""
        for entry in after_hours:
            value8 = value8 + entry + "\n"
            
        embedj = discord.Embed(title="{}\n――――――――――――――――――――――――――――――".format(bot.get_channel(759900601403834419).name), description=value8, color=config.reportColor)
        
        changeLog = "10/5/2020 - Updated the channel formatting and added new channels."
        
        embedf = discord.Embed(title="What's Changed (Why are there notifications?)\n――――――――――――――――――――――――――――――", description=changeLog, color=config.reportColor)

        channel = bot.get_channel(infoChannel)

        # await channel.send(embed=embeda)
        # await channel.send(embed=embedb)
        # await channel.send(embed=embedc)
        # await channel.send(embed=embedd)
        # await channel.send(embed=embedg)
        # await channel.send(embed=embedh)
        # await channel.send(embed=embede)
        # await channel.send(embed=embedi)
        # await channel.send(embed=embedj)
        # await channel.send(embed=embedf)
        
        # path1 = 'files/resources1.txt'
        # path2 = 'files/resources2.txt'
        # path3 = 'files/resources3.txt'
        # path4 = 'files/resources4.txt'

        # fh = open(path1, 'r', encoding="utf-8")
        # file1 = fh.read()
        # fh.close()

        # fh = open(path2, 'r', encoding="utf-8")
        # file2 = fh.read()
        # fh.close()

        # channel = bot.get_channel(resourcesChannel)

        # await channel.send(file1)
        # await channel.send(file2)
        
        # fh = open(path3, 'r', encoding="utf-8")
        # file1 = fh.read()
        # fh.close()
        
        # fh = open(path4, 'r', encoding="utf-8")
        # file2 = fh.read()
        # fh.close()
        
        # await channel.send(file1)
        # await channel.send(file2)
