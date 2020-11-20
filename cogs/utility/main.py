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
        guild = ctx.message.guild
        if user.top_role.id == config.adminID:
            await admin.adminMsgs(ctx, bot, guild)

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

    ## Horen Command
    @commands.command(name="horen")
    async def horen(self, ctx, query):
        user = ctx.message.author
        found_list = []
        output = ""
        found = False
               
        with open(config.horenFile, 'r', encoding='utf-8') as fh:
            horen = json.load(fh)
            
        def getpath(nested_dict, value, list_obj, prepath=[]):
            for k, v in nested_dict.items():
                path = prepath + [k,]
                if type(v) == str:
                    check = re.search(r""+value, v.lower())
                    if check != None:
                        list_obj.append(path)
                elif hasattr(v, 'items'): # v is a dict
                    p = getpath(v, value, list_obj, path) # recursive call
                    if p is not None:
                        p + list_obj
            
            return list_obj
            
        def findEntry(path_list):
            try:
                section = horen[path_list[0]]
            except KeyError:
                return None
            
            for i in range(1,len(path_list)):
                try:
                    section = section[path_list[i]]
                except KeyError:
                    break

            return section
        
        def buildTable(table):
            max_len = 0
            output = '```'
            for key, value in table.items():
                for item in value:
                    if len(item) > max_len:
                        max_len = len(item)

            for key, value in table.items():
                for item in value:
                    len_diff = max_len - len(item)
                    half_len_diff = int(round(len_diff / 2, 0))
                    for i in range(0, half_len_diff):
                        item = ' ' + item
                    for i in range(0, (len_diff - half_len_diff)):
                        item = item + ' '
                    output += item
                for i in range(0, (len_diff - half_len_diff)):
                    output += ' '
                output += '\n'
            output += '```'
            return output
        
        def find_last_entry(var):
            for a, b in var.items():
                if type(b) == dict:
                    last_key = find_last_entry(b)
                else:
                    last_key = a
            return last_key
            
        if query == "-i":
            with open(config.horenLicense, 'r', encoding='utf-8') as fh:
                contents = fh.read()
            embed = discord.Embed(title="Horen Tìskortä License Information", description=contents.format(ctx.guild.get_member(config.makoID).mention,find_last_entry(horen)), color=config.reportColor)         
            await ctx.send(embed=embed)
            return
        elif query == "-c":
            with open(config.horenChangelog, 'r', encoding='utf-8') as fh:
                contents = fh.read()
            embed = discord.Embed(title="Horen Tìskortä Change Log", description=contents, color=config.reportColor)
            await ctx.send(embed=embed)
            return
            
        if re.search(r".\..|.\..\..", query) == None:
            paths = getpath(horen, query, found_list)
            for path in paths:
                for i in range(1, len(path)):
                    section = findEntry(path)
                    if section != None:
                        found = True
                        if path[-1] == "info" or path[-1] == "header" or path[-1] == "section" or path[-1] == "footer":
                            rule_number = path[-2]
                        else:
                            rule_number = path[-1]
                        
                        if len(section) < 60:
                            output += "**{}**: {}\n".format(rule_number, section[0:60])
                        else:
                            output += "**{}**: {}\n".format(rule_number, section[0:60].replace("*","").replace("_","") + "`[...]`")
                        embed = discord.Embed(title="Horen Query: {}".format(query), description=output, color=config.reportColor)
                        break
            if not found:
                embed = discord.Embed(title="Horen Query: {}".format(query), description="Matching text was not found.", color=config.failColor)
        else:
            rule_levels = query.split(".")
            for i, level in enumerate(rule_levels):
                if i > 0:
                    level = rule_levels[i-1] + "." + rule_levels[i]
                    rule_levels[i] = level
            section = findEntry(rule_levels)
               
            try:    
                if "header" in section.keys():
                    embed = discord.Embed(title="Horen {}: {}".format(query, section["header"]), description = "{}".format(section["info"]), color=config.reportColor)
                elif "info" in section.keys():
                    embed = discord.Embed(title="Horen {}".format(query), description="{}".format(section["info"]), color=config.reportColor)
                
                if "footer" in section.keys():
                    embed.set_footer(text=section["footer"])
                    
                if "table" in section.keys():
                    output = buildTable(section["table"])
                    embed.add_field(name="⠀", value=output, inline=True)
                    
                if "list" in section.keys():
                    output = ''
                    for value in section["list"].values():
                        output += value[0] + "\n"
                    embed.add_field(name="⠀", value=output, inline=True)
            except AttributeError:
                embed = discord.Embed(title="Horen {}".format(query), description="{}".format(section), color=config.reportColor)
        
        await ctx.send(embed=embed)

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
        words = list(words)
        word_list = []
        results_list = []
        found_count = 0
        showStress = False
        showSource = False
        searchAll = False
        t1 = time.time()
        
        if "-s" in words:
            showStress = True
            words.remove("-s")
        
        if "-src" in words:
            showSource = True
            words.remove("-src")
            
        if "-all" in words:
            searchAll = True
            words.remove("-all")
        
        # Automatically combines 'si' verbs to prevent needing quotes in lookup
        i = 0
        for word in words:
            check_word = re.search(r"si|s..i|s...i", word)
            if check_word != None:
                if len(word_list) == 0:
                    word_list.append(word)
                else:
                    word_list[i-1] += " {}".format(word)
            else:
                word_list.append(word)
                i += 1
        
        # Loads the dictionary
        with open(config.dictionaryFile, 'r', encoding='utf-8') as fh:
            dictionary = json.load(fh)  

        def validate(word, core_word, infix, pos):
            def find_pos(word, entry):
                try:
                    infix_pos = entry["infixDots"]
                    split_list = infix_pos.split('.')
                except ValueError:
                    return False

                split_list.insert(pos, infix)
                joined_word = ''.join(split_list)
                
                if word == joined_word:
                    validated = True
                    return validated
                else:
                    validated = False

            try:
                check = dictionary[core_word]
                if len(check) > 1:
                    for entry in check:
                        validated = find_pos(word, entry, expected_pos)
                else:
                    validated = find_pos(word, check[0], expected_pos)  
                return validated
                
            except KeyError:
                return False
        
        def stripAffixes(word):
            parsed_word = {}
            found = False
            verbs = ["v.", "vtr.", "vin.", "vtrm.", "vim."]
            
            cases = {
                "agentive" : ["l","ìl"],
                "patientive" : ["t","ti","it"],
                "dative" : ["r","ur","ru"],
                "genitive" : ["ä","yä"],
                "topical" : ["ri","ìri"]
                }
                
            plurals = [{"dual" : 'me'},
                       {"trial" : 'pxe'},
                       {"plural" : 'ay'}]
            
            first_pos_infixes = [{"general past" : 'am'},     # Tense
                       {"near past" : 'ìm'},
                       {"general future" : 'ay'},
                       {"subjunctive" : 'iv'},                # Subjunctive compounds
                       {"perfective subjunctive" : 'ilv'},
                       {"progressive subjunctive" : 'irv'},
                       {"future subjunctive a" : 'ìyev'},
                       {"future subjunctive b" : 'iyev'},
                       {"near future" : 'ìy'},
                       {"general future intent" : 'asy'},     # Intent
                       {"near future intent" : 'ìsy'},
                       {"general past perfective" : 'alm'},   # Perfective compounds
                       {"near past perfective" : 'ìlm'},
                       {"general future perfective" : 'aly'},
                       {"near future perfective" : 'ìly'},
                       {"general past progressive" : 'arm'},  # Progressive compounds
                       {"near past progressive" : 'ìrm'},
                       {"general future progressive" : 'ary'},
                       {"near future progressive" : 'ìry'},
                       {"perfective" : 'ol'},                 # Perfective
                       {"progressive" : 'er'},                # Progressive
                       {"progressive participle" : 'us'},     # Participles
                       {"passive participle" : 'awn'},
                       {"past subjunctive" : 'imv'},
                       {"causative" : 'eyk'},                 # Causative
                       {"reflexive" : 'äp'},                  # Reflexive
                       {"causative reflexive" : 'äpeyk'}]     # Causative reflexive
                       
            second_pos_infixes = [           
                       {"positive mood" : 'ei'},              # Mood
                       {"positive mood (H**2.3.3**)" : 'eiy'},
                       {"negative mood" : 'äng'},
                       {"negative mood (H**2.3.5.2**)" : 'eng'},
                       {"inferential" : 'ats'},               # Inferential
                       {"formal, ceremonial" : 'uy'}]         # Ceremonial
                                  
            def checkElement(word_entry, key, abbrev_list):
                found = False
                for entry in word_entry:
                    if entry[key] in abbrev_list:
                        found = True
                
                return found

            # Tries to find a core, unmodified word
            if word in dictionary:
                parsed_word[word] = {"stripped" : word, "notes" : ""}
            else:
                # Noun Checking
                if " " not in word:
                    for key, value in cases.items():
                        for suffix in value:
                            if word.endswith(suffix):
                                core_word = word[0:-len(suffix)]
                                case_name = key
                                if core_word in dictionary:
                                    if checkElement(dictionary[core_word], "partOfSpeech", ["n.","pn."]):
                                        found = True
                                        parsed_word[word] = {"stripped" : core_word, "notes" : ": {}".format(case_name)}
                                        break
                
                # Multiple Infix Checking
                tense_list = []
                str_tenses = []
                def findInfix(word, infix, expected_pos):
                    tense = list(infix.keys())[0]
                    infix = list(infix.values())[0]
                    found = False
                    verb = re.search(r"{}".format(infix), word)
                    if verb != None:
                        found = True
                        return word.replace("{}".format(infix), "", 1), tense, infix, found
                    else:
                        return word, "", "", found
                        
                def validate_pos(word, core_word, infix, tenses, pos):
                    try:
                        validated = False
                        check = dictionary[core_word]
                    except KeyError:
                        return False
                        
                    for entry in check:
                        if checkElement(dictionary[core_word], "partOfSpeech", verbs):
                            if pos == 1:
                                split_list = entry["infixDots"].split(".")
                                split_list.insert(1, ".")
                                joined_word = ''.join(split_list)
                                index = joined_word.find(".")
                                if index == word.find(infix):
                                    validated = True
                            elif pos == 2:
                                split_list = entry["infixDots"].split(".")
                                split_list.insert(2, ".")
                                joined_word = ''.join(split_list)
                                index = joined_word.find(".")
                                if index == word.find(infix):
                                    validated = True
                                    
                    return validated
                    
                if " s.i " in word and not found:
                    parsed_word, found = verbCheck(word, first_pos_infixes, "s{}i", "si")
                
                elif not found:
                    core_word = word
                    for infix in first_pos_infixes:
                        core_word, tense, infix_str, check = findInfix(core_word, infix, 1)
                        if check:
                            tense_list.append(tense)
                            str_tenses.append((infix_str, 1))
                            
                    for infix in second_pos_infixes:
                        if not list(infix.values())[0] == "äng":
                            core_word, tense, infix_str, check = findInfix(core_word, infix, 2)
                            if check:
                                tense_list.append(tense)
                                str_tenses.append((infix_str, 2))
                        else:
                            if "ängkxängo" in word:
                                tense_list.append("negative mood")
                                str_tenses.append(("äng", 2))
                                core_word = core_word.replace("ängkxängo","ängkxo")
                            
                    for tense_tup in str_tenses:
                        if not validate_pos(word, core_word, tense_tup[0], tense_list, 1):
                            if not validate_pos(word, core_word, tense_tup[0], tense_list, 2):
                                break
                    
                        if tense_list != []:
                            parsed_word[word] = {"stripped" : core_word, "notes" : ": {}".format(' : '.join(tense_list))}
                        
                    
                
                # Adjective Checking
                if not found:
                    adj = re.search(r"\Aa|\Ale|a\Z", word)
                    if adj != None:
                        found = True
                        core_word = re.sub(r"\Aa|a\Z", '', word)
                        parsed_word[word] = {"stripped" : core_word, "notes" : ""}
                
            return parsed_word
        
        def getStress(word_entry):
            pre_stress = word_entry['syllables']
            stress_pos = int(word_entry['stressed'])
            pre_stress = pre_stress.split("-")
            pre_stress[stress_pos - 1] = "__{}__".format(pre_stress[stress_pos - 1])
            post_stress = ''.join(pre_stress)
            return post_stress

        def buildResults(i, word_entry, word, original_word, notes, toggle_output):
            results = ''
            if len(word_entry) > 1:
                results += "`{}.` **{}** has multiple definitions: \n".format(i+1, word)
                for i, entry in enumerate(word_entry):
                    if showStress:
                        post_stress = getStress(entry)
                        results += "`     {}.` **{}** *{}* {}\n".format(alphabet[i], post_stress, entry['partOfSpeech'], entry['translation'])
                    elif showSource:
                        results += "`     {}.` **{}** *{}* {}\n{}\n".format(alphabet[i], word, entry['partOfSpeech'], entry['translation'], entry['source'])
                    else:
                        results += "`     {}.` **{}** *{}* {}\n".format(alphabet[i], word, entry['partOfSpeech'], entry['translation'])
            else:
                if showStress:
                    post_stress = getStress(word_entry[0])
                    if toggle_output:
                        results += "`{}.` **{}** *{}* {} {}\nOriginal: **{}**\n".format(i+1, post_stress, word_entry[0]['partOfSpeech'], word_entry[0]['translation'], notes, original_word)
                    else:
                        results += "`{}.` **{}** *{}* {}\n".format(i+1, post_stress, word_entry[0]['partOfSpeech'], word_entry[0]['translation'])
                elif showSource:
                    results += "`{}.` **{}** *{}* {}\nSource: {}\n".format(i+1, word, word_entry[0]['partOfSpeech'], word_entry[0]['translation'], word_entry[0]['source'])
                else:
                    if toggle_output:
                        results += "`{}.` **{}** *{}* {} {}\nOriginal: **{}**\n".format(i+1, word, word_entry[0]['partOfSpeech'], word_entry[0]['translation'], notes, original_word)
                    else:
                        results += "`{}.` **{}** *{}* {}\n".format(i+1, word, word_entry[0]['partOfSpeech'], word_entry[0]['translation'])
            
            return results
        
        results = ''
        alphabet = ['a', 'b', 'c', 'd', 'e']
        for i, word in enumerate(word_list):
            first_time = True
            nv_found = False
            found = False
            
            if not searchAll:
                # Na'vi word lookup
                try:
                    if not searchAll:
                        word_entry = dictionary[word.lower()]
                        nv_found = True
                        results += "**Na'vi Words:**\n"
                        results += buildResults(i, word_entry, word, word, "", False)
                        found_count += len(word_entry)
                
                # No exact match found
                except KeyError:
                    nv_found = False
            else:
                # Partial match for all Na'vi words
                for key in dictionary.keys():
                    if word in key:
                        nv_found = True
                        results += buildResults(i, dictionary[key], key, word, "", False)
                        found_count += len(dictionary[key])
                        if 1900 < len(results) < 2048:
                            results_list.append(results)
                            results = ''
                
            # Modified Na'vi word lookup
            if not nv_found:
                parsed_word = stripAffixes(word)
                try:
                    word_entry = dictionary[parsed_word[word]['stripped'].lower()]
                    nv_found = True
                    results += buildResults(i, word_entry, word, parsed_word[word]['stripped'].lower(), parsed_word[word]['notes'], True)
                    found_count += len(word_entry)
                
                # No parsed word match found
                except KeyError:
                    nv_found = False
            
            # Reverse lookup
            if not searchAll:
                for key, value in dictionary.items():
                    for k, sub in enumerate(value):
                        found = False
                        x = re.search(r"\b"+word+"$", sub['translation'])
                        y = re.search(r"\b"+word+"[,]", sub['translation'])
                        if x != None or y != None:
                            if first_time:
                                results += "\n**Reverse Lookup Results:**\n"
                                first_time = False
                            found = True
                            found_count += 1
                            results += "`{}.` **{}** *{}* {}\n".format(i+1, key, sub['partOfSpeech'], sub['translation'])
            
            # No results found at all
            if not found and not nv_found:
                results += "`{}.` **{}** not found.\n".format(i+1, word_list[i])
                
            results += "\n"
            
            if 1900 < len(results) < 2048:
                results_list.append(results)
                results = ''
        
        results_list.append(results)
        
        if len(results_list) > 1:
            await ctx.send("More than 20 matching results found. DMing you the results.")
            for n, result in enumerate(results_list):
                embed = discord.Embed(title="Search Results ({}/{}):".format(n+1,len(results_list)), description=result, color=config.reportColor)
                embed.set_footer(text="Found {} results in {} seconds.".format(found_count, round(time.time() - t1, 3)))
                await user.send(embed=embed)
        else:
            for n, result in enumerate(results_list):
                embed = discord.Embed(title="Search Results ({}/{}):".format(n+1,len(results_list)), description=result, color=config.reportColor)
                embed.set_footer(text="Found {} results in {} seconds.".format(found_count, round(time.time() - t1, 3)))
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
            
            with open('files/config/config.json', 'w') as fh:
                config.config['version'] = commit
                json.dump(config.config, fh)
            reload(config)
            await ctx.send("Launching bot version {}".format(config.version))
            
            await self.bot.close()
            
            os.execv(sys.executable, ['python3'] + sys.argv)

def setup(bot):
    bot.add_cog(Utility(bot))
    print('Added new Cog: ' + str(Utility))