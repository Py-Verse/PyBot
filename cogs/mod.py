import asyncio
import os

import discord
from discord.ext import commands


class Moderation(commands.Cog):
    """
    Moderation commands of DevBot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Mod Cog Loaded Successfully")

    @commands.command(description="Bans a member")
    @commands.has_permissions(ban_members=True)
    async def ban(
        self, ctx, member: discord.Member, *, reason=None, delete_message_days=7
    ):
        """
        Ban - Bans a member
        """
        guild = ctx.guild
        if member == self.bot.user:

            await ctx.reply("**Invalid**")

        elif guild.me.top_role < member.top_role:
            await ctx.reply("**Member is higher than me in hierarchy**")
        elif member == ctx.author:
            await ctx.reply("**You cannot ban yourself**")
        else:

            await member.ban(reason=reason)
            embed = discord.Embed(
                title="Ban",
                description=f"{member.name} has been banned by {ctx.author.name}",
                color=0xFF000,
            )
            await ctx.reply(embed=embed)

    @commands.command(description="Unbans a member")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, id: int):
        """
        Unban - Unbans a banned member
        """
        user = await self.bot.fetch_user(id)
        await ctx.guild.unban(user)
        embed = discord.Embed(
            title="Unban",
            description=f"{id} has been unbanned by {ctx.author.name}",
            color=0xFF000,
        )
        await ctx.reply(embed=embed)

    @commands.command(
        aliases=["del", "purge"], description="Deletes the given amount of messages"
    )
    @commands.has_permissions(manage_channels=True)
    async def clear(self, ctx, amount=4):
        """
        Clear - Cleart the given amount of messages
        """
        if amount > 200:
            await ctx.send("**Not more than 200**")
        else:
            await ctx.channel.purge(limit=amount + 1)
            msg = await ctx.send(f"**Purged {amount} messages**")
            await asyncio.sleep(2)
            await msg.delete()

    @commands.command(description="Kicks a member")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        Kick - Kicks a member
        """
        guild = ctx.guild
        if member == self.bot.user:
            await ctx.send("**Invalid**")
        elif guild.me.top_role < member.top_role:
            await ctx.send("**Member is higher than me in hierarchy**")
        elif member == ctx.author:
            await ctx.send("**You cannot kick yourself**")
        else:

            if member.top_role < ctx.author.top_role:
                await member.kick(reason=reason)
                embed = discord.Embed(
                    title="Kick",
                    description=f"{member.name} has been kicked by {ctx.author.name}",
                    color=0xFF000,
                )
                await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
