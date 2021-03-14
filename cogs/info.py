import difflib
import inspect
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union

import discord
import motor.motor_asyncio
import nest_asyncio
from discord import Colour, Embed, utils
from discord.ext import commands
from discord.ext.commands import BadArgument, Context

from utils.messages import send_denial
from utils.paginator import LinePaginator

nest_asyncio.apply()

mongo_url = os.environ.get("mongo")

cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
levelling = cluster["discord"]["levelling"]

SourceType = Union[
    commands.HelpCommand,
    commands.Command,
    commands.Cog,
    str,
    commands.ExtensionNotLoaded,
]


DESCRIPTIONS = ("Command processing time", "Discord API latency")
ROUND_LATENCY = 3


ZEN_OF_PYTHON = """\
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
"""


class SourceConverter(commands.Converter):
    """Convert an argument into a help command, tag, command, or cog."""

    async def convert(self, ctx: commands.Context, argument: str) -> SourceType:
        """Convert argument into source object."""
        if argument.lower().startswith("help"):
            return

        cog = ctx.bot.get_cog(argument)
        if cog:
            return cog

        cmd = ctx.bot.get_command(argument)
        if cmd:
            return cmd

        tags_cog = ctx.bot.get_cog("Tags")
        show_tag = True

        if not tags_cog:
            show_tag = False
        elif argument.lower() in tags_cog._cache:
            return argument.lower()

        escaped_arg = utils.escape_markdown(argument)

        raise commands.BadArgument(
            f"Unable to convert '{escaped_arg}' to valid command{', tag,' if show_tag else ''} or Cog."
        )


class Info(commands.Cog):
    """ Commands related to information """

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Info Cog Loaded Successfully")

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """
        Gets different measures of latency within the bot.
        Returns bot, Discord Protocol latency.
        """
        # datetime.datetime objects do not have the "milliseconds" attribute.
        # It must be converted to seconds before converting to milliseconds.
        bot_ping = (datetime.utcnow() - ctx.message.created_at).total_seconds() * 1000
        bot_ping = f"{bot_ping:.{ROUND_LATENCY}f} ms"

        # Discord Protocol latency return value is in seconds, must be multiplied by 1000 to get milliseconds.
        discord_ping = f"{self.bot.latency * 1000:.{ROUND_LATENCY}f} ms"

        embed = Embed(title="Pong!", color=0x00FFCC)

        for desc, latency in zip(DESCRIPTIONS, [bot_ping, discord_ping]):
            embed.add_field(name=desc, value=latency, inline=False)

        await ctx.reply(embed=embed)

    @commands.command()
    async def charinfo(self, ctx, *, characters):
        """Shows you information on up to 50 unicode characters."""
        match = re.match(r"<(a?):(\w+):(\d+)>", characters)
        if match:
            return await send_denial(
                ctx,
                "**Non-Character Detected**\n"
                "Only unicode characters can be processed, but a custom Discord emoji "
                "was found. Please remove it and try again.",
            )

        if len(characters) > 50:
            return await send_denial(ctx, f"Too many characters ({len(characters)}/50)")

        def get_info(char: str) -> Tuple[str, str]:
            digit = f"{ord(char):x}"
            if len(digit) <= 4:
                u_code = f"\\u{digit:>04}"
            else:
                u_code = f"\\U{digit:>08}"
            url = f"https://www.compart.com/en/unicode/U+{digit:>04}"
            name = f"[{unicodedata.name(char, '')}]({url})"
            info = f"`{u_code.ljust(10)}`: {name} - {utils.escape_markdown(char)}"
            return info, u_code

        char_list, raw_list = zip(*(get_info(c) for c in characters))
        embed = Embed().set_author(name="Character Info")

        if len(characters) > 1:
            # Maximum length possible is 502 out of 1024, so there's no need to truncate.
            embed.add_field(
                name="Full Raw Text", value=f"`{''.join(raw_list)}`", inline=False
            )

        await LinePaginator.paginate(
            char_list, ctx, embed, max_lines=10, max_size=2000, empty=False
        )

    @commands.command(hidden=True)
    async def codeblock(self, ctx):
        embed = discord.Embed(title="CodeBlocks", color=0xFF0000)
        embed.set_image(url="https://i.imgur.com/va1dpTv.png")
        embed.set_footer(text="**These are backticks**, not quotes.")
        await ctx.reply(embed=embed)

    @commands.command()
    async def zen(
        self, ctx: Context, *, search_value: Union[int, str, None] = None
    ) -> None:
        """
        Show the Zen of Python.
        Without any arguments, the full Zen will be produced.
        If an integer is provided, the line with that index will be produced.
        If a string is provided, the line which matches best will be produced.
        """
        embed = Embed(
            colour=Colour.blurple(),
            title="The Zen of Python",
            description=ZEN_OF_PYTHON,
        )

        if search_value is None:
            embed.title += ", by Tim Peters"
            await ctx.send(embed=embed)
            return

        zen_lines = ZEN_OF_PYTHON.splitlines()

        # handle if it's an index int
        if isinstance(search_value, int):
            upper_bound = len(zen_lines) - 1
            lower_bound = -1 * upper_bound
            if not (lower_bound <= search_value <= upper_bound):
                raise BadArgument(
                    f"Please provide an index between {lower_bound} and {upper_bound}."
                )

            embed.title += f" (line {search_value % len(zen_lines)}):"
            embed.description = zen_lines[search_value]
            await ctx.send(embed=embed)
            return

        # Try to handle first exact word due difflib.SequenceMatched may use some other similar word instead
        # exact word.
        for i, line in enumerate(zen_lines):
            for word in line.split():
                if word.lower() == search_value.lower():
                    embed.title += f" (line {i}):"
                    embed.description = line
                    await ctx.send(embed=embed)
                    return

        # handle if it's a search string and not exact word
        matcher = difflib.SequenceMatcher(None, search_value.lower())

        best_match = ""
        match_index = 0
        best_ratio = 0

        for index, line in enumerate(zen_lines):
            matcher.set_seq2(line.lower())

            # the match ratio needs to be adjusted because, naturally,
            # longer lines will have worse ratios than shorter lines when
            # fuzzy searching for keywords. this seems to work okay.
            adjusted_ratio = (len(line) - 5) ** 0.5 * matcher.ratio()

            if adjusted_ratio > best_ratio:
                best_ratio = adjusted_ratio
                best_match = line
                match_index = index

        if not best_match:
            raise BadArgument(
                "I didn't get a match! Please try again with a different search term."
            )

        embed.title += f" (line {match_index}):"
        embed.description = best_match
        await ctx.send(embed=embed)

    # Source command

    @commands.command(name="source", aliases=("src",))
    async def source_command(
        self, ctx: commands.Context, *, source_item: SourceConverter = None
    ) -> None:
        """Display information and a GitHub link to the source code of a command, tag, or cog."""
        if not source_item:
            embed = Embed(title="Bot's GitHub Repository", color=0x00FFCC)
            embed.add_field(
                name="Repository",
                value="[Go to GitHub](https://github.com/Py-Verse/PyBot)",
            )
            embed.set_thumbnail(url="https://avatars1.githubusercontent.com/u/9919")
            await ctx.send(embed=embed)
            return

        embed = await self.build_embed(source_item)
        await ctx.send(embed=embed)

    def get_source_link(
        self, source_item: SourceType
    ) -> Tuple[str, str, Optional[int]]:
        """
        Build GitHub link of source item, return this link, file location and first line number.
        Raise BadArgument if `source_item` is a dynamically-created object (e.g. via internal eval).
        """
        if isinstance(source_item, commands.Command):
            src = source_item.callback.__code__
            filename = src.co_filename
        elif isinstance(source_item, str):
            tags_cog = self.bot.get_cog("Tags")
            filename = tags_cog._cache[source_item]["location"]
        else:
            src = type(source_item)
            try:
                filename = inspect.getsourcefile(src)
            except TypeError:
                raise commands.BadArgument(
                    "Cannot get source for a dynamically-created object."
                )

        if not isinstance(source_item, str):
            try:
                lines, first_line_no = inspect.getsourcelines(src)
            except OSError:
                raise commands.BadArgument(
                    "Cannot get source for a dynamically-created object."
                )

            lines_extension = f"#L{first_line_no}-L{first_line_no+len(lines)-1}"
        else:
            first_line_no = None
            lines_extension = ""

        # Handle tag file location differently than others to avoid errors in some cases
        if not first_line_no:
            file_location = Path(filename).relative_to("/bot/")
        else:
            file_location = Path(filename).relative_to(Path.cwd()).as_posix()

        url = f"https://github.com/Py-Verse/PyBot/blob/master/{file_location}{lines_extension}"

        return url, file_location, first_line_no or None

    async def build_embed(self, source_object: SourceType) -> Optional[Embed]:
        """Build embed based on source object."""
        url, location, first_line = self.get_source_link(source_object)

        if isinstance(source_object, commands.HelpCommand):
            title = "Help Command"
            description = source_object.__doc__.splitlines()[1]
        elif isinstance(source_object, commands.Command):
            description = source_object.short_doc
            title = f"Command: {source_object.qualified_name}"
        elif isinstance(source_object, str):
            title = f"Tag: {source_object}"
            description = ""
        else:
            title = f"Cog: {source_object.qualified_name}"
            description = source_object.description.splitlines()[0]

        embed = Embed(title=title, description=description, color=0x00FFCC)
        embed.add_field(name="Source Code", value=f"[Go to GitHub]({url})")
        line_text = f":{first_line}" if first_line else ""
        embed.set_footer(text=f"{location}{line_text}")

        return embed

    # Levelling stuff

    @commands.command(aliases=["xp", "r"])
    async def rank(self, ctx, member: discord.Member = None):
        """
        Shows the rank of mentioned user / yours
        """
        if member is None:
            member = ctx.author
        else:
            pass
        stats = await levelling.find_one({"id": member.id})
        if stats is None:
            embed = discord.Embed(timestamp=ctx.message.created_at)

            embed.set_author(name="You have not sent messages.")

            await ctx.channel.send(embed=embed)

        else:
            xp = stats["xp"]
            lvl = 0
            rank = 0

            while True:
                if xp < ((50 * (lvl ** 2)) + (50 * (lvl))):
                    break
                lvl += 1
            xp -= (50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1))

            rankings = levelling.find().sort("xp", -1)

            async for x in rankings:
                rank += 1
                if stats["id"] == x["id"]:
                    break

            embed = discord.Embed(
                timestamp=ctx.message.created_at,
                title=f"{ctx.author.name}'s Level stats",
                color=0xFF0000,
            )
            embed.add_field(name="Name", value=f"{member.mention}", inline=True)
            embed.add_field(
                name="XP", value=f"{xp}/{int(200* ((1/2)*lvl))}", inline=True
            )
            embed.add_field(name="Global Rank", value=f"{rank}", inline=True)
            embed.add_field(name="Level", value=f"{lvl}", inline=True)
            embed.set_thumbnail(url=member.avatar_url)
            await ctx.channel.send(embed=embed)

    @commands.command(
        aliases=["db", "dashboard", "leaderboard"],
        description="Shows server leaderboard",
    )
    async def lb(self, ctx):
        """
        Shows the members with highest xp
        """
        rankings = levelling.find().sort("xp", -1)
        i = 1
        embed = discord.Embed(
            timestamp=ctx.message.created_at, title="Rankings", color=0xFF0000
        )
        async for x in rankings:
            try:
                temp = ctx.guild.get_member(x["id"])
                tempxp = x["xp"]
                embed.add_field(
                    name=f"{i} : {temp.name}", value=f"XP: {tempxp}", inline=False
                )
                i += 1
            except Exception as e:
                print(e)
            if i == 11:
                break

        embed.set_footer(
            text=f"Requested By: {ctx.author.name}", icon_url=f"{ctx.author.avatar_url}"
        )

        await ctx.channel.send(embed=embed)


def setup(bot) -> None:
    """Load the Latency cog."""
    bot.add_cog(Info(bot))
