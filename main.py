from datetime import datetime, timedelta
from os import environ, listdir, system

import aiohttp
import discord

# import uvloop
from discord.ext import commands
from pretty_help import PrettyHelp

# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
system("clear")


class PyBot(commands.Bot):
    def __init__(self):
        self.description = """
        PyBot - A Custom Bot for PyVerse Discord Server!
        """

        super().__init__(
            command_prefix={"!", ">", "."},
            owner_ids={747451011484090479, 727365670395838626},
            intents=discord.Intents.all(),
            help_command=PrettyHelp(),
            description=self.description,
            case_insensitive=True,
            start_time=datetime.utcnow(),
        )

    async def on_connnect(self):
        self.session = aiohttp.ClientSession(loop=self.loop)

        cT = datetime.now() + timedelta(
            hours=5, minutes=30
        )  # GMT+05:30 is Our TimeZone So.

        print(
            f"[ Log ] {self.user} Connected at {cT.hour}:{cT.minute}:{cT.second} / {cT.day}-{cT.month}-{cT.year}"
        )

    async def on_ready(self):
        cT = datetime.now() + timedelta(
            hours=5, minutes=30
        )  # GMT+05:30 is Our TimeZone So.

        print(
            f"[ Log ] {self.user} Ready at {cT.hour}:{cT.minute}:{cT.second} / {cT.day}-{cT.month}-{cT.year}"
        )
        print(f"[ Log ] GateWay WebSocket Latency: {self.latency*1000:.1f} ms")


TOKEN = environ.get("TOKEN")
bot = PyBot()

# Reaction embed
@bot.command(hidden=True)
@commands.is_owner()
async def wsend(ctx):
    """
    Use to send embeds for reaction Roles
    """
    e = discord.Embed(color=0x7289DA)
    e.add_field(
        name="Reaction Roles",
        value="**Operating System:**\n\n"
        "<:windows:819940534751199252> Windows\n\n"
        "<:linux:819940542283644988> Linux/ Unix\n\n"
        "**Notification Roles:**\n\n"
        "<:announcement:820155872914833459> Announcement\n\n"
        "<:chat_revive:820145356209389590> Chat Revive",
    )
    msg = await ctx.send(embed=e)
    await msg.add_reaction("<:windows:819940534751199252>")
    await msg.add_reaction("<:linux:819940542283644988>")
    await msg.add_reaction("<:announcement:820155872914833459>")
    await msg.add_reaction("<:chat_revive:820145356209389590>")


# Verification embed
@bot.command(hidden=True)
@commands.is_owner()
async def wsend2(ctx):
    e = discord.Embed(color=0x7289DA)
    e.add_field(
        name="Welcome to PyVerse",
        value="Before getting started please react with <:yes:820156388130160670> "
        "to get access to rest of the channels",
    )
    msg = await ctx.send(embed=e)
    await msg.add_reaction("<:yes:820156388130160670>")


[
    bot.load_extension(f"cogs.{file[:-3]}")
    for file in listdir("./cogs")
    if file.endswith(".py")
]

bot.load_extension("jishaku")
bot.loop.run_until_complete(bot.run(TOKEN))
