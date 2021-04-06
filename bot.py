## ----------------------- ##
## KELUTRAL NETWORK BOT V2 ##
## ----------------------- ##

# -*- encoding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import json
import time
import os

from datetime import datetime

import config
import kt_config
import pr_config

start_time = datetime.now()

## -- Initialize Client
kelutral = discord.Client()

## -- Initialize Bot
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.presences = True
kelutralBot = commands.Bot(command_prefix=config.prefix, help_command=None, intents=intents)

## -- Clear screen function
def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

## -- Bot Events
@kelutralBot.event
async def on_ready():
    def update_bot_stats(newNameCount):
        with open(config.botFile, 'r') as fh:
            botStats = json.load(fh)
            nameCount = botStats["name_count"]
            nameCount += newNameCount
        
        with open(config.botFile, 'w') as fh:
            json.dump(botStats, fh)
            
        return nameCount
        
    nameCount = update_bot_stats(0)
    game = discord.Game("generated " + "{:,}".format(nameCount) + " names!")
    
    await kelutralBot.change_presence(status=discord.Status.online, activity=game)
    
    fileName = 'kelutral-bot/files/config/startup.txt'
    with open(fileName, 'r') as fh:
        lines = fh.readlines()
    
    ## -- Prints the Kelutral OS logo to the command line
    for line in lines:
        print(line.strip('\n').format(config.version))
        time.sleep(.025)
    
    time.sleep(1)
    clear()
    
    now = datetime.strftime(datetime.now(),'%H:%M')
    print(now + " - Watching activity on the network...")
    
    kelutralBot.loop.create_task(config.time_check(kelutralBot))
    
@kelutralBot.event
async def on_command(ctx):
    now = datetime.now().strftime('%H:%M')
    command = ctx.message.content.split(" ")[0]
    if command != "!lep":
        arguments = ctx.message.content.replace(command, "")
        config.log(f"{ctx.message.author.name}: {ctx.message.author.id} executed the {command} command with arguments: {arguments}")

## -- Bot Commands
# About the bot
@kelutralBot.command(name='about', aliases=['teri'])
async def about(ctx):
    mako = ctx.message.guild.get_member(config.makoID)
    self = ctx.message.guild.get_member(config.botID)
    t1 = time.time()

    with open(config.botFile, 'r') as fh:
        bot_stats = json.load(fh)
        
    embed=discord.Embed(title="About Eytukan",description=f"Eytukan is a custom bot coded in Python 3 for use on the Kelutral.org Network of Discord Servers. It is primarily coded and maintained by {mako.mention}.", color=config.botColor)
    embed.set_author(name=self.name,icon_url=self.avatar_url)
    embed.add_field(name="Version: ", value=config.version, inline=True)
    embed.add_field(name="Website: ", value="http://kelutral.org/", inline=True)
    embed.add_field(name="Discord.py:", value="Version " + str(discord.__version__))
    embed.add_field(name="Na'vi Names Generated: ", value=bot_stats["name_count"], inline=True)
    embed.add_field(name="Kelutral Server: ", value=kt_config.invite, inline=True)
    embed.add_field(name="Pandora Rising: ", value=pr_config.invite, inline=True)
    embed.set_thumbnail(url=ctx.guild.icon_url)
    
    tDelta = round(time.time()-t1,3)
    now_datetime = datetime.now() - start_time
    
    # Checks debug output toggle
    embed.set_footer(text=f"Use !help to learn more about the available commands. | Current uptime: {now_datetime.days} days, {divmod(now_datetime.seconds, 3600)[0]}:{divmod(now_datetime.seconds, 60)[0]}")
    if config.debug == True:
        embed.set_footer(text=f"Use !help to learn more about the available commands.  |  Executed in {str(tDelta)} seconds.")

    await ctx.send(embed=embed)
    
# Help Command
@kelutralBot.command(name="help", aliases=['srung','ehelp'])
async def help(ctx, *query):
    isTag = False
    query = list(query)
    t1 = time.time()
    
    async def build_help(variant, query):
        if len(query) > 0:
            if len(query) > 1:
                await ctx.send(embed=config.syntax)
                return
            else:
                query = query[0]
        elif len(query) == 0:
            query = ""
        output = ""
        if variant == "kelutral":
            lepChannel = kelutralBot.get_channel(kt_config.lepChannel)

            reykcommands = [('**run**','Translates a Na\'vi word into English.\n'),
                            ('**find**','Finds words whose English definitions contain the query.\n'),
                            ('**tslam**','Runs a grammar analyzer on your sentence.\n',)]
        
        if not isTag and query != "":
            try:
                command = config.helpFile[query]
                if variant in command['tags']:
                    embed = discord.Embed(title=command['name'], description=f"Aliases: {command['aliases']}\nUsage: {command['usage']}\nExample: {command['example']}\nDescription: {command['description']}")
                    embed.set_footer(text=f"Tags: {', '.join(command['tags'])}")
                else:
                    await ctx.send(embed=config.help_error)
                    return
            except KeyError:
                await ctx.send(embed=config.help_error)
                return
        elif query == "":
            for entry in config.helpFile.values():
                if variant in entry['tags']:
                    output = output + entry['name'] + ": " + entry['short']
                    
            if variant == "kelutral":
                # Reykunyu's command list
                output = output + "\n\nHere are {}'s available commands. Use `!run help` for additional support for Reykunyu's commands.\n\n".format(ctx.guild.get_member(kt_config.reykID).mention)
        
                for command in reykcommands:
                    output = output + command[0] + ": " + command[1]
            
            embed = discord.Embed(title="!help",description="Here are {}'s available commands on this server. Use `!help <command>` for more information about that command.\n\n".format(ctx.guild.get_member(config.botID).mention) + output)
            embed.set_thumbnail(url=ctx.guild.icon_url)
        else:
            for entry in config.helpFile.values():
                if query in entry['tags'] and variant in entry['tags']:
                    output = output + entry['name'] + ": " + entry['short']
            embed = discord.Embed(title="!help {}".format(query), description="Here are {}'s available commands on this server with tag `{}`.\n\nUse `!help <command>` for more information about that command.\n\n".format(ctx.guild.get_member(config.botID).mention, query) + output)
        
        return embed
    
    if "-t" in query:
        query.remove("-t")
        isTag = True
    
    if ctx.guild.id == kt_config.guild:
        embed = await build_help("kelutral", query)
    elif ctx.guild.id == pr_config.guild:
        embed = await build_help("pandora rising", query)

    if config.debug:
        embed.set_footer(text=f"Executed in {round(time.time() - t1, 3)} seconds.")
        
    await ctx.send(embed=embed)
    
## -- Error Handling
# !help errors
@help.error
async def help_error(ctx, error):
   if isinstance(error, commands.CommandError):
        print(error)
        await ctx.send(embed=config.syntax)
   else:
        await ctx.send(error)

def main():
    kelutralBot.load_extension('cogs.kelutral.kelutral_cog')
    kelutralBot.load_extension('cogs.pandora_rising.pr_cog')
    kelutralBot.load_extension('cogs.shared.shared_cog')
    kelutralBot.run(config.token)
    
main()