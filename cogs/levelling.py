import discord
from discord.ext import commands
from discord.ext.commands import (
    BadArgument,
    BucketType,
    Cog,
    Context,
    clean_content,
    command,
    cooldown,
    has_any_role,
)


class Level(commands.Cog):
    """
    Levelling system for PyBot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Level cog loaded successfully")

    """
    Soon...
    """


def setup(bot):
    bot.add_cog(Level(bot))
