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

import admin

## -- Variables
ignoredRoles = ["Olo'eyktan (Admin)","Eyktan (Moderator)","Karyu (Teacher)","Numeyu (Learner)","'Eylan (Friend)","Tìkanu Atsleng (Bot)","He/Him","She/Her","They/Them","frapo"]

## -- Functions

## -- On Join
async def onJoin(member, kelutralBot):
    message_channel = 715052686487191583
    channel = kelutralBot.get_channel(message_channel)
    
    embed=discord.Embed(color=0x07ca48)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_author(name="Member Joined",icon_url=member.avatar_url)
    embed.add_field(name="New Member:", value=str(member.mention) + " " + str(member), inline=False)
    embed.set_footer(text="ID: " + str(member.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
    await channel.send(embed=embed)
    
    # Checks the Blacklist for Blacklisted IDs
    fileName = 'files/blacklist.txt'
    count = 0
    i = 0
    fh = open(fileName, 'r', encoding='utf-8')
    lines = fh.readlines()
    count = len(lines)
    while i < count:
        line = ''.join(lines[i])
        line.strip()
        if int(lines[i]) == member.id:
            now = datetime.strftime(datetime.now(),'%H:%M')
            print(now + " -- Found this user in the blacklist.")
            if member.dm_channel is None:
                   await member.create_dm()
            await member.send("Sorry, you are forbidden from joining Kelutral.org.")
            await member.ban()
            now = datetime.strftime(datetime.now(),'%H:%M')
            print(now + " -- " + member.name + " was banned.")
            
            target = member.guild.get_member(81105065955303424)
            await target.send(member.name + " attempted to join Kelutral.org.")

            break
        i += 1
    fh.close()
    
    # This will automatically give anyone the 'frapo' role when they join the server.
    
    newRole = get(member.guild.roles, name="frapo")
    await member.add_roles(newRole)
    now = datetime.strftime(datetime.now(),'%H:%M')
    print(now + " -- Gave " + member.name + " the role " + newRole.name + ".")
    
    # This will add the join to the count of joins for that day
    today = datetime.now().strftime('%m-%d-%Y')
    fileName = 'files/logs/join_data/' + today + '.tsk'
    if not os.path.exists(fileName):
        fh = open(fileName, 'w', encoding='utf-8')
        fh.write('1')
        fh.close()
    else:
        fh = open(fileName, 'r', encoding='utf-8')
        total = fh.read()
        fh.close()
        
        fh = open(fileName, 'w', encoding='utf-8')
        total = int(total) + 1
        fh.write(str(total))
        fh.close()
    
    try:
        if member.dm_channel is None:
            await member.create_dm()

        embed=discord.Embed()
        embed=discord.Embed(title="Welcome to the Kelutral.org Discord Server!", colour=0x6D326D)
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
            target = member.guild.get_member(715296437335752714)
            for emoji in emojis:
                await message.remove_reaction(emoji, target)
        else:
            i = 0
            while i < 3:
                if str(reaction) == emojis[i]:
                    newRole = get(member.guild.roles, name=pronounRole[i])
                    await member.add_roles(newRole)
                    now = datetime.strftime(datetime.now(),'%H:%M')
                    print(now + " -- Assigned " + member.name + " " + pronounRole[i] + " pronouns.")
                    break
                else:
                    i += 1
    except:
        now = datetime.strftime(datetime.now(),'%H:%M')
        print(now + " -- Cannot DM this user.")
                
## -- On Leave
async def onLeave(member, kelutralBot):
    message_channel = 715052686487191583
    channel = kelutralBot.get_channel(message_channel)
    
    embed=discord.Embed(color=0xe93535)
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
            fh = open(fileName, 'w', encoding='utf-8')
            fh.write('1')
            fh.close()
        else:
            fh = open(fileName, 'r', encoding='utf-8')
            total = fh.read()
            fh.close()
            
            fh = open(fileName, 'w', encoding='utf-8')
            total = int(total) + 1
            fh.write(str(total))
            fh.close()
    
    fileName = 'files/logs/leave_data/' + today + '.tsk'
    if not os.path.exists(fileName):
        fh = open(fileName, 'w', encoding='utf-8')
        fh.write('1')
        fh.close()
    else:
        fh = open(fileName, 'r', encoding='utf-8')
        total = fh.read()
        fh.close()
        
        fh = open(fileName, 'w', encoding='utf-8')
        total = int(total) + 1
        fh.write(str(total))
        fh.close()
    
    if member.dm_channel is None:
        await member.create_dm()

## -- On Message Delete
async def onDelete(message, kelutralBot):
    member = message.author
    message_channel = 715052686487191583
    channel = kelutralBot.get_channel(message_channel)
    
    embed=discord.Embed(color=0xe93535)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_author(name=str(member),icon_url=member.avatar_url)
    embed.add_field(name="Message Deleted", value="**Message sent by " + str(member.mention) + " deleted in " + str(message.channel.mention) + "**\n" + str(message.content), inline=False)
    embed.set_footer(text="ID: " + str(message.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
    await channel.send(embed=embed)
    
## -- On Member Update
async def onUpdate(before, after, kelutralBot):
    message_channel = 715052686487191583
    channel = kelutralBot.get_channel(message_channel)
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
        embed=discord.Embed(color=0x5da9e9)
        embed.set_thumbnail(url=after.avatar_url)
        embed.set_author(name=str(after),icon_url=after.avatar_url)
        embed.add_field(name="Member Updated", value=str(after.mention) + "** was removed from `" + ' '.join(nameList) + '`**', inline=False)
        embed.set_footer(text="ID: " + str(after.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
        
        await channel.send(embed=embed)
    elif len(addedRoles) > 0:
        for role in addedRoles:
            nameList.append(addedRoles[i].name)
            i += 1
        embed=discord.Embed(color=0x5da9e9)
        embed.set_thumbnail(url=after.avatar_url)
        embed.set_author(name=str(after),icon_url=after.avatar_url)
        embed.add_field(name="Member Updated", value=str(after.mention) + "** was added to `" + ' '.join(nameList) + '`**', inline=False)
        embed.set_footer(text="ID: " + str(after.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
        
        await channel.send(embed=embed)
        
    beforeName = before.display_name
    afterName = after.display_name
        
    if beforeName != afterName:
        embed=discord.Embed(color=0x5da9e9)
        embed.set_thumbnail(url=after.avatar_url)
        embed.set_author(name=str(after),icon_url=after.avatar_url)
        embed.add_field(name="Member Updated", value='`' + str(beforeName) + '`** changed their name to `' + str(afterName) + '`**', inline=False)
        embed.set_footer(text="ID: " + str(after.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
        
        await channel.send(embed=embed)

## -- On Member Ban
async def onBan(guild, user, kelutralBot):
    message_channel = 715052686487191583
    channel = kelutralBot.get_channel(message_channel)

    embed=discord.Embed(color=0xe93535)
    embed.set_thumbnail(url=user.avatar_url)
    embed.set_author(name=str(user),icon_url=user.avatar_url)
    embed.add_field(name="Member Banned", value=str(user.mention) + '** was banned**', inline=False)
    embed.set_footer(text="ID: " + str(user.id) + " • Today at " + datetime.now().strftime('%H:%M EST'))
    
    await channel.send(embed=embed)
    
## -- On Member Unban
async def onUnban(guild, user, kelutralBot):
    message_channel = 715052686487191583
    channel = kelutralBot.get_channel(message_channel)

    embed=discord.Embed(color=0x5da9e9)
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
        if not message.content.startswith("!"):
            # If message is in guild and isn't from the bot.
            if len(message.content) >= 5 and message.author.top_role.id != 715094486992027699:
                currentRole = user.top_role
                userRoles = user.roles
                isMod = False
                userMessageCount = 0
                fileName = 'files/users/' + str(user.id) + '.tsk'
                
                ## Check if author.top_role is moderator.
                if currentRole.name in ignoredRoles:
                    isMod = True

                ## Assigns correct role to currentRole if mod.
                if isMod:
                    for role in userRoles:
                        if role.name not in ignoredRoles:
                            currentRole = role

                ## Updates the user profile.
                if not os.path.exists(fileName):
                    fh = open(fileName, 'w', encoding='utf-8')
                    fh.write(str(userMessageCount + 1) + "\n")
                    fh.write(user.name + "\n")
                    fh.write("English")
                    fh.close()
                    content = str(userMessageCount + 1)
                else:
                    content = admin.checkProfile(user, "Messages", "User Name", "Language Preference")

                    fh = open(fileName, "w", encoding='utf-8')
                    fh.write(str(int(content[0]) + 1) + "\n")
                    fh.write(content[1] + "\n")
                    fh.write(content[2])
                    fh.close()
                        
                await admin.roleUpdate(int(content[0]) + 1, currentRole, message, user)
