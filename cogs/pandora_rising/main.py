import discord
from discord.ext import commands
from discord.utils import get

import config

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emojis = ['<:rdaloyalty:778834136643272724>', '<:nvloyalty:778834136450203708>']
        rank_roles = {'778834136643272724': 783061138296012801, '778834136450203708': 783061180259500065}
        rankAssigned = False
        
        if payload.guild_id == config.PRID:
            emoji = payload.emoji
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            
            if member.id != config.botID:
                set_ranks = set(rank_roles.values())
                for role in member.roles:
                    if role.id in set_ranks:
                        rankAssigned = True
                        current_rank_id = role.id
                        
                if str(emoji) in emojis:
                    role_id = rank_roles[str(emoji.id)]
                    message = await guild.get_channel(783053871606005801).fetch_message(payload.message_id)
                    
                    if rankAssigned:
                        await member.remove_roles(get(guild.roles, id=current_rank_id))
                    await member.add_roles(get(guild.roles, id=role_id))
                    await message.remove_reaction(emoji, member)

    @commands.command(name="rolemsg")
    async def sendRolemsg(self, ctx):
        emojis = ['<:rdaloyalty:778834136643272724>', '<:nvloyalty:778834136450203708>']
        rank_roles = {'778834136643272724': 783061138296012801, '778834136450203708': 783061180259500065}
        
        embed = discord.Embed(title="Rank Assignment", description="React to this message to assign your primary Faction in-game. This is purely cosmetic and serves no other use than determining your chat color.\n\n{} : {}\n{} : {}".format('<:rdaloyalty:778834136643272724>', get(ctx.guild.roles, id=783061138296012801).mention, '<:nvloyalty:778834136450203708>', get(ctx.guild.roles, id=783061180259500065).mention), color=0xf9f9f4)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        message = await ctx.send(embed=embed)
        
        for emoji in emojis:
            await message.add_reaction(emoji)
            

def setup(bot):
    bot.add_cog(Utility(bot))
    print('Initialzed Pandora Rising command set.')