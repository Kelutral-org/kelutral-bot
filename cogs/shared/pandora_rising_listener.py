# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import random

from datetime import datetime

import asyncio
import os
import glob
import json

import config
import pr_admin

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    ## -- On Join
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 748700165266866227:
            channel = self.bot.get_channel(config.pr_modLog)
            roles = member.guild.roles
            now = datetime.strftime(datetime.now(),'%H:%M')
            
            embed=discord.Embed(color=config.successColor)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name="Member Joined",icon_url=member.avatar_url)
            embed.add_field(name="New Member:", value=str(member.mention) + " " + str(member), inline=False)
            embed.set_footer(text="ID: {} • Today at {}".format(member.id, datetime.now().strftime('%H:%M EST')))
            await channel.send(embed=embed)
            
            # Checks the Blacklist for Blacklisted IDs
            fileName = 'files/blacklist.txt'
            with open(fileName, 'r', encoding='utf-8') as fh:
                lines = fh.readlines()

            setLines = set(lines)
            
            if str(member.id) in setLines:
                print(now + " -- Found this user in the blacklist.")
                if member.dm_channel is None:
                       await member.create_dm()
                await member.send("Sorry, you are forbidden from joining Kelutral.org.")
                await member.ban()
                print(now + " -- " + member.name + " was banned.")
                
                target = member.guild.get_member(config.makoID)
                await target.send("{} attempted to join Kelutral.org.".format(member.name))
                
                return
            
            print(now + " -- {} joined the server.".format(member.name))
            # This will automatically give anyone the 'frapo' role when they join the server.
            
            frapoRole = get(member.guild.roles, name="frapo")
            await member.add_roles(frapoRole)

            print(now + " -- Gave {} the role {}.".format(member.name, frapoRole.name))
            
            with open('cogs/shared/files/pandora_rising/server_info.json', 'r', encoding='utf-8') as fh:
                server_info = json.load(fh)
            
            date = datetime.now().strftime("%m-%d-%Y")
            try:
                today_dict = server_info[date]
                today_dict['joins'] += 1
            except KeyError:
                server_info[date] = {
                    "joins" : 1,
                    "leaves" : 0,
                    "rds" : 0
                    }
            
            with open('cogs/shared/files/pandora_rising/server_info.json', 'w', encoding='utf-8') as fh:
                json.dump(server_info, fh)
            
            try:
                emojis = ['\U00002642','\U00002640','\U0001F3F3\U0000fe0f\U0000200d\U0001f308','\U0000267E']
                if member.dm_channel is None:
                    await member.create_dm()
                embed=discord.Embed()
                embed=discord.Embed(title="Welcome to Kelutral.org's Pandora Rising Discord Server!", colour=config.welcomeColor)
                embed.add_field(name="**We're glad that you're here!**", value="When you get the chance, please read our rules and information channels to familiarize yourself with our code of conduct and roles.\n\nIf you would like to personally assign your own pronouns, you can react to this message with {}, {}, {} or {} (He/Him, She/Her, They/Them or Any Pronouns).".format(emojis[0],emojis[1],emojis[2],emojis[3]), inline=False)

                message = await member.send(embed=embed)
                
                kt_pronounRoleDict = {"716012802933784726": "He/Him", "716012837851627530": "She/Her", "716012861515890741": "They/Them","769540306843729951": "Any Pronouns"}
                for emoji in emojis:
                    await message.add_reaction(emoji)
            except:
                now = datetime.strftime(datetime.now(),'%H:%M')
                print(now + " -- Cannot DM this user.")
                pronounChoice = "Unspecified"
                
            # This creates a profile for new joins.
            pronouns = "Unspecified"
            profile = pr_admin.readDirectory(member)
            
            if profile != None:
                print(now + " -- This user already has an existing Kelutral profile. Skipping generation of a new profile.")
                if type(profile['pronouns']) == int:
                    role_to_add = get(member.guild.roles, name=kt_pronounRoleDict[str(profile['pronouns'])])
                    await member.add_roles(role_to_add)
                    print(now + " -- {} previously had the pronouns {}. Assigning now.".format(member.name, role_to_add.name))
            else:
                config.directory[str(member.id)] = {
                                                    "id" : member.id,
                                                    "message count" : 0,
                                                    "name" : member.name,
                                                    "language" : "English",
                                                    "pronouns" : pronouns,
                                                    "rank" : {
                                                        "id" : config.frapoID,
                                                        "translation" : "Everyone"
                                                    },
                                                    "thanks" : 0,
                                                    "pr_rank" : {
                                                        "id" : config.prFrapo
                                                    }
                                                }
                print(now + " -- Created a new profile for {}.".format(member.name))
            pr_admin.updateDirectory()
        
    ## -- On Leave
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id == 748700165266866227:
            channel = self.bot.get_channel(config.pr_modLog)
            
            embed=discord.Embed(color=config.failColor)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name="Member Left",icon_url=member.avatar_url)
            embed.add_field(name="Member:", value=str(member.mention) + " " + str(member), inline=False)
            embed.set_footer(text="ID: {} • Today at {}".format(member.id, datetime.now().strftime('%H:%M EST')))
            await channel.send(embed=embed)
            
            # This will add the departure to the count of departures for that day
            today = datetime.now().strftime('%m-%d-%Y')
            checkJoin = member.joined_at.strftime('%m-%d-%Y')
            
            now = datetime.strftime(datetime.now(),'%H:%M')
            print(now + " -- " + member.name + " left the server.")   

            
            with open('cogs/shared/files/pandora_rising/server_info.json', 'r', encoding='utf-8') as fh:
                server_info = json.load(fh)
            
            if checkJoin == today:
                try:
                    today_dict = server_info[checkJoin]
                    today_dict['leaves'] += 1
                    today_dict['rds'] += 1
                except KeyError:
                    server_info[datetime.now().strftime('%H:%M')] = {
                        "joins" : 0,
                        "leaves" : 1,
                        "rds" : 1
                        }
            else:
                try:
                    today_dict = server_info[checkJoin]
                    today_dict['leaves'] += 1
                except KeyError:
                    server_info[datetime.now().strftime('%H:%M')] = {
                        "joins" : 0,
                        "leaves" : 1,
                        "rds" : 0
                        }
            
            with open('cogs/shared/files/pandora_rising/server_info.json', 'w', encoding='utf-8') as fh:
                json.dump(server_info, fh)

    ## -- On Message Delete
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild.id == 748700165266866227:
            member = message.author
            channel = self.bot.get_channel(config.pr_modLog)
            
            if message.author.top_role.id != config.botRoleID and message.channel.id != 748718468303683677:  
                embed=discord.Embed(color=config.failColor)
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_author(name=str(member),icon_url=member.avatar_url)
                embed.add_field(name="Message Deleted", value="**Message sent by " + str(member.mention) + " deleted in " + str(message.channel.mention) + "**\n" + str(message.content), inline=False)
                embed.set_footer(text="ID: {} • Today at {}".format(message.id, datetime.now().strftime('%H:%M EST')))
                await channel.send(embed=embed)
        
    ## -- On Member Update
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id == 748700165266866227:
            channel = self.bot.get_channel(config.pr_modLog)
            nameList = []
            i = 0
            
            listBeforeRoles = before.roles
            listAfterRoles = after.roles
            removedRoles = list(set(listBeforeRoles) - set(listAfterRoles))
            addedRoles = list(set(listAfterRoles) - set(listBeforeRoles))
            
            if len(removedRoles) > 0:
                for role in removedRoles:
                    nameList.append(removedRoles[i].name)
                    i += 1
                embed=discord.Embed(color=config.reportColor)
                embed.set_thumbnail(url=after.avatar_url)
                embed.set_author(name=str(after),icon_url=after.avatar_url)
                embed.add_field(name="Member Updated", value="{}** was removed from `{}`**".format(after.mention, ''.join(nameList)), inline=False)
                embed.set_footer(text="ID: {} • Today at {}".format(after.id, datetime.now().strftime('%H:%M EST')))
                
                await channel.send(embed=embed)
            elif len(addedRoles) > 0:
                for role in addedRoles:
                    nameList.append(addedRoles[i].name)
                    i += 1
                embed=discord.Embed(color=config.reportColor)
                embed.set_thumbnail(url=after.avatar_url)
                embed.set_author(name=str(after),icon_url=after.avatar_url)
                embed.add_field(name="Member Updated", value="{}** was added to `{}`**".format(after.mention, ''.join(nameList)), inline=False)
                embed.set_footer(text="ID: {} • Today at {}".format(after.id, datetime.now().strftime('%H:%M EST')))
                
                await channel.send(embed=embed)
                
            beforeName = before.display_name
            afterName = after.display_name
                
            if beforeName != afterName:
                embed=discord.Embed(color=config.reportColor)
                embed.set_thumbnail(url=after.avatar_url)
                embed.set_author(name=str(after),icon_url=after.avatar_url)
                embed.add_field(name="Member Updated", value='`{}`** changed their name to `{}`**'.format(beforeName, afterName), inline=False)
                embed.set_footer(text="ID: {} • Today at {}".format(after.id, datetime.now().strftime('%H:%M EST')))
                
                await channel.send(embed=embed)

    ## -- On Member Ban
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if guild.id == 748700165266866227:
            channel = self.bot.get_channel(config.pr_modLog)

            embed=discord.Embed(color=config.failColor)
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_author(name=str(user),icon_url=user.avatar_url)
            embed.add_field(name="Member Banned", value="{}** was banned.**".format(user.mention), inline=False)
            embed.set_footer(text="ID: {} • Today at {}".format(user.id, datetime.now().strftime('%H:%M EST')))
            
            await channel.send(embed=embed)
        
    ## -- On Member Unban
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if guild.id == 748700165266866227:
            channel = self.bot.get_channel(config.pr_modLog)

            embed=discord.Embed(color=config.reportColor)
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_author(name=str(user),icon_url=user.avatar_url)
            embed.add_field(name="Member Banned", value='{} ** was unbanned**'.format(str(user.mention)), inline=False)
            embed.set_footer(text="ID: {} • Today at {}".format(str(user.id), datetime.now().strftime('%H:%M EST')))
            
            await channel.send(embed=embed)

    ## -- On Member Message
    @commands.Cog.listener()
    async def on_message(self, message):
        user = message.author
        ctx = await self.bot.get_context(message)
        now = datetime.strftime(datetime.now(),'%H:%M')
        
        # If message is in Pandora Rising
        if message.guild and message.guild.id == 748700165266866227:
            # If message is not a command.
            if not message.content.startswith("!") and not message.content.startswith("?") and not message.content.startswith("%"):
                # If message is in guild and isn't from the bot.
                if len(message.content) >= 5 and user.id != 715296437335752714:
                    print(now + " - Analyzing message from {} in {} on {}.".format(user, message.channel.name, message.guild.name))
                    try:
                        pr_admin.writeDirectory(user, "message count", pr_admin.readDirectory(user, "message count") + 1)
                    except KeyError:
                        print(now + " -- WARNING: {} does not have a profile!".format(user.name))
                            
                    await pr_admin.roleUpdate(user)
                    pr_admin.updateDirectory()
                
                if message.author.id != config.botID and config.watch_keywords:
                    for keyword in config.watched_phrases:
                        if keyword in message.content.lower():
                            await self.bot.get_channel(config.pr_modLog).send("The following message requires review by an {}: {}".format(get(ctx.guild.roles, id=config.modID).mention, message.jump_url))
                
                if "eytukan" in message.content.lower():
                    await message.add_reaction("👀")
                    
                for user in message.mentions:
                    if config.botID == user.id:
                        responses = config.text_file[pr_admin.readDirectory(user, "language")]["responses"]
                        index = random.randint(0,len(responses)-1)
                        await ctx.send(responses[index])
                    
            elif message.content.startswith("!") and message.author.id == 723257649055006740:
                question = message.content.replace("!8ball ", "")
                
                options = config.text_file[pr_admin.readDirectory(user, "language")]["8ball"]["options"]
                index = random.randint(0, len(options) - 1)
                embed = discord.Embed(description=config.text_file[pr_admin.readDirectory(user, "language")]["8ball"]["response"].format(user.mention, question, config.text_file[pr_admin.readDirectory(user, "language")]["8ball"]["options"][index]))
                
                await ctx.send(embed=embed)

    ## -- On Reaction Add
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id == config.PRID:
            added_emoji = payload.emoji
            guild = self.bot.get_guild(748700165266866227)
            channel = await self.bot.fetch_channel(payload.channel_id)
            
            if payload.member == None:
                member = guild.get_member(payload.user_id)
            else:
                member = payload.member
                
            emoji = ['<:irayo:715054886714343455>','<:prirayo:782966273466171412>'] 
            fileName = 'files/config/reactions.txt'

            if isinstance(channel, discord.DMChannel):
                if member.id != config.botID:
                    emojis = ['♂️','♀️','🏳️‍🌈','♾️']
                    pronounRole = ['He/Him','She/Her','They/Them','Any Pronouns']
                    
                    if added_emoji.name in emojis:
                        profile = pr_admin.readDirectory(member)
                        pronouns = pr_admin.readDirectory(member, "pronouns")
                        now = datetime.strftime(datetime.now(),'%H:%M')
                        
                        index = emojis.index(added_emoji.name)
                        role_to_add = get(guild.roles, name=pronounRole[index])
                        
                        if pronouns == role_to_add.id:
                            await member.send("You already have that role!")
                            print(now + " -- {} attempted to add the {} pronouns, but they already had them.".format(member.name, role_to_add.name))
                        elif pronouns != "Unspecified":
                            old_role = get(guild.roles, id=profile['pronouns'])
                            await member.remove_roles(old_role)
                            await member.add_roles(role_to_add)
                            await member.send("Removed {} and added {}.".format(old_role.name, role_to_add.name))
                            print(now + " -- {} swapped from {} pronouns to {} ones.".format(member.name, old_role.name, role_to_add.name))
                        else:
                            await member.add_roles(role_to_add)
                            await member.send("Successfully added you to {}.".format(role_to_add.name))
                            print(now + " -- {} was given the {} pronouns.".format(member.name, role_to_add.name))
                        
                        pr_admin.writeDirectory(member, 'pronouns', role_to_add.id)
                        return
            
            # If reaction was added by the message author (sneaky sneaky!)
            message = await channel.fetch_message(payload.message_id)
            if message.author.id == payload.user_id:
                return
            else:
                with open(fileName, 'r') as fh:
                    contents = json.load(fh)
                
                # Checks to see if the reaction adder has already added a reaction to that message (prevents duplication)
                if str(added_emoji) in emoji: 
                    check = [message.id, payload.user_id]
                    if check not in contents:
                        contents.append([message.id, payload.user_id])
                        timesThanked = pr_admin.readDirectory(message.author, "thanks")
                        
                        timesThanked += 1
                        
                        # Updates the reactions log
                        with open(fileName, 'w') as fh:
                            json.dump(contents, fh)
                
                    pr_admin.writeDirectory(message.author, "thanks", timesThanked)
                pr_admin.updateDirectory()
            
def setup(bot):
    bot.add_cog(Utility(bot))
    print('Added Pandora Rising listener: ' + str(Utility))