import discord
from discord.ext import commands
import bot
import config
import admin

class TNP(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    ## Accepts a submitted request for a teacher
    @commands.command(name='accept')
    async def accept(self, ctx, user_id):
        teacher = ctx.message.author
        student = ctx.guild.get_member(int(user_id))
        
        # Retrieves the necessary profiles
        student_profile = admin.readDirectory(student)
        teacher_profile = admin.readDirectory(teacher)
        
        # Checks for a registration message from the student
        if type(student_profile['tnp']['registration']) == int:
            reg_id = student_profile['tnp']['registration']
            student_profile['tnp']['accepted_by'] = user.id
            
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
        embed = discord.Embed(title="The Neytiri Project", description="Accepted your registration! Check your DMs for more the next steps.")
        
        await ctx.send(embed=embed)

    ## Requests a teacher for The Neytiri Project
    @commands.command(name='register')
    async def register(self, ctx):
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



def setup(bot):
    bot.add_cog(TNP(bot))
    print('Added new Cog: ' + str(TNP))