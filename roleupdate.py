import discord
from discord.ext import commands
import re
import bot
import admin

# Replace RandomCog with something that describes the cog.  E.G. SearchCog for a search engine, sl.
class LoyaltyCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    # commands have this format instead.  For any variables from the main file, use bot.variable.
    @commands.Cog.listener()
    async def roleUpdate(self,count, check, message, user):
        i = 0
        activeRoles = message.guild.roles
        langCheck = admin.outputCheck(message.author)
        for roles in bot.activeRoleNames:
            if count >= bot.activeRoleThresholds[i] and check.name != roles:
                newRole = bot.get(activeRoles, name=bot.activeRoleNames[i])
                await user.add_roles(newRole)
                print('Tìmìng txintìnit alu ' + newRole.name + ' tuteru alu ' + user.display_name + '.')
                if message.author.dm_channel is None:
                    await message.author.create_dm()

                if langCheck == "English":
                    embed = discord.Embed()
                    embed = discord.Embed(colour=0x1e3626)
                    embed.add_field(name="New Rank Achieved on Kelutral.org",
                                    value="**Congratulations!** You're now a " + newRole.name + ".", inline=False)
                    # embed.set_thumbnail(ctx.guild.icon_url)

                elif langCheck == "Na'vi":
                    embed = discord.Embed()
                    embed = discord.Embed(colour=0x1e3626)
                    embed.add_field(name="Mipa txìntin lu ngaru mì Helutral.org",
                                    value="**Seykxel si nitram!** Nga slolu " + newRole.name + ".", inline=False)
                    # embed.set_thumbnail(ctx.guild.icon_url)

                await message.author.send(embed=embed)

                if check.name != "@everyone":
                    await user.remove_roles(check)
                    print("'olaku txintìnit alu " + check.name + " ta " + user.display_name + ".")
                break
            elif count >= bot.activeRoleThresholds[i]:
                break
            i += 1


def setup(bot):
    bot.add_cog(LoyaltyCog(bot))