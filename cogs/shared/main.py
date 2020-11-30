import discord
from discord.ext import commands
from discord.utils import get

import bot
import config
import admin
import pr_admin

import sys
import re
import json
import time
import git
import os
import random
from datetime import datetime
from importlib import reload

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ## -- Reads the necessary files and builds the output for the Leaderboard and Profile commands.
    async def buildLeaderboard(self, ctx, user_id, variant, requested_info):
        messageCounts = []
        userNames = []
        search_user = ctx.message.guild.get_member(user_id)
        t1 = time.time()
        
        ## -- Builds the Current Leaderboard
        async for member in ctx.guild.fetch_members(limit=None):
            profile = admin.readDirectory(member)
            
            if profile != None:
                if member.nick == None:
                    userNames.append(str(member.name))
                    user = ""
                else:
                    userNames.append(str(member.nick))
                    user = ""
                
                ## -- Checks the variant of leaderboard to build.
                if variant.lower() == "messages":
                    messageCounts.append(admin.readDirectory(member, "message count"))
                elif variant.lower() == "thanks":
                    try:
                        messageCounts.append(admin.readDirectory(member, "thanks"))
                    except:
                        messageCounts.append(0)
            
        sortedUserNames = [x for _,x in sorted(zip(messageCounts, userNames))]
        sortedMessageCounts = sorted(messageCounts)
        sortedUserNames.reverse()
        sortedMessageCounts.reverse()

        ## -- Indexes by the user who is being searched to find their position on the leaderboard
        if search_user.nick == None:
            pos = sortedUserNames.index(search_user.name) + 1
        else:
            pos = sortedUserNames.index(search_user.nick) + 1
            
        tDelta = round(time.time() - t1, 3)

        return {
            "full"    : [sortedUserNames, sortedMessageCounts, pos, tDelta], # Conditional return for !leaderboard
            "position": pos                                                  # Conditional return for !profile
            }.get(requested_info)

    ## Display Server Leaderboard
    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx, variant):
        leaderboard = ""
        
        # Checks for a valid variant and builds the overall server leaderboard list
        if variant.lower() == "messages" or variant.lower() == "thanks":
            output = await self.buildLeaderboard(ctx, ctx.message.author.id, variant, "full")
        else:
            await ctx.send(embed=config.syntax)
            return
        
        # Builds the top 10 list
        for i in range(0,10):
            leaderboard += "**{}**\n{} messages | Rank #{}\n\n".format(output[0][i], output[1][i], i + 1)
        
        # Builds final embed
        embed=discord.Embed(title="Server Leaderboard:", description=leaderboard, color=config.reportColor)
        if config.debug == True:
            embed.set_footer(text="You are ranked #{} overall. | Executed in {} seconds.".format(output[2], output[3]))
        else:
            embed.set_footer(text="You are ranked #{} overall.".format(output[2]))
        
        # Sends results
        await ctx.send(embed=embed)

    ## Display User Message Count
    @commands.command(name='profile', aliases=['yì'])
    async def profile(self, ctx, user: discord.Member, *setting):
        preference = ''.join(setting).lower()
        variant = "messages"
        
        # Function for building the final profile output
        async def buildEmbed(user, language_pref, to_next_level, active_roles):
            final_text = ''
            # Checks if the user has a nickname
            try:
                nickname = " AKA \"{}\"".format(user.nick)
            except:
                nickname = ""
                
            # Checks if the user has 'unspecified'
            if ctx.guild.id == 715043968886505484:
                if type(admin.readDirectory(user, "pronouns")) == int:
                    pronoun_role = get(user.guild.roles, id=admin.readDirectory(user, "pronouns")).name
                else:
                    pronoun_role = admin.readDirectory(user, "pronouns")
                
            # Builds the embed
            embed=discord.Embed(color=get(user.guild.roles, id=active_roles["id"]).color, title=user.name + nickname)
            embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["join_date"], value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
            embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["language"], value=language_pref, inline=True)
            if ctx.guild.id == 715043968886505484:
                embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["pronouns"], value=pronoun_role, inline=True)
                embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["current_rank"], value=get(user.guild.roles, id=active_roles["id"]).mention + ", \"" + active_roles["translation"] + "\"")
            else:
                embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["current_rank"], value=get(user.guild.roles, id=active_roles["id"]).mention)
            embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["message_count"], value=to_next_level, inline=True)
            if type(admin.readDirectory(user, "na'vi only")) == int:
                final_text += "{} **messages**: {}\n".format(self.bot.get_channel(715050499203661875).mention, admin.readDirectory(user, "na'vi only"))
            final_text += "**{}** {}\n".format(config.text_file[language_pref]["profile"]["embed"]["server_leaderboard"], await self.buildLeaderboard(ctx, user.id, variant, "position"))
            final_text += "**{}** {}\n".format(config.text_file[language_pref]["profile"]["embed"]["times_thanked"], admin.readDirectory(user, "thanks"))
            embed.add_field(name="Additional Stats:", value=final_text, inline=False)
            embed.set_footer(text=config.text_file[language_pref]["profile"]["embed"]["footer"])
            embed.set_thumbnail(url=user.avatar_url) 
            
            return embed
        
        # Time start
        t1 = time.time()
        
        # Pulls necessary information from the user profile
        message_count = admin.readDirectory(user, "message count")
        language_pref = admin.readDirectory(user, "language")
        if ctx.guild.id == 748700165266866227:
            active_roles = pr_admin.readDirectory(user, "pr_rank")
        else:
            active_roles = admin.readDirectory(user, "rank")
        
        # Retrieves the current and next rank from Discord
        current_rank = get(ctx.guild.roles, id=active_roles["id"])
        if ctx.guild.id == 748700165266866227:
            try:
                next_rank_index = config.prIDs.index(current_rank.id) - 1
            except AttributeError:
                next_rank_index = config.prIDs.index(782980232746893343)
            next_rank = get(ctx.guild.roles, id=config.prIDs[next_rank_index])
            next_rank_translation = next_rank.name
        else:
            next_rank_index = config.activeRoleIDs.index(current_rank.id) - 1
            next_rank = get(ctx.guild.roles, id=config.activeRoleIDs[next_rank_index])
            for entry in config.activeRoleDict:
                if entry[0] == next_rank.id:
                    next_rank_translation = entry[1]
                    break
        
        # Checks the total messages sent against the threshold.
        for i, count in enumerate(config.activeRoleThresholds):
            if message_count >= count and i == 0:
                toNextLevel = 0
                break
            elif message_count >= count:
                toNextLevel = config.activeRoleThresholds[i - 1] - int(message_count)
                break
            elif message_count <= 8:
                toNextLevel = 8 - int(message_count)
                break
        
        output2 = str(toNextLevel)
            
        # Checks the command arguments for updated language preference
        # No update
        if preference == "":
            preference = language_pref
            if preference == "Na'vi":
                str_message_count = bot.wordify(str(oct(message_count))[2:]).capitalize()
                output2 = bot.wordify(str(oct(toNextLevel))[2:])
            elif preference == "English":
                str_message_count = str(message_count)
                
            if toNextLevel < 0:
                to_next_level = config.text_file[language_pref]["profile"]["max_rank"].format(str_message_count)
            else:
                to_next_level = config.text_file[language_pref]["profile"]["rank_progress"].format(str_message_count, output2, next_rank.mention, next_rank_translation)
            
            embed = await buildEmbed(user, language_pref, to_next_level, active_roles)
        # Update
        elif user.id == ctx.message.author.id:
            if preference.capitalize() == "Na'vi":
                str_message_count = bot.wordify(str(oct(message_count))[2:]).capitalize()
                output2 = bot.wordify(str(oct(toNextLevel))[2:])
            elif preference.capitalize() == "English":
                str_message_count = str(message_count)
            else:
                await ctx.send(embed=discord.Embed(description=config.text_file[language_pref]["errors"]["profile"] + config.text_file[language_pref]["errors"]["profile_errors"]["invalid_language"], color=config.failColor))
                return
            
            language_pref = preference.capitalize()
            admin.writeDirectory(user, "language", language_pref)

            if toNextLevel < 0:
                to_next_level = config.text_file[language_pref]["profile"]["max_rank"].format(str_message_count)
            else:
                to_next_level = config.text_file[language_pref]["profile"]["rank_progress"].format(str_message_count, output2, next_rank.mention, next_rank_translation)
            
            embed = await buildEmbed(user, language_pref, to_next_level, active_roles)
        # Invalid entry
        else:
            embed=discord.Embed(description=config.text_file[language_pref]["errors"]["profile"] + config.text_file[language_pref]["errors"]["profile_errors"]["missing_perms"], color=config.failColor)
               
        # Checks debug state and sends final embed.
        if config.debug:
            embed.set_footer(text="Executed in {} seconds.".format(round(time.time() - t1, 3)))
        await ctx.send(embed=embed)

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
        embed.add_field(name="Kelutral Server: ", value="http://discord.gg/YSyvBEF", inline=True)
        embed.add_field(name="Pandora Rising: ", value="http://discord.gg/xKV88se", inline=True)
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
        if ctx.message.author.top_role.id in config.modRoles:
            await ctx.send("Reloading the bot...")
            reload(config)
            await ctx.send("Launching bot version {}".format(config.version))
            await self.bot.close()
            os.execv(sys.executable, ['python3'] + sys.argv)

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
        
    ## Show Invite
    @commands.command(name="invite")
    async def showInvite(self, ctx, *variant):
        variant = ' '.join(variant)
        if variant.lower() == "kelutral":
            await ctx.send("http://discord.gg/YSyvBEF")
        elif variant.lower() == "pandora rising" or variant.lower() == "pr":
            await ctx.send("http://discord.gg/xKV88se")
        else:
            await ctx.send(embed=config.syntax)
           
    # Error Handling
    
    ## Error Handling for !profile
    @profile.error
    async def profile_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(embed=config.syntax)

def setup(bot):
    bot.add_cog(Utility(bot))
    print('Initialized utility command set.')