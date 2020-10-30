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

# Replace RandomCog with something that describes the cog.  E.G. SearchCog for a search engine, sl.
class Games(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
    ## -- Updates the Visible Stat for 'names generated'
    def update(self, newNameCount):
        fileName = 'files/users/bot.tsk'
        if os.path.exists(fileName): # If bot file exists
            with open(fileName, 'r') as fh:
                nameCount = json.load(fh)
            
            nameCount[0] = nameCount[0] + newNameCount
            
            with open(fileName, 'w') as fh:
                json.dump(nameCount, fh)
            
        return nameCount[0]

    ## Generate # of random names
    @commands.command(name="generate",aliases=['ngop'])
    async def generate(self, ctx, numOut, numSyllables, *letterPrefs):
        user = ctx.message.author
        n = int(numOut)
        i = int(numSyllables)
        output = []
        c = 0
        language = admin.readDirectory(user, "language")
        
        if not n <= 0 and not i <= 0:
            if not i <= 5:
                embed=discord.Embed(description=config.text_file[language]["errors"]["generate_error"] + config.text_file[language]["errors"]["generate_errors"]["syllables"], colour=config.failColor) 
                await ctx.send(embed=embed)
                
            elif not n <= 20:
                embed=discord.Embed(description=config.text_file[language]["errors"]["generate_error"] + config.text_file[language]["errors"]["generate_errors"]["names"], colour=config.failColor) 
                await ctx.send(embed=embed)
                
            else:
                nameCount = self.update(n)
                game = discord.Game("ngamop " + "{:,}".format(nameCount) + " tstxoti.")
        
                await self.bot.change_presence(status=discord.Status.online, activity=game)

                embed=discord.Embed(color=config.successColor)
                embed.set_author(name=config.text_file[language]["generate"]["success"].format(ctx.message.author.name))
                
                while c < n:
                    output.append(namegen.nameGen(numSyllables, letterPrefs))
                    embed.add_field(name=config.text_file[language]["generate"]["name"] + str(c + 1) + ":", value=output[c], inline=True)
                    c += 1
                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                
                await ctx.send(embed=embed)

        else:
            embed=discord.Embed(description=config.text_file[language]["errors"]["generate_error"] + config.text_file[language]["errors"]["generate_errors"]["zero"], color=config.failColor)
            await ctx.send(embed=embed)
        
        now = datetime.strftime(datetime.now(),'%H:%M')
        print(now + " -- " + ctx.author.name + " generated " + str(n) + " names.")

    # Quiz Command
    @commands.command(name="quiz",aliases=['fmetok'])
    async def quiz(self, ctx, *args):
        iteration = 0
        needStudy = []
        
        if len(args) > 2:
            await ctx.send(embed=config.arguments)
            return
        elif len(args) == 2:
            for test in args:
                try:
                    val = int(test)
                    rounds = val
                except ValueError:
                    lang = test
        elif len(args) == 1:
            for test in args:
                try:
                    val = int(test)
                    rounds = val
                    lang = "English"
                except ValueError:
                    lang = test
                    rounds = 1
        else:
            lang = "English"
            rounds = 1
        
        if rounds > 10 or rounds < 1:
            await ctx.send(embed=config.syntax)
        else:
            correct = 0
            incorrect = 0
            while iteration < abs(int(rounds)):
                i = 0
                allDefinitions = []

                fileLen = len(config.words)
                correctEntry = random.randint(1,fileLen)
                selectedEntry = config.words[correctEntry]
                
                if lang.lower() == "english":
                    nv = selectedEntry[0]
                    correctDef = selectedEntry[1]
                    
                    embed=discord.Embed(title="Na'vi to English: " + nv, description="React with the appropriate letter to submit your answer for the correct definition.", color=config.quizColor)
                    
                    while i < 3:
                        index = random.randint(1,fileLen)
                        if index == correctEntry:
                            while index == correctEntry:
                                index = random.randint(1,fileLen)
                        else:
                            randomDef = config.words[index]
                            randomDef = randomDef[1]
                            allDefinitions.append(randomDef)
                            i += 1
                            
                elif lang.lower() == "na'vi":
                    nv = selectedEntry[1]
                    correctDef = selectedEntry[0]

                    embed=discord.Embed(title="English to Na'vi: " + nv, description="React with the appropriate letter to submit your answer for the Na'vi counterpart.", color=config.quizColor)
                    
                    while i < 3:
                        index = random.randint(1,fileLen)
                        if index == correctEntry:
                            while index == correctEntry:
                                index = random.randint(1,fileLen)
                        else:
                            randomDef = config.words[index]
                            randomDef = randomDef[0]
                            allDefinitions.append(randomDef)
                            i += 1

                else:
                    value = "{}".format("**Error: Invalid language** \n Please use `English` or `Na'vi`.")
                    embed = discord.Embed(description=value, color=config.failColor)
                    await ctx.send(embed=embed)
                    return
                
                allDefinitions.append(correctDef)
                
                random.shuffle(allDefinitions)
                
                message = await ctx.send(embed=embed)
                
                emojis = ['\U0001F1E6','\U0001F1E7','\U0001F1E8','\U0001F1E9']
                for emoji in emojis:
                    await message.add_reaction(emoji)
                
                alphabet = ['A', 'B', 'C', 'D']
                for i, letter in enumerate(alphabet):
                    embed.add_field(name="Definition {}".format(letter), value=allDefinitions[i],inline=False)
                await message.edit(embed=embed)
                    
                def check(reaction, user):
                    for emoji in emojis:
                        if str(reaction.emoji) == emoji:
                            foundEmoji = True
                            break
                        else:
                            foundEmoji = False

                    return user == ctx.message.author and foundEmoji
                
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
                except asyncio.TimeoutError:
                    embed=discord.Embed(title="Word: " + nv, description="Sorry, you took too long to answer! The correct answer was " + nv + ", **" + correctDef + "**. Try again!", color=config.failColor)
                    needStudy.append("**" + nv + "**, *" + correctDef + "*\n")
                    
                    await message.clear_reactions()
                    await message.edit(embed=embed)
                else:
                    i = 0
                    while i < 4:
                        if str(reaction) == emojis[i]:
                            v = 0
                            for emoji in emojis:
                                if emojis[v] == str(reaction):
                                    response = v
                                else:
                                    v += 1

                            
                            if allDefinitions[v] == correctDef:
                                if ctx.message.guild:
                                    await message.clear_reactions()
                                embed=discord.Embed(title="Word: " + nv, description="Congratulations ma " + str(ctx.message.author.mention)+ ", you were correct!", color=config.successColor)
                                embed.add_field(name="Definition " + alphabet[v], value=correctDef,inline=False)
                                await message.edit(embed=embed)
                                
                                correct += 1
                            else:
                                if ctx.message.guild:
                                    await message.clear_reactions()
                                embed=discord.Embed(title="Word: " + nv, description="Sorry ma " + str(ctx.message.author.mention)+ ", the correct answer was **" + correctDef + "**. Your answer was: ", color=config.failColor)
                                embed.add_field(name="Definition " + alphabet[v], value=allDefinitions[v],inline=False)
                                await message.edit(embed=embed)
                                
                                incorrect += 1
                                needStudy.append("**" + nv + "**, *" + correctDef + "*\n")
                            break
                        else:
                            i += 1
                iteration += 1

            if correct == 0:
                embed = discord.Embed(title="Results", description="You got " + str(correct) + " out of " + str(rounds) + " correct, try again! \n\n Here are the words you need to work on:")
                for i in needStudy:
                    embed.add_field(name="Word:", value=i)
            elif correct == rounds:
                embed = discord.Embed(title="Results", description="Nice work! You got " + str(correct) + " out of " + str(rounds) + " correct!")
            else:
                embed = discord.Embed(title="Results", description="You got " + str(correct) + " out of " + str(rounds) + " correct, not bad! \n\n Here are the words you need to work on:")
                for i in needStudy:
                    embed.add_field(name="Word:", value=i)
            await ctx.send(embed=embed)

    ## 8 Ball Command
    @commands.command(name="8ball")
    async def eightBall(self, ctx, *args):
        user = ctx.message.author
        question = " ".join(args)
        
        index = random.randint(0,11)
        options = config.text_file[admin.readDirectory(user, "language")]["8ball"]["options"]
        embed = discord.Embed(description=config.text_file[admin.readDirectory(user, "language")]["8ball"]["response"].format(user.mention, question, config.text_file[admin.readDirectory(user, "language")]["8ball"]["options"][index]))
        
        await ctx.send(embed=embed)
        
    ## Thank the Bot
    @commands.command(name="thanks", aliases=['irayo'])
    async def thanks(self, ctx):
        language = admin.readDirectory(ctx.message.author, "language")
        await ctx.send(config.text_file[language]["thanks"].format(ctx.message.author.mention))
        
    # Error Handling for !quiz
    @quiz.error
    async def quiz_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(embed=config.syntax)
    
    # Error Handling for !generate
    @generate.error
    async def generate_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(embed=config.syntax)

def setup(bot):
    bot.add_cog(Games(bot))
    print('Added new Cog: ' + str(Games))