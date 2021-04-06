# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import os
import glob
import json
from datetime import datetime

import config
import kt_config
import pr_config

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

    joins1 = checkFile('kelutral-bot/files/logs/join_data/'+ date + '*.tsk')
    leaves1 = checkFile('kelutral-bot/files/logs/leave_data/'+ date + '*.tsk')
    rds1 = checkFile('kelutral-bot/files/logs/rds/'+ date + '*.tsk')
    
    return joins1, leaves1, rds1
    
def readDirectory(user, *requested_value):
    try:
        profile = config.directory[str(user.id)]
    except (IndexError, KeyError):
        profile = None
        return profile
    
    try:
        if requested_value != ():
            return profile[requested_value[0]]
        else:
            return profile
    except KeyError:
        return profile

def writeDirectory(user, index, value):
    profile = config.directory[str(user.id)]
    profile[index] = value
    
    with open(config.directoryFile, 'w', encoding='utf-8') as fh:
        json.dump(config.directory, fh)

def updateDirectory():
    with open(config.directoryFile, 'w', encoding='utf-8') as fh:
        json.dump(config.directory, fh)
    
    config.directory = config.reloadDir()
    
async def roleUpdate(user, ctx):
    i = 0
    guild = user.guild
    activeRoles = user.guild.roles
    
    # Retrieves the user profile
    profile = readDirectory(user)
    
    # Unpacks the relevant parts of the user profile
    message_count = profile['message count']
    language_pref = profile['language']
    
    if guild.id == kt_config.guild:
        # Retrieves the current and next rank
        current_rank = get(activeRoles, id=profile['rank']['id'])
        next_rank_index = kt_config.activeRoleIDs.index(current_rank.id) - 1
        next_rank = get(activeRoles, id=kt_config.activeRoleIDs[next_rank_index])
        
        now = datetime.strftime(datetime.now(), '%H:%M')
        if message_count >= kt_config.activeRoleThresholds[next_rank_index]:
            await user.add_roles(next_rank)
            if current_rank.id != kt_config.frapoID:
                await user.remove_roles(current_rank)
                config.log(now + ' -- Gave ' + user.name + ' the ' + next_rank.name + ' role and removed the ' + current_rank.name + ' role.')
            else:
                config.log(now + ' -- Gave ' + user.name + ' the ' + next_rank.name + ' role.')
            
            if language_pref == "English":
                embed=discord.Embed(color=config.rankColor)
                embed.add_field(name="New Rank Achieved on Kelutral.org", value="**Congratulations!** By participating in the community, you've leveled up! You're now a " + next_rank.name + " (" + kt_config.activeRoleDict[next_rank_index][1] + ").", inline=False)
                embed.set_thumbnail(url=user.guild.icon_url)
            elif language_pref == "Na'vi":
                embed=discord.Embed(color=config.rankColor)
                embed.add_field(name="Mipa txìntin lu ngaru mì Helutral.org", value="**Seykxel si nitram!** Nga slolu " + next_rank.name + ".", inline=False)
                embed.set_thumbnail(url=user.guild.icon_url)
            
            try:
                if user.dm_channel is None:
                    await user.create_dm()
                await user.send(embed=embed)
            except:
                config.log(now + ' -- Cannot DM this user.')
            
            # Updates the directory count.
            profile['rank'] = {
                "id" : kt_config.activeRoleDict[next_rank_index][0],
                "translation" : kt_config.activeRoleDict[next_rank_index][1]
                }
            
    elif guild.id == pr_config.guild:
        # Retrieves the current and next rank
        current_rank = get(activeRoles, id=profile['pr_rank']['id'])
        if current_rank == None:
            return
        else:
            current_rank_index = pr_config.activeRoleIDs.index(current_rank.id)
            for threshold in pr_config.activeRoleThresholds:
                if message_count > threshold:
                    next_rank_index = pr_config.activeRoleThresholds.index(threshold)
                    break
            next_rank = get(activeRoles, id=pr_config.activeRoleIDs[next_rank_index])
            
            now = datetime.strftime(datetime.now(), '%H:%M')
            if message_count >= pr_config.activeRoleThresholds[next_rank_index] and current_rank_index != next_rank_index:
                await user.add_roles(next_rank)
                if current_rank.id != pr_config.defaultID and current_rank.id != next_rank.id:
                    await user.remove_roles(current_rank)
                    config.log(now + ' -- Gave ' + user.name + ' the ' + next_rank.name + ' role and removed the ' + current_rank.name + ' role.')
                else:
                    config.log(now + ' -- Gave ' + user.name + ' the ' + next_rank.name + ' role.')
                
                if language_pref == "English":
                    embed=discord.Embed(color=config.rankColor)
                    embed.add_field(name="New Rank Achieved", value="**Congratulations!** By participating in the community, you've leveled up! You're now " + next_rank.name + ".", inline=False)
                    embed.set_thumbnail(url=user.guild.icon_url)
                    embed.set_footer(text=f"Use !profile @{user.name} to check your progress to the next rank.")
                elif language_pref == "Na'vi":
                    embed=discord.Embed(color=config.rankColor)
                    embed.add_field(name="Mipa txìntin lu ngaru", value="**Seykxel si nitram!** Nga slolu " + next_rank.name + ".", inline=False)
                    embed.set_thumbnail(url=user.guild.icon_url)
                
                await ctx.send(embed=embed)
                
                # Updates the directory count.
                profile['pr_rank'] = {
                    "id" : pr_config.activeRoleIDs[next_rank_index]
                    }
            
    with open(config.directoryFile, 'w', encoding='utf-8') as fh:
        json.dump(config.directory, fh)
        
    config.directory = config.reloadDir()
        
async def adminMsgs(ctx, bot, guild):
    user = ctx.message.author
    rulesChannel = 715727832063410207
    infoChannel = 715049168984473671
    resourcesChannel = 715050231967776778
    if user.top_role.name == "Olo'eyktan (Admin)":
        oloEyktan = 715044138864607334
        Eyktan = 715048580334878732
        Karyu = 715044889049563147
        Numeyu = 715044972436389890
        Eylan = 715048542468833321

        pre = ["Mod Roles: \n",
               "{} : Administrators, responsible for upkeep of the Kelutral network of resources.\n".format(ctx.guild.get_role(oloEyktan).mention),
               "{} : Moderators, responsible for monitoring content in the Kelutral Discord.\n".format(ctx.guild.get_role(Eyktan).mention),
               "\nNa'vi Language: \n",
               "{} : Teacher, a capable, volunteer teacher who has shown willingness to share their knowledge of the Na'vi Language with other learners.\n".format(ctx.guild.get_role(Karyu).mention),
               "{} : Someone who is learning the Na'vi language.\n".format(ctx.guild.get_role(Numeyu).mention),
               "\nOther Roles: \n",
               "{} : Avatar enthusiasts who don't want learner notifications, or friends of the community.\n".format(ctx.guild.get_role(Eylan).mention)]
               
        value = ""
        
        for line in pre:
            value = value + line
        
        embeda = discord.Embed(title="Role Descriptions\n――――――――――", description=value, color=config.reportColor)    
        
        path1 = 'kelutral-bot/files/info1.txt'
        path2 = 'kelutral-bot/files/info2.txt'
        
        serverInfo = ["{} - Rules".format(guild.get_channel(rulesChannel).mention),
                      "• Explains our community values, and the rules that arise from them.\n",
                      "{} - Information".format(guild.get_channel(715049168984473671).mention),
                      "• You're here!",
                      "• Translations and explanations of roles and channels.\n",
                      "{} - Hello".format(guild.get_channel(718309284705861647).mention),
                      "• A space for new members to introduce themselves and get assigned appropriate roles based on whether they want to receive notifications for learners (such as class meetups, new vocabulary, etc.)\n",
                      "{} - News".format(guild.get_channel(715049263842721792).mention),
                      "• News concerning Kelutral, new Na'vi vocabulary, and other AVATAR happenings.\n",
                      "{} - Suggestions".format(guild.get_channel(715314466312683612).mention),
                      "• Suggestions or other help requests from the community can be asked here.\n",
                      "{} - Bot Spam".format(guild.get_channel(718309398048538687).mention),
                      "• The channel to use spammy commands like `!generate` or `!leaderboard`.\n",
                      "{}".format(guild.get_channel(740554812961325129).mention),
                      "• A daily countdown to the release of AVATAR 2, courtesy of the Based Counter **Calzone**.\n",
                      "{}".format(guild.get_channel(746446354196201553).mention),
                      "• News and releases from other AVATAR fan projects.\n"]
        
        value1 = ""
        for entry in serverInfo:
            value1 = value1 + entry + "\n"
            
        embedb = discord.Embed(title="{}\n――――――――――".format(guild.get_channel(715048353876017252).name), description=value1, color=config.reportColor)
        
        naviLanguage = ["{} - Useful Tools".format(guild.get_channel(715050231967776778).mention),
                        "• Links to useful resources for learners.\n",
                        "{} - Lessons".format(guild.get_channel(801460980805664778).mention),
                        "• Lesson signup and scheduling.\n",
                        "{} - Classroom".format(guild.get_channel(715046084837376061).mention),
                        "• A place for learners to ask questions, practice, and help others learn the Na'vi language.\n"
                        "{} - In Na'vi Only".format(guild.get_channel(715050499203661875).mention),
                        "• A place for learners to hone their skills in a Na'vi-only environment.",
                        "• Non-Na'vi messages will be deleted without warning.\n",
                        "{} - Let's Go!".format(guild.get_channel(724724850278531103).mention),
                        "• Community challenges, meant to encourage participation and practice.\n",
                        "{}".format(guild.get_channel(715050363740487782).mention),
                        "• A place for requesting translations, or help with finding vocabulary or alternate wordings.\n",
                        "{}".format(guild.get_channel(config.lepChannel).mention),
                        "• Anonymous discussion of proposed words to be submitted to the Lexical Expansion Project (LEP), the committee responsible for filtering submissions and forwarding them to Karyu Pawl for approval.\n"]
                        
        value2 = ""
        for entry in naviLanguage:
            value2 = value2 + entry + "\n"
            
        embedc = discord.Embed(title="{}\n――――――――――".format(guild.get_channel(715049915524448316).name), description=value2, color=config.reportColor)
        
        hobbies = ["{} - Conversation".format(guild.get_channel(715296162394931340).mention),
                   "• General chat! Any topic of discussion is allowed here in any language, so long as it does not violate our rules or belong in another channel.\n",
                   "{} - Concerning AVATAR".format(guild.get_channel(778777008699473930).mention),
                   "• Chat and discussion about the AVATAR franchise specifically.\n",
                   "{} - Games".format(guild.get_channel(715046135357636652).mention),
                   "• Discussion of all varieties of games belong here.\n"
                   "{} - Art".format(guild.get_channel(715051480293572669).mention),
                   "• Share and discuss artworks of all kinds. Please limit it to artwork you have personally created.\n",
                   "{} - Computers".format(guild.get_channel(718841083718795354).mention),
                   "• For conversations about computers, programming, or computer science.\n",
                   "{} - Science".format(guild.get_channel(715301718967058496).mention),
                   "• For conversations surrounding anything science or mathematics related.\n",
                   "{} - Beloved Creatures".format(guild.get_channel(715344553204514817).mention),
                   "• Photos and discussion of plants and animals, such as pets.\n",
                   "{} - Constructed Languages".format(guild.get_channel(790362808332058674).mention),
                   "• Discussion of Constructed Languages (conlangs) that aren't the Na'vi language.\n",
                   "{} - Mature Art (**18+ Only**)".format(guild.get_channel(751162981957501089).mention),
                   "• For tasteful, mature art and anatomy studies. Pornography is *strictly* forbidden and will result in an immediate ban.\n"]
                   
        value3 = ""
        for entry in hobbies:
            value3 = value3 + entry + "\n"
        
        embedd = discord.Embed(title="{}\n――――――――――".format(guild.get_channel(715043968886505485).name), description=value3, color=config.reportColor)
        
        partnered = ["{}".format(guild.get_channel(788100741494472765).mention),
                    "• Community hub for partnered servers.\n"]
        
        value5 = ""
        for entry in partnered:
            value5 = value5 + entry + "\n"
            
        embedg = discord.Embed(title="{}\n――――――――――".format(guild.get_channel(788100626361090171).name), description=value5, color=config.reportColor)
        
        other_languages = ["{}".format(guild.get_channel(718237500216442902).mention),
                           "• German / Deutsch\n",
                           "{}".format(guild.get_channel(737445777508401273).mention),
                           "• French / Français\n",
                           "{}".format(guild.get_channel(743531137586167913).mention),
                           "• Dutch / Nederlands\n",
                           "{}".format(guild.get_channel(773157380644405299).mention),
                           "• Spanish / Español\n"]
                           
        value6 = ""
        for entry in other_languages:
            value6 = value6 + entry + "\n"
            
        embedh = discord.Embed(title="{}\n――――――――――".format(guild.get_channel(718237458994561044).name), description=value6, color=config.reportColor)
        
        voice = ["{} - Voice".format(guild.get_channel(715290369314521099).mention),
                 "• For text communication with voice channels, for when you are unable to speak.",
                 "• Should also be used for sharing relevant images or links during conversation.\n",
                 "{} - Converse".format(guild.get_channel(715060309836169300).mention),
                 "• General conversation channel. If it doesn't belong in the other channels, it goes here.\n"
                 "{} - Classroom".format(guild.get_channel(715060388517118023).mention),
                 "• Voice channel for lessons and practice .\n",
                 "{} - In Na'vi Only".format(guild.get_channel(715060555013947492).mention),
                 "• For those who want to practice in Na'vi-only.\n",
                 "{} - Play a Game".format(guild.get_channel(737748050445074623).mention),
                 "• For those who want to play games together.\n",
                 "{} - Hammock".format(guild.get_channel(740378369413087393).mention),
                 "• The AFK timeout channel.\n"]
                 
        value4 = ""
        for entry in voice:
            value4 = value4 + entry + "\n"
            
        embede = discord.Embed(title="{}\n――――――――――".format(guild.get_channel(715048420691148830).name), description=value4, color=config.reportColor)
        
        games = ["{} - Word Game".format(guild.get_channel(757026975696027688).mention),
                 "• A game in which you try to think of a word that begins with the last letter of the previously submitted word. Use `?help wordgame` for more info.\n",
                 "{} - Word Test".format(guild.get_channel(757082428673228838).mention),
                 "• Your standard vocabulary quiz game. Use `!help quiz` for more info.\n"]
                 
        value7 = ""
        for entry in games:
            value7 = value7 + entry + "\n"
            
        embedi = discord.Embed(title="{}\n――――――――――".format(guild.get_channel(757026924307415086).name), description=value7, color=config.reportColor)
        
        after_hours = ["{}".format(guild.get_channel(759900745733505024).mention),
                       "• A channel for mature discussion. (**18+ Only**) It carries its own set of rules, which are pinned in the channel.\n",
                       "{}".format(guild.get_channel(759896770988998687).mention),
                       "• Corresponding voice channel for the After Hours channel.\n"]
                       
        value8 = ""
        for entry in after_hours:
            value8 = value8 + entry + "\n"
            
        embedj = discord.Embed(title="{}\n――――――――――".format(guild.get_channel(759900601403834419).name), description=value8, color=config.reportColor)
        
        changeLog = "12/22/2020 - Added the conlangs channel to the channel descriptions.\n12/14/2020 - Merged the Roleplay section into the new Partnered Servers section."
        
        embedf = discord.Embed(title="What's Changed (Why are there notifications?)\n――――――――――", description=changeLog, color=config.reportColor)
        
        servInfo = ["The **Kelutral.org** Discord has several unique features thanks to our custom coded bot, {}.".format(ctx.guild.get_member(config.botID).mention),
                    "\n\nWhile you are here, you will rank up through a series of ranks by participating in the community. You can check your progress to the next rank by using `!profile @yourself` in {}.".format(guild.get_channel(718309398048538687).mention),
                    "\n\nOur server features a 'karma' system, where you can give people karma by adding <:irayo:766299908159701043> to their message.",
                    "\n\nUpdates from around the Na'vi Language community can be found in {}.".format(guild.get_channel(746446354196201553).mention)
                    ]
        
        value9 = ""
        for entry in servInfo:
            value9 = value9 + entry + "\n"
            
        embedk = discord.Embed(title="Server Information\n――――――――――", description=value9, color=config.reportColor)

        channel = guild.get_channel(infoChannel)

        await channel.send(embed=embedk)
        await channel.send(embed=embeda)
        await channel.send(embed=embedg)
        await channel.send(embed=embedb)
        await channel.send(embed=embedc)
        await channel.send(embed=embedd)
        await channel.send(embed=embedh)
        await channel.send(embed=embede)
        await channel.send(embed=embedi)
        await channel.send(embed=embedj)
        await channel.send(embed=embedf)