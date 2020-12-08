    @commands.command(name="search")
    async def search(self, ctx, *words):
        if isinstance(ctx.channel, discord.channel.DMChannel) or ctx.guild.id == config.KTID:
            user = ctx.message.author
            words = list(words)
            
            verbs = ["v.", "vtr.", "vin.", "vtrm.", "vim."]
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
                
            # Loads the dictionary
            with open(config.dictionaryFile, 'r', encoding='utf-8') as fh:
                dictionary = json.load(fh)
            
            # Automatically combines 'si' verbs to prevent needing quotes in lookup
            i = 0
            word_list = []
            for word in words:
                # If 'si'-variant is found in the word
                if re.search(r"si|s..i|s...i", word) != None:
                    # If 'si'-variant is the first word, appends the 'si'-variant
                    if len(word_list) == 0:
                        word_list.append(word)
                    # If 'si'-variant is not the first word, combines the 'si'-variant with the previous list entry
                    else:
                        word_list[i-1] += " {}".format(word)
                # If 'si'-variant is not found in the word
                else:
                    word_list.append(word)
                    i += 1

            def checkLenition(lenited_word):
                lenition_rules = [['p','f'],['t','s'],['k','h'],['px','p'],['tx','t'],['kx','k'],['ts','s']]
                possible_words = []
                for lenited_character in lenition_rules:
                    # If there's a possible match in the initial character of the word, appends the non-lenited word
                    if lenited_word[0] == lenited_character[1]:
                        possible_words.append(lenited_character[0] + lenited_word[1:])

                return possible_words
                
            def checkNoun(word_to_check):
                for case_name, case_endings in cases.items():
                    for suffix in case_endings:
                        if word_to_check.endswith(suffix):
                            core_word = word_to_check.replace(suffix, "")
                            unlenited_word_list = checkLenition(core_word)
                            if unlenited_word_list != []:
                                for unlenited_word in unlenited_word_list:
                                    if unlenited_word in dictionary:
                                        if checkElement(dictionary[unlenited_word], "partOfSpeech", ["n.","pn."]):
                                            parsed_word[unlenited_word] = {"stripped" : unlenited_word, "notes" : "\n- lenition\n- {}".format(case_name)}
                                            return parsed_word
                            else:
                                word_with_tìftang = "'{}".format(core_word)
                                if word_with_tìftang in dictionary:
                                    if checkElement(dictionary[word_with_tìftang], "partOfSpeech", ["n.","pn."]):
                                        parsed_word[word_with_tìftang] = {"stripped" : word_with_tìftang, "notes" : "\n- lenition\n- {}".format(case_name)}
                                        return parsed_word
                                elif core_word in dictionary:
                                    if checkElement(dictionary[core_word], "partOfSpeech", ["n.","pn."]):
                                        parsed_word[core_word] = {"stripped" : core_word, "notes" : "\n- {}".format(case_name)}
                                        return parsed_word
                
                for plural, prefix in plurals.items():
                    if word_to_check.startswith(prefix):
                        core_word = word_to_check.replace(prefix, "")
                        unlenited_word_list = checkLenition(core_word)
                        if unlenited_word_list != []:
                            for unlenited_word in unlenited_word_list:
                                if unlenited_word in dictionary:
                                    if checkElement(dictionary[unlenited_word], "partOfSpeech", ["n.","pn."]):
                                        parsed_word[unlenited_word] = {"stripped" : unlenited_word, "notes" : "\n- lenition\n- {}".format(plural)}
                                        return parsed_word
                        else:
                            word_with_tìftang = "'{}".format(core_word)
                            if word_with_tìftang in dictionary:
                                if checkElement(dictionary[word_with_tìftang], "partOfSpeech", ["n.","pn."]):
                                    parsed_word[word_with_tìftang] = {"stripped" : word_with_tìftang, "notes" : "\n- lenition\n- {}".format(plural)}
                                    return parsed_word
                            elif core_word in dictionary:
                                if checkElement(dictionary[core_word], "partOfSpeech", ["n.","pn."]):
                                    parsed_word[core_word] = {"stripped" : core_word, "notes" : "\n- {}".format(plural)}
                                    return parsed_word

            for word in words:
                if word in dictionary:
                    parsed_word[word] = {"stripped" : word, "notes" : ""}
                
                # Words with spaces will automatically be 'si'-verbs, so this excludes those. Checks the word for noun modifications like plurals, cases or lenition.
                if " " not in word:
                    parsed_word = checkNoun(word)
                
            
            def stripAffixes(word):
                parsed_word = {}
                found = False
                
                cases = {
                    "agentive" : ["l","ìl"],
                    "patientive" : ["t","ti","it"],
                    "dative" : ["r","ur","ru"],
                    "genitive" : ["ä","yä"],
                    "topical" : ["ri","ìri"]
                    }
                    
                plurals = {
                    "dual" : 'me',
                    "trial" : 'pxe',
                    "plural" : 'ay'
                    }
                
                first_pos_infixes = [
                           {"↩️ causative reflexive" : 'äpeyk'},     # Causative reflexive
                           {"➡️ causative" : 'eyk'},                 # Causative
                           {"⬅️ reflexive" : 'äp'},                  # Reflexive
                           {"⏹️ perfective" : 'ol'},                 # Perfective
                           {"↔️ progressive" : 'er'},                # Progressive
                           {"❔ subjunctive" : 'iv'},                # Subjunctive compounds
                           {"⏪ near past" : 'ìm'},
                           {"⏩ near future" : 'ìy'},
                           {"⏭️ general future" : 'ay'},
                           {"❓ perfective subjunctive" : 'ilv'},
                           {"❔↔️ progressive subjunctive" : 'irv'},
                           {"❔⏩ future subjunctive a" : 'ìyev'},
                           {"❔⏩ future subjunctive b" : 'iyev'},
                           {"⏭️☑️ general future intent" : 'asy'},     # Intent
                           {"⏩☑️ near future intent" : 'ìsy'},
                           {"⏹️⏮️ general past perfective" : 'alm'},   # Perfective compounds
                           {"⏹️⏪ near past perfective" : 'ìlm'},
                           {"⏹️⏭️ general future perfective" : 'aly'},
                           {"⏹️⏩ near future perfective" : 'ìly'},
                           {"↔️⏮️ general past progressive" : 'arm'},  # Progressive compounds
                           {"↔️⏪ near past progressive" : 'ìrm'},
                           {"↔️⏭️ general future progressive" : 'ary'},
                           {"↔️⏩ near future progressive" : 'ìry'},
                           {"progressive participle" : 'us'},     # Participles
                           {"passive participle" : 'awn'},
                           {"❔⏮️ past subjunctive" : 'imv'},
                           {"⏮️ general past" : 'am'}]
                           
                second_pos_infixes = [
                           {"😃 positive mood (H**2.3.3**)" : 'eiy'},# Mood
                           {"😃 positive mood" : 'ei'},              
                           {"😃 positive mood (H**2.3.3**)" : 'eiy'},
                           {"😔 negative mood" : 'äng'},
                           {"😔 negative mood (H**2.3.5.2**)" : 'eng'},
                           {"🕵️ inferential" : 'ats'},               # Inferential
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
                    # Multiple Infix Checking
                    tense_list = []
                    str_tenses = []
                    
                    def validate_pos(word, core_word, infixes, pos):
                        try:
                            validated = False
                            check = dictionary[core_word]
                        except KeyError:
                            return False
                            
                        for entry in check:
                            if checkElement(dictionary[core_word], "partOfSpeech", verbs):
                                if pos == 1:
                                    for infix in infixes:
                                        split_list = entry["infixDots"].split(".")
                                        split_list.insert(1, ".")
                                        joined_word = ''.join(split_list)
                                        index = joined_word.find(".")
                                        if index == word.find(infix[0]):
                                            validated = True
                                        else:
                                            return False
                                elif pos == 2:
                                    for infix in infixes:
                                        print(infix)
                                        split_list = entry["infixDots"].split(".")
                                        split_list.insert(2, ".")
                                        joined_word = ''.join(split_list)
                                        index = joined_word.find(".")
                                        if index == word.find(infix[0]):
                                            validated = True
                                        else:
                                            return False
                                        
                        return validated
                    
                    def findInfix(core_word, infix, expected_pos):
                        tense = list(infix.keys())[0]
                        infix = list(infix.values())[0]
                        found = False
                        verb = re.search(r"{}".format(infix), core_word)
                        if verb != None:
                            found = True
                            return core_word.replace("{}".format(infix), "", 1), tense, infix, found
                        else:
                            return core_word, "", "", found
                    
                    if not found:
                        core_word = word
                        def check_first_pos(core_word):
                            for infix in first_pos_infixes:
                                core_word, tense, infix_str, check = findInfix(core_word, infix, 1)
                                if check:
                                    tense_list.append(tense)
                                    str_tenses.append((infix_str, 1))
                                    try:
                                        word_entry = dictionary[core_word]
                                        if word_entry[0]["partOfSpeech"] in verbs:
                                            parsed_word[word] = {"stripped" : core_word, "notes" : "\n- {}".format('\n- '.join(tense_list))}
                                            
                                            return parsed_word, tense_list, str_tenses, True
                                        else:
                                            continue
                                    except KeyError:
                                        continue
                            
                            return core_word, tense_list, str_tenses, False
                            
                        def check_second_pos(core_word):
                            for infix in second_pos_infixes:
                                if not list(infix.values())[0] == "äng":
                                    core_word, tense, infix_str, check = findInfix(core_word, infix, 2)
                                    if check:
                                        tense_list.append(tense)
                                        str_tenses.append((infix_str, 2))
                                        try:
                                            word_entry = dictionary[core_word]
                                            if word_entry[0]["partOfSpeech"] in verbs:
                                                parsed_word[word] = {"stripped" : core_word, "notes" : "\n- {}".format('\n- '.join(tense_list))}
                                                
                                                return parsed_word, tense_list, str_tenses, True
                                            else:
                                                continue
                                        except KeyError:
                                            continue
                                else:
                                    if "ängkxängo" in word:
                                        tense_list.append("negative mood")
                                        str_tenses.append(("äng", 2))
                                        core_word = core_word.replace("ängkxängo","ängkxo")
                                        try:
                                            word_entry = dictionary[core_word]
                                            if word_entry[0]["partOfSpeech"] in verbs:
                                                parsed_word[word] = {"stripped" : core_word, "notes" : "\n- {}".format('\n- '.join(tense_list))}
                                                
                                                return parsed_word, tense_list, str_tenses, True
                                            else:
                                                continue
                                        except KeyError:
                                            continue
                                    else:
                                        core_word, tense, infix_str, check = findInfix(core_word, infix, 2)
                                        if check:
                                            tense_list.append(tense)
                                            str_tenses.append((infix_str, 2))
                                            try:
                                                word_entry = dictionary[core_word]
                                                if word_entry[0]["partOfSpeech"] in verbs:
                                                    parsed_word[word] = {"stripped" : core_word, "notes" : "\n- {}".format('\n- '.join(tense_list))}
                                                    
                                                    return parsed_word, tense_list, str_tenses, True
                                            except KeyError:
                                                continue
                                            
                            return core_word, tense_list, str_tenses, False
                        
                        output_word, tense_list, str_tenses, finished_strip = check_second_pos(core_word)

                        if not finished_strip:
                            output_word, tense_list, str_tenses, finished_strip = check_first_pos(output_word)

                            if not finished_strip:
                                print("")
                            elif not validate_pos(word, output_word[word]["stripped"], str_tenses, 1):
                                parsed_word[word] = {"stripped" : word, "notes" : ""}
                                return parsed_word
                            else:
                                return output_word
                        elif not validate_pos(word, output_word[word]["stripped"], str_tenses, 2):
                            parsed_word[word] = {"stripped" : word, "notes" : ""}
                            return parsed_word
                        else:
                            return output_word
                    
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
                
                # Lenition check
                if not nv_found:
                    possible_words = checkLenition(word)
                    for key in dictionary.keys():
                        if word[1:] in key:
                            if possible_words != []:
                                for result in possible_words:
                                    try:
                                        word_entry = dictionary[result.lower()]
                                        if word_entry[0]["partOfSpeech"] not in verbs:
                                            results += buildResults(i, word_entry, word, result.lower(), ": lenition", True)
                                            found_count += len(word_entry)
                                            nv_found = True
                                            possible_words = []
                                            break
                                        else:
                                            continue
                                    except KeyError:
                                        continue
                            else:
                                try:
                                    word_entry = dictionary["'{}".format(word).lower()]
                                    if word_entry[0]["partOfSpeech"] not in verbs:
                                        results += buildResults(i, word_entry, word, "'{}".format(word).lower(), ": lenition", True)
                                        found_count += len(word_entry)
                                        nv_found = True
                                        possible_words = []
                                        break
                                    else:
                                        continue
                                except KeyError:
                                    continue
                
                # Reverse lookup
                if not searchAll:
                    for key, value in dictionary.items():
                        for k, sub in enumerate(value):
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
