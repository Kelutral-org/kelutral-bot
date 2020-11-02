import discord
from discord.ext import commands
import bot
import config
import admin

import sys
import re
import json
import time
import git
import os
from datetime import datetime
from importlib import reload

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ## About the bot
    @commands.command(name='about', aliases=['teri'])
    async def about(self, ctx):
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
    @commands.command(name='ban', aliases=['yitx'])
    async def ban(self, ctx, user: discord.Member):
        if user.top_role.id in config.modRoles: # If the user is allowed to use this command
            await user.ban()
            embed=discord.Embed(description=str(user.mention) + "** was banned**", colour=config.failColor)
            await ctx.send(embed=embed)

    ## Update Rules
    @commands.command(name='donotuse')
    async def updateRules(self, ctx):
        user = ctx.message.author
        if user.top_role.id == config.adminID:
            await admin.adminMsgs(ctx, bot)

    ## Debug toggle
    @commands.command(name='debug')
    async def debugToggle(self, ctx):
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

    ## FAQ Command
    @commands.command(name="faq",aliases=['sìpawm'])
    async def faq(self, ctx, *topic):
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

    ## Fixes a directory entry
    @commands.command(name='fix')
    async def fixDirectory(self, ctx, user: discord.Member, attribute, newVal):
        if ctx.message.author.top_role.id in config.modRoles:
            admin.writeDirectory(user, attribute, newVal)
            admin.updateDirectory()
            await ctx.send("Updated!")

    ## Kill Command
    @commands.command(name='quit', aliases=['ftang'])
    async def botquit(self, ctx):
        user = ctx.message.author

        if user.top_role.id == config.adminID:
            embed=discord.Embed(description="Shutting down...", colour=config.failColor)
            await ctx.send(embed=embed)
            await self.bot.close()
            quit()
        else:
            await ctx.send(embed=config.denied)

    ## Reload command
    @commands.command(name='reload')
    async def reloadBot(self, ctx):
        if ctx.message.author.top_role.id == config.adminID:
            await ctx.send("Reloading the bot...")
            reload(config)
            await ctx.send("Launching bot version {}".format(config.version))
            await self.bot.close()
            os.execv(sys.executable, ['python3'] + sys.argv)

    ## Search command
    @commands.command(name="search")
    async def search(self, ctx, *words):
        user = ctx.message.author
        
        word_list = []
        i = 0
        for word in words:
            check_word = re.search(r"si|s..i|s...i", word)
            if check_word != None:
                if len(word_list) == 0:
                    word_list.append(word)
                else:
                    word_list[i-1] += " {}".format(word)
                    i -= 1
            else:
                word_list.append(word)
            i += 1
                
        with open('files/dictionary.json', 'r', encoding='utf-8') as fh:
            dictionary = json.load(fh)    
        
        def stripAffixes(word):
            parsed_word = {}
            mod = ""
            output = ""
            cases = {
                "agentive" : ["l\Z","ìl\Z"],
                "patientive" : ["t\Z","ti\Z","it\Z"],
                "dative" : ["r\Z","ur\Z","ru\Z"],
                "genitive" : ["ä\Z","yä\Z"],
                "topical" : ["ri\Z","ìri\Z"]
                }
            
            infixes = [{"general past" : 'am'},{"near past" : 'ìm'},{"general future" : 'ay'},{"near future" : 'ìy'},{"general future intent" : 'asy'},{"near future intent" : 'ìsy'},{"general past perfective" : 'alm'},{"near past perfective" : 'ìlm'},{"general future perfective" : 'aly'},{"near future perfective" : 'ìly'},{"general past progressive" : 'arm'},{"near past progressive" : 'ìrm'},{"general future progressive" : 'ary'},{"near future progressive" : 'ìry'},{"positive mood" : 'ei'},{"negative mood" : 'äng'},{"perfective" : 'ol'},{"progressive" : 'er'},{"progressive participle" : 'us'},{"passive participle" : 'awn'}]
            
            isverb = False
            isnoun = False
            isadj = False
            try:
                check = re.search(r"\s", word)
                if check != None:
                    isverb = True
                dictionary[word]
                core_word = word
                parsed_word[word] = {"stripped" : core_word, "notes" : ""}
            except KeyError:
                # Noun Checking
                if not isverb:
                    for key, value in cases.items():
                        for suffix in value:
                            case = re.search(r""+suffix, word)
                            if case != None:
                                isnoun = True
                                core_word = re.sub(r""+suffix, '', word)
                                case_name = key
                                parsed_word[word] = {"stripped" : core_word, "notes" : ": {}".format(case_name)}
                                break
                # Verb Checking
                if not isnoun:
                    isverb = False
                    if " s.i " in word:
                        for infix in infixes:
                            if not isverb:
                                for key, value in infix.items():
                                    verb = re.search(r"s"+value+"i", word)
                                    if verb != None:
                                        isverb = True
                                        core_word = re.sub(r"s"+value+"i", 'si', word)
                                        tense = key
                                        parsed_word[word] = {"stripped" : core_word, "notes" : ": {}".format(tense)}
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
                                        parsed_word[word] = {"stripped" : core_word, "notes" : ": {}".format(tense)}
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
                        parsed_word[word] = {"stripped" : core_word, "notes" : ""}

            return parsed_word
        
        results = ''
        for i, word in enumerate(word_list):
            found = False
            try:
                word_entry = dictionary[word.lower()]
                found = True
                if len(word_entry) > 1:
                    alphabet = ['a','b','c','d','e']
                    results += "`{}.` **{}** has multiple definitions: \n".format(i+1, word)
                    for j, sub in enumerate(word_entry):
                        results += "`     {}.` **{}** *{}* {}\n".format(alphabet[j], word, sub['partOfSpeech'], sub['translation'])
                else:
                    results += "`{}.` **{}** *{}* {}\n".format(i+1, word, word_entry[0]['partOfSpeech'], word_entry[0]['translation'])
            except KeyError:
                for key, value in dictionary.items():
                    for k, sub in enumerate(value):
                        x = re.search(r"\b"+word+"$", sub['translation'])
                        y = re.search(r"\b"+word+"[,]", sub['translation'])
                        if x != None or y != None:
                            found = True
                            results += "`{}.` **{}** *{}* {}\n".format(i+1, key, sub['partOfSpeech'], sub['translation'])
            
            if not found:
                parsed_word = stripAffixes(word)
                try:
                    word_entry = dictionary[parsed_word[word]["stripped"].lower()]
                    found = True
                    if len(word_entry) > 1:
                        alphabet = ['a','b','c','d','e']
                        results += "`{}.` **{}** has multiple definitions: \n".format(i+1, parsed_word[word]["stripped"])
                        for j, sub in enumerate(word_entry):
                            results += "`     {}.` **{}** *{}* {} {} \nOriginal: **{}**\n".format(alphabet[j], word, sub['partOfSpeech'], sub['translation'], parsed_word[word]["notes"], parsed_word[word]["stripped"])
                    else:
                        results += "`{}.` **{}** *{}* {} {}\nOriginal: **{}**\n".format(i+1, word, word_entry[0]['partOfSpeech'], word_entry[0]['translation'], parsed_word[word]["notes"], parsed_word[word]["stripped"])
                except KeyError: 
                    results += "`{}.` **{}** not found.\n".format(i+1, word_list[i])
                
            results += "\n"

        embed = discord.Embed(title="Search Results:", description=results, color=config.reportColor)
        await ctx.send(embed=embed)

    ## Server information
    @commands.command(name='serverinfo')
    async def serverInfo(self, ctx):
        guild = ctx.guild
        
        embed = discord.Embed(color=config.reportColor)
        embed.set_author(name=guild.name, icon_url=guild.icon_url)
        embed.add_field(name="Owner", value=guild.owner, inline=True)
        embed.add_field(name="Region", value=guild.region, inline=True)
        embed.add_field(name="Channel Categories", value=len(guild.categories), inline=True)
        embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="Members", value=len([m for m in guild.members if not m.bot]), inline=True)
        embed.add_field(name="Bots", value=len([m for m in guild.members if m.bot]), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.set_footer(text="ID: {} | Server Created: {}".format(guild.id, guild.created_at.strftime("%m/%d/%Y")))
        
        await ctx.send(embed=embed)

    ## Member Join Stats   
    @commands.command(name='showdata', aliases=['sd'])
    async def showData(self, ctx, *date):
        user = ctx.message.author
        joins = 0
        leaves = 0
        rds = 0
        t1 = time.time()
        
        with open('files/config/server_info.json', 'r', encoding='utf-8') as fh:
            server_info = json.load(fh)
            
        if user.top_role.id == config.adminID:
            if date:
                date = ''.join(date)
                date = date.replace("*", ".")
                split_date = date.split('-')
                for entry in server_info:
                    x = re.search(date, entry)
                    if x:
                        joins += server_info[entry]['joins']
                        leaves += server_info[entry]['leaves']
                        rds += server_info[entry]['rds']
            else:
                date = datetime.now().strftime("%m-%d-%Y")
                split_date = date.split('-')
                joins = server_info[date]['joins']
                leaves = server_info[date]['leaves']
                rds = server_info[date]['rds']
            
            # Finalizing date output for embed
            output_month = ''
            output_day = ''
            output_year = ''
            
            if "." not in split_date[0] and int(split_date[0]) < 12:
                output_month = bot.months[int(split_date[0]) - 1]
            if "." not in split_date[1] and int(split_date[1]) < 31:
                output_day = ' ' + split_date[1] + ','
            if "." not in split_date[2] and int(split_date[2]) > 0:
                output_year = int(split_date[2])
            
            embed=discord.Embed(title="Requested report for {}{} {}".format(output_month, output_day, output_year), color=config.reportColor)
            embed.add_field(name="Joins:", value=joins, inline=True)
            embed.add_field(name="Leaves:", value=leaves, inline=True)
            embed.add_field(name="Revolving Doors:", value=rds, inline=True)
            embed.add_field(name="Total Members:", value=len([m for m in ctx.guild.members if not m.bot]), inline=True)
            
            t2 = time.time()
            tDelta = round(t2 - t1, 3)
            
            if config.debug == True:
                embed.set_footer(text="Use !sd mm-dd-yyyy to query specific dates, or replace \nletters with ** to search all dates in that category.  |  Executed in " + str(tDelta) + " seconds.")
            else:
                embed.set_footer(text="Use !sd mm-dd-yyyy to query specific dates, or replace \nletters with ** to search all dates in that category.")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=config.denied)

    ## Updates the bot and relaunches
    @commands.command(name='update')
    async def updateBot(self, ctx, commit):
        if ctx.message.author.top_role.id == config.adminID:
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
            await ctx.send("Launching bot version {}".format(config.version))
            
            await self.bot.close()
            
            os.execv(sys.executable, ['python3'] + sys.argv)

def setup(bot):
    bot.add_cog(Utility(bot))
    print('Added new Cog: ' + str(Utility))