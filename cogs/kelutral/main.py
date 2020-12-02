import discord
from discord.ext import commands
from discord.utils import get

import json
import time
import re
import asyncio
import random

import bot
import config
import namegen
import admin

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    ## -- Checks for empty args
    def is_empty(self, any_structure):
        if any_structure:
            return False
        else:
            return True

    ## -- Updates the Visible Stat for 'names generated'
    def update(self, newNameCount):
        with open(config.botFile, 'r') as fh:
            nameCount = json.load(fh)
        
        nameCount[0] = nameCount[0] + newNameCount
        
        with open(config.botFile, 'w') as fh:
            json.dump(nameCount, fh)
            
        return nameCount[0]

    ## FAQ Command
    @commands.command(name="faq",aliases=['sìpawm'])
    async def faq(self, ctx, *topic):
        if ctx.guild.id == config.KTID:
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

    ## Horen Command
    @commands.command(name="horen")
    async def horen(self, ctx, query):
        if ctx.guild.id == config.KTID:
            user = ctx.message.author
            found_list = []
            n = 0
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
                        section = "This section does not exist."
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
                
            def find_next_entry(horen_dict, current):
                split_list = current.split(".")
                next_entry = None
                
                def run_search(split_list):
                    rule_levels = list(".".join(split_list).split("."))
                    for i, level in enumerate(rule_levels):
                        if i > 0:
                            level = rule_levels[i-1] + "." + rule_levels[i]
                            rule_levels[i] = level
                    next_entry = findEntry(rule_levels)
                    if next_entry == "This section does not exist.":
                        next_entry = None
                        split_list.pop(len(split_list)-1)
                        rule_levels.pop(len(rule_levels)-1)
                        
                    return next_entry
                
                if len(split_list) < 4:
                    split_list.append('1')
                    next_entry = run_search(split_list)
                        
                while next_entry == None:
                    split_list[len(split_list)-1] = str(int(split_list[len(split_list)-1]) + 1)
                    next_entry = run_search(split_list)

                    if len(split_list) == 0:
                        return None
                
                return split_list
                
            def find_previous_entry(horen_dict, current):
                split_list = current.split(".")
                rule_levels = current.split(".")
                next_entry = None
                
                def run_search(split_list):
                    def sub_check(split_list):
                        if len(split_list) < 4:
                            for i in range(20,1,-1):
                                split_list.append(str(i))
                                next_entry, split_list = run_search(split_list)
                                if next_entry != None:
                                    break
                                split_list.pop(len(split_list)-1)
                        
                            return next_entry, split_list
                        else:
                            return None, split_list
                
                    rule_levels = list(".".join(split_list).split("."))
                    for i, level in enumerate(rule_levels):
                        if i > 0:
                            level = rule_levels[i-1] + "." + rule_levels[i]
                            rule_levels[i] = level
                    next_entry = findEntry(rule_levels)
                    if next_entry == "This section does not exist.":
                        next_entry = None
                        if int(split_list[len(split_list)-1]) == 0:
                            split_list.pop(len(split_list)-1)
                            rule_levels.pop(len(rule_levels)-1)
                        else:
                            split_list[len(split_list)-1] = str(int(split_list[len(split_list)-1]) - 1)
                    
                    if next_entry == None:
                        for i in range(0,4-len(split_list)):
                            next_entry, split_list = sub_check(split_list)

                    return next_entry, split_list
                
                if len(split_list) == 1:
                    split_list = [str(int(split_list[0])-1),'20','20','20']
                else:
                    split_list[len(split_list)-1] = str(int(split_list[len(split_list)-1]) - 1)
                    
                while next_entry == None:
                    next_entry, split_list = run_search(split_list)
                    print(split_list, next_entry)
                    if len(split_list) == 0:
                        return None

                return split_list
            
            async def search_horen(horen, query, loop_state, original_msg, n, found_list):
                output = ""
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
                    
                elif re.search(r".\..|.\..\..", query) == None and len(query) > 1:
                    path_list = []
                    paths = getpath(horen, query, path_list)
                    for path in paths:
                        for i in range(1, len(path)):
                            section = findEntry(path)
                            if section != None:
                                found = True
                                if path[-1] == "info" or path[-1] == "header" or path[-1] == "section" or path[-1] == "footer":
                                    rule_number = path[-2]
                                    found_list.append(rule_number)
                                else:
                                    rule_number = path[-1]
                                    found_list.append(rule_number)
                                break

                    if not found:
                        embed = discord.Embed(title="Horen Query: {}".format(query), description="Matching text was not found.", color=config.failColor)
                
                if found_list == []:
                    rule_levels = query.split(".")
                    if len(rule_levels) > 1:
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
                    
                    emojis = ['⏮','⏹️','⏭']
                    if not loop_state:
                        message = await ctx.send(embed=embed)
                    else:
                        message = original_msg
                        await message.edit(embed=embed)
                    
                    for emoji in emojis:
                            await message.add_reaction(emoji)
                    
                    def check(reaction, user):
                        emojis = ['⏮','⏹️','⏭']
                        return str(reaction.emoji) in emojis and user.id == ctx.message.author.id
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=20, check=check)
                    except asyncio.TimeoutError:
                        await message.clear_reactions()
                    else:
                        if str(reaction.emoji) == '⏮':
                            await message.remove_reaction(reaction.emoji, ctx.message.author)
                            query = '.'.join(find_previous_entry(horen, query))
                            await search_horen(horen, query, True, message, 0, found_list)
                        elif str(reaction.emoji) == '⏭':
                            await message.remove_reaction(reaction, ctx.message.author)
                            query = '.'.join(find_next_entry(horen, query))
                            await search_horen(horen, query, True, message, 0, found_list)
                        elif str(reaction.emoji) == '⏹️':
                            await message.clear_reactions()
                else:
                    found_list = dict.fromkeys(found_list)
                    found_list = list(found_list)
                    rule_levels = found_list[n].split(".")
                    if len(rule_levels) > 1:
                        for i, level in enumerate(rule_levels):
                            if i > 0:
                                level = rule_levels[i-1] + "." + rule_levels[i]
                                rule_levels[i] = level
                    section = findEntry(rule_levels)
                    
                    try:
                        if type(section) == str and section != "This section does not exist.":
                            embed = discord.Embed(title="Horen {}".format(found_list[n]), description="{}".format(section), color=config.reportColor)
                            embed.set_footer(text="Result {}/{}".format(n+1,len(found_list)))
                        else:
                            if "header" in section.keys():
                                embed = discord.Embed(title="Horen {}: {}".format(found_list[n], section["header"]), description = "{}".format(section["info"]), color=config.reportColor)
                            elif "info" in section.keys():
                                embed = discord.Embed(title="Horen {}".format(found_list[n]), description="{}".format(section["info"]), color=config.reportColor)
                            
                            if "footer" in section.keys():
                                embed.set_footer(text="{}\n\nResult {}/{}".format(section["footer"], n+1, len(found_list)))
                            else:
                                embed.set_footer(text="Result {}/{}".format(n+1,len(found_list)))
                                
                            if "table" in section.keys():
                                output = buildTable(section["table"])
                                embed.add_field(name="⠀", value=output, inline=True)
                                
                            if "list" in section.keys():
                                output = ''
                                for value in section["list"].values():
                                    output += value[0] + "\n"
                                embed.add_field(name="⠀", value=output, inline=True)
                            
                    except AttributeError as err:
                        print("Triggered error somehow: " + str(err))
                        embed = discord.Embed(title="Horen {}".format(query), description="{}".format(section), color=config.reportColor)
                    
                    emojis = ['⏮','⏹️','⏭']
                    if not loop_state:
                        message = await ctx.send(embed=embed)
                    else:
                        message = original_msg
                        await message.edit(embed=embed)
                    
                    for emoji in emojis:
                            await message.add_reaction(emoji)
                    
                    def check(reaction, user):
                        emojis = ['⏮','⏹️','⏭']
                        return str(reaction.emoji) in emojis and user.id == ctx.message.author.id
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=20, check=check)
                    except asyncio.TimeoutError:
                        await message.clear_reactions()
                    else:
                        if str(reaction.emoji) == '⏮':
                            await message.remove_reaction(reaction.emoji, ctx.message.author)
                            if n - 1 < 0:
                                n = len(found_list) + 1
                            await search_horen(horen, "", True, message, n - 1, found_list)
                        elif str(reaction.emoji) == '⏭':
                            await message.remove_reaction(reaction, ctx.message.author)
                            if n + 1 > len(found_list) - 1:
                                n = -1
                            await search_horen(horen, "", True, message, n + 1, found_list)
                        elif str(reaction.emoji) == '⏹️':
                            await message.clear_reactions()
        
        await search_horen(horen, query, False, None, 0, found_list)

    ## LEP Command
    @commands.command(name="lep")
    async def lepCommand(self, ctx, *args):
        if ctx.guild.id == config.KTID:
            user = ctx.message.author.id
            msg_channel = self.bot.get_channel(config.lepChannel)
            modLog_channel = self.bot.get_channel(config.modLog)
            
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

    ## Search command
    @commands.command(name="search")
    async def search(self, ctx, *words):
        if isinstance(ctx.channel, discord.channel.DMChannel) or ctx.guild.id == config.KTID:
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

    # Games Commands

    ## Generate # of random names
    @commands.command(name="generate",aliases=['ngop'])
    async def generate(self, ctx, numOut, numSyllables, *letterPrefs):
        if ctx.guild.id == config.KTID:
            user = ctx.message.author
            n = int(numOut)
            s = int(numSyllables)
            language = admin.readDirectory(user, "language")
            t1 = time.time()
            
            # Checks that both generation parameters are < 0
            if not n <= 0 and not s <= 0:
                if not s <= 5:
                    # Syllable error
                    await ctx.send(embed=discord.Embed(description=config.text_file[language]["errors"]["generate_error"] + config.text_file[language]["errors"]["generate_errors"]["syllables"], colour=config.failColor) )
                elif not n <= 20:
                    # Name count error
                    await ctx.send(embed=discord.Embed(description=config.text_file[language]["errors"]["generate_error"] + config.text_file[language]["errors"]["generate_errors"]["names"], colour=config.failColor))
                else:
                    # Updates bot presence
                    nameCount = self.update(n)
                    await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("ngamop " + "{:,}".format(nameCount) + " tstxoti."))
                    
                    # Builds embed
                    dict_embed = {'author': {'name': '{}: '.format(config.text_file[language]["generate"]["success"].format(ctx.message.author.name))},'fields': [], 'color': config.successColor,'type': 'rich'}
                    for i in range(0, n):
                        dict_embed['fields'].append({'inline': True, 'name': '{} {}'.format(config.text_file[language]["generate"]["name"], i + 1), 'value': namegen.nameGen(numSyllables,letterPrefs)})
                    if config.debug:
                        dict_embed['footer'] = {'text': "Executed in {} seconds.".format(round(time.time() - t1, 3))}
                    
                    await ctx.send(embed=discord.Embed.from_dict(dict_embed))
            else:
                # Invalid syntax
                await ctx.send(embed=discord.Embed(description=config.text_file[language]["errors"]["generate_error"] + config.text_file[language]["errors"]["generate_errors"]["zero"], color=config.failColor))
            
            now = datetime.strftime(datetime.now(),'%H:%M')
            print(now + " -- {} generated {} names.".format(user.name, n))

    ## Quiz Command
    @commands.command(name="quiz",aliases=['fmetok'])
    async def quiz(self, ctx, *args):
        if ctx.guild.id == config.KTID:
            member = ctx.message.author
            needStudy = []
            toDelete = []
            correct = 0
            incorrect = 0
            
            emojis = ['\U0001F1E6','\U0001F1E7','\U0001F1E8','\U0001F1E9']
            alphabet = ['A', 'B', 'C', 'D']
            
            def check(reaction, user):
                for emoji in emojis:
                    if str(reaction.emoji) == emoji:
                        foundEmoji = True
                        break
                    else:
                        foundEmoji = False
                return user == ctx.message.author and foundEmoji
            
            # Initializes dictionary
            with open(config.dictionaryFile, 'r', encoding='utf-8') as fh:
                dictionary = json.load(fh)
            
            # Validates arguments
            if len(args) > 2:
                await ctx.send(embed=config.arguments)
            else:
                # Validates Language argument
                if "English" in args or "english" in args:
                    lang = "English"
                elif "Na'vi" in args or "na'vi" in args:
                    lang = "Na'vi"
                else:
                    lang = "English"
                
                # Validates round count argument
                if not self.is_empty(args): # If not an empty tuple
                    for test in args:
                        try:
                            if test.isnumeric():
                                rounds = int(test)
                                if 10 > rounds < 1:
                                    await ctx.send(embed=config.syntax)
                                    return
                                break
                        except ValueError:
                            rounds = 1
                            continue
                else:
                    rounds = 1

                # If all argument checks succeed, starts the quiz
                for it in range(0, abs(int(rounds))):
                    allDefinitions = []
                    correctEntry = random.choice(list(dictionary))
                    english_def = dictionary[correctEntry][0]["translation"]
                    nv_def = correctEntry
                    
                    # If the quiz is English > Na'vi
                    if lang == "English":
                        correctDef = english_def
                        selected_word = nv_def
                        
                        # Selects a random Na'vi word
                        for i in range(1,4):
                            index = random.randint(1,len(list(dictionary)))
                            
                            # Duplicate prevention
                            if list(dictionary.keys())[index] == correctEntry:
                                while list(dictionary.keys())[index] == correctEntry:
                                    index = random.randint(1,len(list(dictionary)))
                            else:
                                random_entry = list(dictionary)[index]
                                randomDef = dictionary[random_entry][0]['translation']
                                allDefinitions.append(randomDef)
                    
                    # If the quiz is Na'vi > English
                    elif lang == "Na'vi":
                        correctDef = nv_def
                        selected_word = english_def
                        
                        # Selects a random English word
                        for i in range(1,4):
                            index = random.randint(1,len(list(dictionary)))
                            
                            # Duplicate prevention
                            if list(dictionary.keys())[index] == correctEntry:
                                while list(dictionary.keys())[index] == correctEntry:
                                    index = random.randint(1,len(list(dictionary)))
                            else:
                                random_entry = dictionary[list(dictionary)[index]][0]["translation"]
                                randomDef = list(dictionary)[index]
                                allDefinitions.append(randomDef)
                    
                    allDefinitions.append(correctDef)
                    random.shuffle(allDefinitions)                
                    
                    # Builds the embed for output
                    embed=discord.Embed(title="Vocabulary Quiz: {}".format(selected_word), description="React with the appropriate letter to submit your guess for the definition in the opposite language.", color=config.quizColor)
                    message = await ctx.send(embed=embed)
                    toDelete.append(message)
                    
                    # Adds reactions
                    for emoji in emojis:
                        await message.add_reaction(emoji)
                    
                    # Adds definitions
                    for i, letter in enumerate(alphabet):
                        embed.add_field(name="Definition {}".format(letter), value=allDefinitions[i],inline=False)
                    
                    # Updates the embed with the choices
                    await message.edit(embed=embed)
                    
                    # Waits for reaction
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
                    except asyncio.TimeoutError:
                        embed=discord.Embed(title="Word: {}".format(nv_def), description="Sorry, you took too long to answer! The correct answer was {}, **{}**. Try again!".format(nv_def, english_def), color=config.failColor)
                        needStudy.append("**{}**, *{}*\n".format(nv_def, english_def))
                        
                        await message.clear_reactions()
                        await message.edit(embed=embed)
                    else:
                        # If the reaction added is one of the 4 required
                        if str(reaction) in emojis:
                            # Indexes the response
                            response = emojis.index(str(reaction))

                            # Makes sure the quiz isn't being run in DMs
                            if ctx.message.guild:
                                await message.clear_reactions()
                            
                            # If the selected response is the correct one
                            if allDefinitions[response] == correctDef:
                                embed=discord.Embed(title="Word: {}".format(selected_word), description="Congratulations ma {}, you were correct!".format(member.mention), color=config.successColor)
                                embed.add_field(name="Definition {}".format(alphabet[response]), value=correctDef,inline=False)
                                
                                correct += 1
                            else:
                                embed=discord.Embed(title="Word: {}".format(selected_word), description="Sorry ma {}, the correct answer was **{}**. Your answer was: {}".format(member.mention, correctDef, allDefinitions[response]), color=config.failColor)
                                embed.add_field(name="Definition {}".format(alphabet[response]), value=allDefinitions[response],inline=False)
                                
                                incorrect += 1
                                needStudy.append("**{}**, *{}*\n".format(nv_def, english_def))
                            await message.edit(embed=embed)
                
                # Builds the results embed
                if correct == 0:
                    embed = discord.Embed(title="Results", description="You got {} out of {} correct. Try again!\n\nHere are the words you need to work on:".format(correct, rounds))
                    for i in needStudy:
                        embed.add_field(name="Word:", value=i)
                elif correct == rounds:
                    embed = discord.Embed(title="Results", description="Nice work! You got {} out of {} correct!".format(correct, rounds))
                else:
                    embed = discord.Embed(title="Results", description="You got {} out of {} correct, not bad!\n\nHere are the words you need to work on:".format(correct, rounds))
                    for i in needStudy:
                        embed.add_field(name="Word:", value=i)
                await ctx.send(embed=embed)
                
                # Waits 30 seconds before deleting the quiz messages, leaving the responses
                await asyncio.sleep(30)
                for message in toDelete:
                    await message.delete()

    # The Neytiri Project Commands
    
    ## Accepts a submitted request for a teacher
    @commands.command(name='accept')
    async def accept(self, ctx, user_id):
        if ctx.guild.id == config.KTID:
            teacher = ctx.message.author
            student = ctx.guild.get_member(int(user_id))
            
            # Retrieves the necessary profiles
            student_profile = admin.readDirectory(student)
            teacher_profile = admin.readDirectory(teacher)
            
            # Checks for a registration message from the student
            if type(student_profile['tnp']['registration']) == int:
                reg_id = student_profile['tnp']['registration']
                student_profile['tnp']['accepted_by'] = teacher.id
                
                # Retrieves the registration channel
                channel = self.bot.get_channel(config.newRegChannel) #new-registrations
                
                # Retrieves the registration message
                message = await channel.fetch_message(reg_id)
                
                # Edits the registration message to confirm acceptance
                embed = discord.Embed(title="{}: {}".format(student.name, student.id), description="{} was accepted by {}!".format(student.name, teacher.name), color=config.successColor)
                await message.edit(embed=embed)
                
                # Retrieves the teacher's channel
                teacher_channel = self.bot.get_channel(teacher_profile['tnp']['channel'])
                
                # Updates the student's permissions in the teacher's channel and sends them a confirmation message
                await teacher_channel.set_permissions(student, send_messages = True, read_messages = True)
                await teacher_channel.send("{} has accepted you ma {}!".format(teacher.mention, student.mention))

    ## Registers for The Neytiri Project
    @commands.command(name='tnp')
    async def accessTNP(self, ctx):
        if ctx.guild.id == config.KTID:
            user = ctx.message.author
            channel = self.bot.get_channel(config.regChannel) # Registration Channel
            guild = ctx.message.guild
            
            profile = admin.readDirectory(user)
            
            if get(guild.roles, id=config.teacherID) in user.roles:
                embed_role = get(guild.roles, id=config.teacherID)
                embed_channel = guild.get_channel(769027341857849435)
            else:
                embed_role = get(guild.roles, id=715044972436389890)
                embed_channel = channel
            
            # Tries to retrieve the Neytiri Project subdict from the profile
            try:
                theNeytiriProject = profile['tnp']
            except KeyError:
                profile['tnp'] = {
                    'channel' : '',
                    'registration' : ''
                    }
                theNeytiriProject = profile['tnp']
            
            # If the user has the teacher role, registers them as a teacher
            if get(ctx.guild.roles, id=config.teacherID) in user.roles:
                # Adds the TNP roles
                tnpRole = get(ctx.guild.roles, id=config.tnpID)
                await user.add_roles(tnpRole, get(guild.roles, id=config.tnpKaryuID))
                
                # Creates the teacher channel and sets perms for the user
                new_channel = await guild.create_text_channel("{}'s-channel".format(user.name), category = get(guild.categories, id=768591895227007016))
                
                perms = new_channel.overwrites_for(tnpRole)
                perms.view_channel = False
                await new_channel.set_permissions(tnpRole, overwrite=perms)
                await new_channel.set_permissions(user, send_messages = True, read_messages = True)
                
                # Adds the new channel id to the teacher's profile.
                theNeytiriProject['channel'] = new_channel.id
                
                admin.updateDirectory()
            
            # If the user does not have the teacher role, registers them as a learner
            else:
                # Adds TNP role and sets permissions for the #registration channel
                await user.add_roles(get(guild.roles, id =config.tnpID))
                await channel.set_permissions(user, send_messages = True, read_messages = True)
            
            # Tries to DM the user
            try:
                embed = discord.Embed(title="Welcome to The Neytiri Project", description="Please read this information before continuing.\n\nThe Neytiri Project is a 1 on 1 teaching program where teachers can pair with dedicated students based on shared qualities like time-zone or learning style.\n\nYou have been accepted as a **{}** based on your existing roles in Kelutral.org.\n\nProspective teacher's availability to teach is determined by them, and they are under no obligation to teach if they are busy or have other responsibilites to attend to. To get started with registration, use !register in {}.".format(embed_role.name, embed_channel.mention), color=config.reportColor)
                embed.set_footer(text="To leave the Neytiri Project, use !unregister at any time.")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/539428806558220308/539429072422436895/TNP2.png")
                await user.send(embed=embed)
            except:
                embed = discord.Embed(description="Unable to DM. Please allow DMs from the bot to continue.", color=config.failColor)
                await ctx.send(embed=embed)
                return
            
            # Sends the confirmation
            embed = discord.Embed(title="The Neytiri Project", description="Accepted your registration! Check your DMs for the next steps.")
            
            await ctx.send(embed=embed)

    ## Requests a teacher for The Neytiri Project
    @commands.command(name='register')
    async def register(self, ctx):
        if ctx.guild.id == config.KTID:
            channel = ctx.message.channel
            author = ctx.message.author
            profile = admin.readDirectory(author)
            
            # Conditional check for the registration process
            def check(c):
                return c.channel == channel and c.author == author
                
            if type(profile['tnp']['registration']) == int:
                embed = discord.Embed(description="You already have a teacher request on file. To change your request, use `!unregister` and start over.")
                await ctx.send(embed=embed)
                return
                
            if get(ctx.guild.roles, id=config.teacherID) in author.roles:
                teacher_channel = ctx.guild.get_channel(profile['tnp']['channel'])
                
                embed = discord.Embed(title="Create a Teacher Profile", description="Thanks for signing up to teach in **The Neytiri Project**! I just need a little bit of information from you to get your teacher bio set up. To get started, tell me a little bit about yourself.")
                message = await ctx.send(embed=embed)
                
                master_loop = True
                while master_loop:
                    
                    step_one = True
                    while step_one:
                        about_me = await self.bot.wait_for('message', check=check)
                        await about_me.delete()
                        
                        embed = discord.Embed(title=author.name, description="Here's what I received:\n\n'{}'\n\nDoes that look correct? Let me know with 'yes' or 'no'".format(about_me.content), color=config.reportColor)
                        embed.set_footer(text="Step 1/4")
                        await message.edit(embed=embed)
                        
                        response = await self.bot.wait_for('message', check=check)
                        if response.content.lower() == 'yes':
                            step_one = False
                            embed = discord.Embed(title=author.name, description="Great! What is your time-zone?", color=config.reportColor)
                            embed.set_footer(text="Step 2/4")
                            await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=author.name, description="Okay, let's try again. Tell me a little bit about yourself.", color=config.welcomeColor)
                            embed.set_footer(text="Step 1/4")
                            await message.edit(embed=embed)
                        
                        await response.delete()
                    
                    step_two = True
                    while step_two:
                        time_zone = await self.bot.wait_for('message', check=check)
                        await time_zone.delete()
                        embed = discord.Embed(title=author.name, description="Great! So your time-zone is '{}', correct? Let me know with 'yes' or 'no'".format(time_zone.content), color=config.reportColor)
                        embed.set_footer(text="Step 2/4")
                        await message.edit(embed=embed)
                        
                        response = await self.bot.wait_for('message', check=check)
                        if response.content.lower() == 'yes':
                            step_two = False
                            embed = discord.Embed(title=author.name, description="Great! Moving on. How would you describe your teaching style?", color=config.reportColor)
                            embed.set_footer(text="Step 3/4")
                            await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=author.name, description="Okay, let's try again. What is your time-zone?", color=config.welcomeColor)
                            embed.set_footer(text="Step 2/4")
                            await message.edit(embed=embed)
                        
                        await response.delete()
                    
                    step_three = True
                    while step_three:
                        teaching = await self.bot.wait_for('message', check=check)
                        await teaching.delete()
                        embed = discord.Embed(title=author.name, description="Great! Making sure I got that, you said '{}', correct? Let me know with 'yes' or 'no'.".format(teaching.content), color=config.reportColor)
                        embed.set_footer(text="Step 3/4")
                        await message.edit(embed=embed)
                    
                        response = await self.bot.wait_for('message', check=check)
                        if response.content.lower() == 'yes':
                            step_three = False
                            embed = discord.Embed(title=author.name, description="Great! Moving on. What is your favorite Na'vi word and why?", color=config.reportColor)
                            embed.set_footer(text="Step 4/4")
                            await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=author.name, description="Okay, let's try again. How would you describe your teaching style?", color=config.welcomeColor)
                            embed.set_footer(text="Step 3/4")
                            await message.edit(embed=embed)
                        
                        await response.delete()
                        
                    step_four = True
                    while step_four:
                        fav_word = await self.bot.wait_for('message', check=check)
                        await fav_word.delete()
                        embed = discord.Embed(title=author.name, description="Great! Making sure I got that, you said '{}', correct? Let me know with 'yes' or 'no'.".format(fav_word.content), color=config.reportColor)
                        embed.add_field(name="Favorite Na'vi Word:", value=fav_word.content)
                        embed.set_footer(text="Step 3/4")
                        await message.edit(embed=embed)
                    
                        response = await self.bot.wait_for('message', check=check)
                        if response.content.lower() == 'yes':
                            step_four = False
                            embed = discord.Embed(title=author.name, description="Great! Moving on. What is your favorite Na'vi word and why?", color=config.reportColor)
                            embed.set_footer(text="Step 4/4")
                            await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=author.name, description="Okay, let's try again. What is your favorite Na'vi word and why?", color=config.welcomeColor)
                            embed.set_footer(text="Step 3/4")
                            await message.edit(embed=embed)
                        
                        await response.delete()
                        
                    # Prompts the user to confirm all their submitted information is correct
                    step_five = True
                    while step_five:
                        embed = discord.Embed(title=author.name, description="Does everything look correct? Let me know with 'yes' or 'no'.", color=config.reportColor)
                        embed.add_field(name="About Me:", value=about_me.content, inline=False)
                        embed.add_field(name="Time Zone:", value=time_zone.content, inline=True)
                        embed.add_field(name="Teaching Style:", value=teaching.content, inline=True)
                        embed.add_field(name="Favorite Na'vi Word:", value=fav_word.content, inline=True)
                        embed.set_footer(text="Step 4/4")
                        await message.edit(embed=embed)
                    
                        response = await self.bot.wait_for('message', check=check)
                        if response.content.lower() == 'yes':
                            # Ends both loops
                            step_five = False
                            master_loop = False
                            
                            await response.delete()
                            
                            # Builds the registration embed for #new-registrations
                            embed = discord.Embed(title="{}: {}".format(author.name, author.id))
                            embed.add_field(name="About Me:", value=about_me.content, inline=False)
                            embed.add_field(name="Time Zone:", value=time_zone.content, inline=True)
                            embed.add_field(name="Teaching Style:", value=teaching.content, inline=True)
                            embed.add_field(name="Favorite Na'vi Word:", value=fav_word.content, inline=True)
                            embed.set_thumbnail(url=author.avatar_url)
                            
                            try:
                                registration_message = await teacher_channel.fetch_message(profile['tnp']['registration'])
                                await registration_message.edit(embed=embed)
                            except:
                                registration_message = await teacher_channel.send(embed=embed)
                                profile['tnp']['registration'] = registration_message.id
                                await registration_message.pin()
                            
                            admin.updateDirectory()
                            
                            embed = discord.Embed(title=author.name, description="Alright! You're all set. Your profile has been automatically posted and pinned in your teaching channel for prospective learners to read. If at any point you wish to update your profile, simply run this command again.", color=config.reportColor)
                            await message.edit(embed=embed)
                            await asyncio.sleep(120)
                            await message.delete()
                        else:
                            embed = discord.Embed(title=author.name, description="Okay, let's go back to the top. Tell me a little bit about yourself.", color=config.welcomeColor)
                            embed.set_footer(text="Step 1/3")
                            await message.edit(embed=embed)
                            await response.delete()
                            
            else:
                embed = discord.Embed(title="Registration Form: {}".format(author.name), description="Thanks for registering for The Neytiri Project ma {}. Please answer a few short questions to help give teachers a better idea of whether or not you would be a good fit for them.\n\nTo start, what is your time-zone?".format(author.mention), color=config.reportColor)
                message = await ctx.send(embed=embed)
                
                master_loop = True
                while master_loop:
                    # Prompts the user for their time zone
                    step_one = True
                    while step_one:
                        time_zone = await self.bot.wait_for('message', check=check)
                        await time_zone.delete()
                        embed = discord.Embed(title=author.name, description="Great! So your time zone is '{}', correct? Let me know with 'yes' or 'no'".format(time_zone.content), color=config.reportColor)
                        embed.set_footer(text="Step 1/3")
                        dict_embed = embed.to_dict()
                        await message.edit(embed=embed)
                        
                        response = await self.bot.wait_for('message', check=check)
                        if response.content.lower() == 'yes':
                            step_one = False
                            dict_embed['description'] = "Great! Moving on. When are you available during the week? As much detail as possible will help the teachers."
                            dict_embed['footer'] = {'text' : "Step 2/3"}
                            dict_embed['fields'] = [{'name' : "Time Zone",'value' : time_zone.content}]
                            await message.edit(embed=discord.Embed.from_dict(dict_embed))
                        else:
                            dict_embed['description'] = "Okay, let's try again. What is your time-zone?"
                            dict_embed['color'] = config.welcomeColor
                            await message.edit(embed=discord.Embed.from_dict(dict_embed))
                        
                        await response.delete()
                    
                    # Prompts the user for their availability
                    step_two = True
                    while step_two:
                        availability = await self.bot.wait_for('message', check=check)
                        await availability.delete()
                        dict_embed['description'] = "Great! So your availability is '{}', correct? Let me know with 'yes' or 'no'".format(availability.content)
                        dict_embed['color'] = config.reportColor
                        await message.edit(embed=discord.Embed.from_dict(dict_embed))
                    
                        response = await self.bot.wait_for('message', check=check)
                        if response.content.lower() == 'yes':
                            step_two = False
                            dict_embed['description'] = "Great! Moving on. How would you describe your learning style?"
                            dict_embed['fields'].append({'name' : "Availability", 'value' : availability.content})
                            dict_embed['footer'] = {'text' : "Step 3/3"}
                            await message.edit(embed=discord.Embed.from_dict(dict_embed))
                        else:
                            dict_embed['description'] = "Okay, let's try again. What is your availability during the week?"
                            dict_embed['color'] = config.welcomeColor
                            await message.edit(embed=discord.Embed.from_dict(dict_embed))
                        
                        await response.delete()
                    
                    # Prompts the user for their learning style
                    step_three = True
                    while step_three:
                        learning = await self.bot.wait_for('message', check=check)
                        await learning.delete()
                        dict_embed['description'] = "Great! Making sure I got that, you said '{}', correct? Let me know with 'yes' or 'no'.".format(learning.content)
                        dict_embed['color'] = config.reportColor
                        await message.edit(embed=discord.Embed.from_dict(dict_embed))
                    
                        response = await self.bot.wait_for('message', check=check)
                        if response.content.lower() == 'yes':
                            step_three = False
                            dict_embed['fields'].append({'name' : "Learning Style", 'value' : learning.content})
                            await message.edit(embed=discord.Embed.from_dict(dict_embed))
                        else:
                            dict_embed['description'] = "Okay, let's try again. How would you describe your learning style?"
                            dict_embed['color'] = config.welcomeColor
                            await message.edit(embed=discord.Embed.from_dict(dict_embed))
                        
                        await response.delete()
                    
                    # Prompts the user to confirm all their submitted information is correct
                    step_four = True
                    while step_four:
                        dict_embed['description'] = "Does everything look correct? Let me know with 'yes' or 'no'."
                        await message.edit(embed=discord.Embed.from_dict(dict_embed))
                    
                        response = await self.bot.wait_for('message', check=check)
                        if response.content.lower() == 'yes':
                            # Ends both loops
                            step_four = False
                            master_loop = False
                            
                            await response.delete()
                            
                            # Builds the registration embed for #new-registrations
                            registration_channel = self.bot.get_channel(config.newRegChannel)
                            dict_embed['title'] = "{}: {}".format(author.name, author.id)
                            dict_embed['description'] = ""
                            dict_embed['footer'] = {'text' : "Use !accept <id> to accept this registration"}
                            
                            embed = discord.Embed.from_dict(dict_embed)
                            embed.set_thumbnail(url=author.avatar_url)
                            # Sends the registration
                            registration_message = await registration_channel.send(embed=embed)
                            
                            admin.writeDirectory(author, 'tnp', {"channel" : "", "registration" : registration_message.id})
                            admin.updateDirectory()
                            
                            dict_embed['title'] = author.name
                            dict_embed['description'] = "Alright! You're all set. Available teachers have been notified of your registration. If one decides that you are a good match for them, you will be notified."
                            await message.edit(embed=discord.Embed.from_dict(dict_embed))
                            await asyncio.sleep(120)
                            await channel.set_permissions(author, send_messages = False, read_messages = False)
                            await message.delete()
                        
                        elif response.content.lower() == 'no':
                            dict_embed['description'] = "Okay, let's go back to the top. what is your time-zone?"
                            dict_embed['color'] = config.welcomeColor
                            dict_embed['footer'] = {'text' : "Step 1/3"}
                            dict_embed['fields'] = []
                            await message.edit(embed=discord.Embed.from_dict(dict_embed))
                            step_four = False
                        
                        await response.delete()

    ## Unregisters from The Neytiri Project
    @commands.command(name='unregister')
    async def unregisterTNP(self, ctx):
        if ctx.guild.id == config.KTID:
            user = ctx.message.author
            channel = self.bot.get_channel(config.regChannel) #registration
            reg_channel = self.bot.get_channel(config.newRegChannel) #new-registrations
            
            profile = admin.readDirectory(user)
            
            # Checks registered users for the command author's id
            if type(profile['tnp']['registration']) == int:
                # Removes registration entry in #new-registrations
                try:
                    message = await reg_channel.fetch_message(profile['tnp']['registration'])
                    await message.delete()
                except discord.errors.NotFound:
                    print("Original message has been deleted!")
                
                profile['tnp']['registration'] = ''
                
                # Removes relevant roles
                await user.remove_roles(get(ctx.guild.roles, id=config.tnpID)) # @TNP
            
            elif type(profile['tnp']['channel']) == int:
                # Removes the teacher's channel
                teacher_channel = self.bot.get_channel(profile['tnp']['channel'])
                await teacher_channel.delete()
                
                # Removes relevant roles 
                await user.remove_roles(get(ctx.guild.roles, id=config.tnpKaryuID)) # @TNPKaryu
            
            try:
                if type(profile['tnp']['accepted_by']) == int:
                    teacher_profile = admin.readDirectory(ctx.guild.get_member(profile['tnp']['accepted_by']))
                    teacher_channel = self.bot.get_channel(teacher_profile['tnp']['channel'])
                    
                    await teacher_channel.set_permissions(user, send_messages = False, read_messages = False)
            except:
                profile['tnp']['accepted_by'] = ""
            
            # Revokes access to #registration if accessible
            await channel.set_permissions(user, send_messages = False, read_messages = False)
            
            embed = discord.Embed(description="Unregistered you.")
            await ctx.send(embed=embed)
            
            admin.updateDirectory()

    # Error Handling

    ## Error Handling for !generate
    @generate.error
    async def generate_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(embed=config.syntax)

    ## Error Handling for !quiz
    @quiz.error
    async def quiz_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(embed=config.syntax)

def setup(bot):
    bot.add_cog(Utility(bot))
    print('Initialzed Kelutral.org Discord command set.')