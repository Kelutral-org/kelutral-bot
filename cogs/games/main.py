import discord
from discord.ext import commands

import bot
import config
import admin
import namegen

import random
import asyncio
from datetime import datetime
import os
import json
import time

class Games(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
    ## -- Updates the Visible Stat for 'names generated'
    def update(self, newNameCount):
        with open(config.botFile, 'r') as fh:
            nameCount = json.load(fh)
        
        nameCount[0] = nameCount[0] + newNameCount
        
        with open(config.botFile, 'w') as fh:
            json.dump(nameCount, fh)
            
        return nameCount[0]

    ## -- Checks for empty args
    def is_empty(self, any_structure):
        if any_structure:
            return False
        else:
            return True

    ## Generate # of random names
    @commands.command(name="generate",aliases=['ngop'])
    async def generate(self, ctx, numOut, numSyllables, *letterPrefs):
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

    ## 8 Ball Command
    @commands.command(name="8ball")
    async def eightBall(self, ctx, *args):
        user = ctx.message.author
        question = " ".join(args)
        
        index = random.randint(0,12)
        options = config.text_file[admin.readDirectory(user, "language")]["8ball"]["options"]
        embed = discord.Embed(description=config.text_file[admin.readDirectory(user, "language")]["8ball"]["response"].format(user.mention, question, config.text_file[admin.readDirectory(user, "language")]["8ball"]["options"][index].format(question)))
        
        await ctx.send(embed=embed)
        if index == 12:
            await ctx.send("%q {}".format(question))
        
    ## Thank the Bot
    @commands.command(name="thanks", aliases=['irayo'])
    async def thanks(self, ctx):
        language = admin.readDirectory(ctx.message.author, "language")
        await ctx.send(config.text_file[language]["thanks"].format(ctx.message.author.mention))
        
    ## Error Handling for !quiz
    @quiz.error
    async def quiz_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(embed=config.syntax)
    
    ## Error Handling for !generate
    @generate.error
    async def generate_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(embed=config.syntax)

def setup(bot):
    bot.add_cog(Games(bot))
    print('Added new Cog: ' + str(Games))