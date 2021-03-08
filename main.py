import os
from datetime import datetime

import discord
from discord.ext import commands
from pretty_help import PrettyHelp

start_time = datetime.utcnow()


description = """
PyBot - A Bot for PyBot
"""
bot = commands.Bot(
    command_prefix=["!", ">", "."],
    owner_ids={747451011484090479, 727365670395838626},
    intents=discord.Intents.all(),
    help_command=PrettyHelp(),
    description=description,
    case_insensitive=True,
    start_time=start_time,
)


@bot.event
async def on_ready():
    print("Bot is ready")


"""
Commands related to cog
"""
admins = [747451011484090479, 727365670395838626]


@bot.command(hidden=True, description="Load cog")
async def load(self, ctx, extension):
    """
    Load cog
    """
    if ctx.author.id not in admins:
        bot.load_extension(f"cogs.{extension}")
        await ctx.send("Done")


@bot.command(hidden=True, description="Unload cog")
async def unload(self, ctx, extension):
    """
    Unload Cog
    """
    if ctx.author.id not in admins:
        bot.unload_extension(f"cogs.{extension}")
        await ctx.send("Done")


@bot.command(hidden=True, description="Reload cog")
async def reload(self, ctx, extension):
    """
    Reload Cog
    """
    if ctx.author.id not in admins:
        bot.unload_extension(f"cogs.{extension}")
        bot.load_extension(f"cogs.{extension}")
        await ctx.send("Done")


"""
Loads cog
"""
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.load_extension("jishaku")


token = os.environ.get("TOKEN")


bot.run(f"{token}")
