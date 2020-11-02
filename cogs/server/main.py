import discord
from discord.ext import commands
from discord.utils import get

import config
import admin

import re
import bot
import time

class Server(commands.Cog):
    def __init__(self,bot):
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
            
        t2 = time.time()
        tDelta = round(t2 - t1, 3)

        return {
            "full"    : [sortedUserNames, sortedMessageCounts, pos, tDelta], # Conditional return for !leaderboard
            "position": pos                                                  # Conditional return for !profile
            }.get(requested_info)

    ## Display Server Leaderboard
    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx, variant):
        i = 0
        leaderboard = ""
        
        # Checks for a valid variant and builds the overall server leaderboard list
        if variant.lower() == "messages" or variant.lower() == "thanks":
            output = await self.buildLeaderboard(ctx, ctx.message.author.id, variant, "full")
        else:
            await ctx.send(embed=config.syntax)
            return
        
        # Builds the top 10 list
        while i <= 9:
            leaderboard = leaderboard + "**" + output[0][i] + "**\n" + str(output[1][i]) + " messages  |  Rank: #" + str(i + 1) + "\n\n"
            i += 1
        
        # Builds final embed
        embed=discord.Embed(title="Server Leaderboard:", description=leaderboard, color=config.reportColor)
        if config.debug == True:
            embed.set_footer(text="You are ranked #" + str(output[2]) + " overall.  |  Executed in " + str(output[3]) + " seconds.")
        else:
            embed.set_footer(text="You are ranked #" + str(output[2]) + " overall.")
        
        # Sends results
        await ctx.send(embed=embed)

    ## Display User Message Count
    @commands.command(name='profile', aliases=['yì'])
    async def profile(self, ctx, user: discord.Member, *setting):
        preference = ''.join(setting).lower()
        variant = "messages"
        
        # Function for building the final profile output
        async def buildEmbed(user, language_pref, to_next_level, active_roles):
            # Checks if the user has a nickname
            try:
                nickname = " AKA \"" + user.nick + "\""
            except:
                nickname = ""
                
            # Checks if the user has 'unspecified'
            if type(admin.readDirectory(user, "pronouns")) == int:
                pronoun_role = get(user.guild.roles, id=admin.readDirectory(user, "pronouns")).name
            else:
                pronoun_role = admin.readDirectory(user, "pronouns")
                
            # Builds the embed
            embed=discord.Embed(color=get(user.guild.roles, id=active_roles["id"]).color, title=user.name + nickname)
            embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["join_date"], value=user.joined_at.strftime("%d/%m/%y, %H:%M"), inline=True)
            embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["language"], value=language_pref, inline=True)
            embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["pronouns"], value=pronoun_role, inline=True)
            embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["current_rank"], value=get(user.guild.roles, id=active_roles["id"]).mention + ", \"" + active_roles["translation"] + "\"")
            embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["message_count"], value=to_next_level, inline=False)
            embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["server_leaderboard"], value=await self.buildLeaderboard(ctx, user.id, variant, "position"))
            embed.add_field(name=config.text_file[language_pref]["profile"]["embed"]["times_thanked"], value=admin.readDirectory(user, "thanks"))
            embed.set_footer(text=config.text_file[language_pref]["profile"]["embed"]["footer"])
            embed.set_thumbnail(url=user.avatar_url) 
            
            return embed
        
        # Time start
        t1 = time.time()
        
        # Pulls necessary information from the user profile
        message_count = admin.readDirectory(user, "message count")
        language_pref = admin.readDirectory(user, "language")
        active_roles = admin.readDirectory(user, "rank")
        
        # Retrieves the current and next rank from Discord
        current_rank = get(ctx.guild.roles, id=active_roles["id"])
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
        
        # Time stop
        t2 = time.time()
        
        # Calculates execution time
        tDelta = round(t2 - t1, 3)
        
        # Checks debug state and sends final embed.
        if config.debug == True:
            embed.set_footer(text="Executed in " + str(tDelta) + " seconds.")
        await ctx.send(embed=embed)

    # Error Handling for !profile
    @profile.error
    async def profile_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(embed=config.syntax)

def setup(bot):
    bot.add_cog(Server(bot))
    print('Added new Cog: ' + str(Server))