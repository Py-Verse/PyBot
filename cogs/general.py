import asyncio

import discord
import requests
from discord.ext import commands
from discord.ext.commands import BucketType, cooldown


def to_emoji(c):
    base = 0x1F1E6
    return chr(base + c)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("General cog loaded successfully")

    @commands.command(cooldown_after_parsing=True, description="Suggest Us :) ")
    @cooldown(1, 7200, BucketType.user)
    async def suggest(self, ctx, *, msg):
        """
        Suggest us what changes you need in server or bot
        """
        channel_only = self.bot.get_channel(813688116552007700)
        up = "<:yes:820156388130160670>"
        down = "<:no:820156423509114900>"

        embed = discord.Embed(
            timestamp=ctx.message.created_at, title=f"Suggestion By {ctx.author}"
        )
        embed.add_field(name="Suggestion", value=msg)
        embed.set_footer(
            text=f"Wait until your suggestion is approved",
            icon_url=f"{ctx.author.avatar_url}",
        )
        message = await channel_only.send(embed=embed)
        await message.add_reaction(up)
        await message.add_reaction(down)
        await ctx.message.delete()
        await ctx.send("**Your Suggestion Has Been Recorded**")

    @commands.command(hidden=True, description="Creates a poll")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def poll(self, ctx, *, question):
        """Interactively creates a poll with the following question.
        To vote, use reactions!
        """

        # a list of messages to delete when we're all done
        messages = [ctx.message]
        answers = []

        def check(m):
            return (
                m.author == ctx.author
                and m.channel == ctx.channel
                and len(m.content) <= 100
            )

        for i in range(20):
            messages.append(
                await ctx.send(f"Say poll option or cancel to publish poll.")
            )

            try:
                entry = await self.bot.wait_for("message", check=check, timeout=60.0)
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith(f"cancel"):
                break

            answers.append((to_emoji(i), entry.clean_content))

        try:
            await ctx.channel.delete_messages(messages)
        except:
            pass  # oh well
        answer = "\n".join(f"{keycap}: {content}" for keycap, content in answers)
        e = discord.Embed(title=f"{ctx.author.name} asks: {question}", color=0x7289DA)
        e.add_field(name="\u200b", value=f"{answer}")
        actual_poll = await ctx.send(embed=e)
        for emoji, _ in answers:
            await actual_poll.add_reaction(emoji)

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Missing the question.")


def setup(bot):
    bot.add_cog(General(bot))
