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
import admin

## -- Functions

## -- On Join
async def onJoin(member, kelutralBot):
    channel = kelutralBot.get_channel(config.modLog)
    roles = member.guild.roles
    
    embed=discord.Embed(color=config.successColor)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_author(name="Member Joined",icon_url=member.avatar_url)
    embed.add_field(name="New Member:", value=str(member.mention) + " " + str(member), inline=False)
    embed.set_footer(text="ID: " + str(member.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
    await channel.send(embed=embed)
    
    # Checks the Blacklist for Blacklisted IDs
    fileName = 'files/blacklist.txt'
    with open(fileName, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()

    setLines = set(lines)
    
    if str(member.id) in setLines:
        now = datetime.strftime(datetime.now(),'%H:%M')
        print(now + " -- Found this user in the blacklist.")
        if member.dm_channel is None:
               await member.create_dm()
        await member.send("Sorry, you are forbidden from joining Kelutral.org.")
        await member.ban()
        now = datetime.strftime(datetime.now(),'%H:%M')
        print(now + " -- " + member.name + " was banned.")
        
        target = member.guild.get_member(config.makoID)
        await target.send(member.name + " attempted to join Kelutral.org.")
        
        return
        
    # This will automatically give anyone the 'frapo' role when they join the server.
    
    frapoRole = get(member.guild.roles, name="frapo")
    await member.add_roles(frapoRole)
    now = datetime.strftime(datetime.now(),'%H:%M')
    print(now + " -- Gave " + member.name + " the role " + frapoRole.name + ".")
    
    # This will add the join to the count of joins for that day
    today = datetime.now().strftime('%m-%d-%Y')
    fileName = 'files/logs/join_data/' + today + '.tsk'
    if not os.path.exists(fileName):
        with open(fileName, 'w', encoding='utf-8') as fh:
            fh.write('1')
    else:
        with open(fileName, 'r', encoding='utf-8') as fh:
            total = fh.read()
        
        total = int(total) + 1
        with open(fileName, 'w', encoding='utf-8') as fh:
            fh.write(str(total))
    
    try:
        if member.dm_channel is None:
            await member.create_dm()

        embed=discord.Embed()
        embed=discord.Embed(title="Welcome to the Kelutral.org Discord Server!", colour=config.welcomeColor)
        embed.add_field(name="**Fwa ngal fìtsengit sunu ayoer!**", value="We are glad that you are here!\n\nWhen you get the chance, please read our rules and information channels to familiarize yourself with our code of conduct and roles. After that, please introduce yourself in #kaltxì so that a moderator can assign you the proper role.\n\nIf you would like to personally assign your own pronouns, you can react to this message with \U00002640, \U00002642 or \U0001F308. Please be careful when making your selection, as changes can't be made without contacting a moderator.\n\n**Zola'u nìprrte' ulte siva ko!** Welcome, let's go!", inline=False)

        message = await member.send(embed=embed)
        emojis = ['\U00002642','\U00002640','\U0001F308']
        pronounRole = ['He/Him','She/Her','They/Them']
        for emoji in emojis:
            await message.add_reaction(emoji)
        
        def check(reaction, user):
            for emoji in emojis:
                if str(reaction.emoji) == emoji:
                    foundEmoji = True
                    break
                else:
                    foundEmoji = False
            return user == member and foundEmoji

        try:
            reaction, user = await kelutralBot.wait_for('reaction_add', timeout=180.0, check=check)
        except asyncio.TimeoutError:
            await member.send("Window has passed to self-assign pronouns. Please DM a mod if you would still like to do so.")
            target = member.guild.get_member(config.botID)
            for emoji in emojis:
                await message.remove_reaction(emoji, target)
            pronounChoice = "Unspecified"
        else:
            i = 0
            while i < 3:
                if str(reaction) == emojis[i]:
                    pronounChoice = get(member.guild.roles, name=pronounRole[i])
                    await member.add_roles(pronounChoice)
                    now = datetime.strftime(datetime.now(),'%H:%M')
                    print(now + " -- Assigned " + member.name + " " + pronounRole[i] + " pronouns.")
                    break
                else:
                    i += 1
            # This creates a profile for new joins.
            if type(pronounChoice) == str:
                pronouns = pronounChoice
            elif type(pronounChoice) == object:
                pronouns = pronounChoice.id
            
            profile = admin.getProfile(member)
            
            if profile != None:
                print(now + " -- This user already has an existing profile. Skipping generation of a new profile.")
            else:
                #          [member id, msg count, member name, default language, pronoun role id, frapo role id, translation, thanks count]
                new_user_profile = [member.id, 0, member.name, "English", pronouns, [config.frapoID, "Everyone"], 0]
                config.directory.append(new_user_profile)
                print(now + " -- Created a new profile for " + member.name)
    except:
        now = datetime.strftime(datetime.now(),'%H:%M')
        print(now + " -- Cannot DM this user.")
        
    with open(config.directoryFile, 'w', encoding='utf-8') as fh:
        json.dump(config.directory, fh)
    
    config.directory = config.reloadDir()
            
## -- On Leave
async def onLeave(member, kelutralBot):
    channel = kelutralBot.get_channel(config.modLog)
    
    embed=discord.Embed(color=config.failColor)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_author(name="Member Left",icon_url=member.avatar_url)
    embed.add_field(name="Member:", value=str(member.mention) + " " + str(member), inline=False)
    embed.set_footer(text="ID: " + str(member.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
    await channel.send(embed=embed)
    
    # This will add the departure to the count of departures for that day
    today = datetime.now().strftime('%m-%d-%Y')
    checkJoin = member.joined_at.strftime('%m-%d-%Y')
    
    now = datetime.strftime(datetime.now(),'%H:%M')
    print(now + " -- " + member.name + " left the server.")    
    if checkJoin == today:
        fileName = 'files/logs/rds/' + today + '.tsk'
        if not os.path.exists(fileName):
            with open(fileName, 'w', encoding='utf-8') as fh:
                fh.write('1')
        else:
            with open(fileName, 'r', encoding='utf-8') as fh:
                total = fh.read()
            total = int(total) + 1
            with open(fileName, 'w', encoding='utf-8') as fh:
                fh.write(str(total))
    
    fileName = 'files/logs/leave_data/' + today + '.tsk'
    if not os.path.exists(fileName):
        with open(fileName, 'w', encoding='utf-8') as fh:
            fh.write('1')
    else:
        with open(fileName, 'r', encoding='utf-8') as fh:
            total = fh.read()
        total = int(total) + 1        
        with open(fileName, 'w', encoding='utf-8') as fh:
            fh.write(str(total))

## -- On Message Delete
async def onDelete(message, kelutralBot):
    member = message.author
    channel = kelutralBot.get_channel(config.modLog)
    
    if message.author.top_role.id != config.botRoleID:  
        embed=discord.Embed(color=config.failColor)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=str(member),icon_url=member.avatar_url)
        embed.add_field(name="Message Deleted", value="**Message sent by " + str(member.mention) + " deleted in " + str(message.channel.mention) + "**\n" + str(message.content), inline=False)
        embed.set_footer(text="ID: " + str(message.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
        await channel.send(embed=embed)
    
## -- On Member Update
async def onUpdate(before, after, kelutralBot):
    channel = kelutralBot.get_channel(config.modLog)
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
        embed.add_field(name="Member Updated", value=str(after.mention) + "** was removed from `" + ' '.join(nameList) + '`**', inline=False)
        embed.set_footer(text="ID: " + str(after.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
        
        await channel.send(embed=embed)
    elif len(addedRoles) > 0:
        for role in addedRoles:
            nameList.append(addedRoles[i].name)
            i += 1
        embed=discord.Embed(color=config.reportColor)
        embed.set_thumbnail(url=after.avatar_url)
        embed.set_author(name=str(after),icon_url=after.avatar_url)
        embed.add_field(name="Member Updated", value=str(after.mention) + "** was added to `" + ' '.join(nameList) + '`**', inline=False)
        embed.set_footer(text="ID: " + str(after.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
        
        await channel.send(embed=embed)
        
    beforeName = before.display_name
    afterName = after.display_name
        
    if beforeName != afterName:
        embed=discord.Embed(color=config.reportColor)
        embed.set_thumbnail(url=after.avatar_url)
        embed.set_author(name=str(after),icon_url=after.avatar_url)
        embed.add_field(name="Member Updated", value='`' + str(beforeName) + '`** changed their name to `' + str(afterName) + '`**', inline=False)
        embed.set_footer(text="ID: " + str(after.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
        
        await channel.send(embed=embed)

## -- On Member Ban
async def onBan(guild, user, kelutralBot):
    channel = kelutralBot.get_channel(config.modLog)

    embed=discord.Embed(color=config.failColor)
    embed.set_thumbnail(url=user.avatar_url)
    embed.set_author(name=str(user),icon_url=user.avatar_url)
    embed.add_field(name="Member Banned", value=str(user.mention) + '** was banned**', inline=False)
    embed.set_footer(text="ID: " + str(user.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
    
    await channel.send(embed=embed)
    
## -- On Member Unban
async def onUnban(guild, user, kelutralBot):

    channel = kelutralBot.get_channel(config.modLog)

    embed=discord.Embed(color=config.reportColor)
    embed.set_thumbnail(url=user.avatar_url)
    embed.set_author(name=str(user),icon_url=user.avatar_url)
    embed.add_field(name="Member Banned", value=str(user.mention) + '** was unbanned**', inline=False)
    embed.set_footer(text="ID: " + str(user.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
    
    await channel.send(embed=embed)

## -- On Member Message
async def onMessage(message, kelutralBot):
    user = message.author
    now = datetime.strftime(datetime.now(),'%H:%M')
    print(now + " - Analyzing message from " + str(user))
    
    # If message is in-server
    if message.guild:
        # If message is not a command.
        if not message.content.startswith("!") and not message.content.startswith("?"):
            # If message is in guild and isn't from the bot.
            if len(message.content) >= 5 and message.author.top_role.id != config.botRoleID:
                for entry in config.directory:
                    if entry[0] == user.id:
                        entry[1] += 1
                        break
                        
                await admin.roleUpdate(user)
                
                with open(config.directoryFile, 'w', encoding='utf-8') as fh:
                    json.dump(config.directory, fh)
                    
                config.directory = config.reloadDir()
