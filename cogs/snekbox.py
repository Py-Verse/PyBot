"""
Credits goes to https://github.com/python-discord for the cog and docker
"""
import os
import re
import textwrap
from io import BytesIO
from signal import Signals
from typing import Optional, Tuple

import aiohttp
import discord
from discord.ext import commands

ip = os.environ.get("ip")  # for docker container
SIGKILL = 9
ESCAPE_REGEX = re.compile("[`\u202E\u200B]{3,}")
FORMATTED_CODE_REGEX = re.compile(
    r"(?P<delim>(?P<block>```)|``?)"  # code delimiter: 1-3 backticks; (?P=block) only matches if it's a block
    r"(?(block)(?:(?P<lang>[a-z]+)\n)?)"  # if we're in a block, match optional language (only letters plus newline)
    r"(?:[ \t]*\n)*"  # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"  # extract all code inside the markup
    r"\s*"  # any more whitespace before the end of the code markup
    r"(?P=delim)",  # match the exact same delimiter from the start again
    re.DOTALL | re.IGNORECASE,  # "." also matches newlines, case insensitive
)
RAW_CODE_REGEX = re.compile(
    r"^(?:[ \t]*\n)*"  # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"  # extract all the rest as code
    r"\s*$",  # any trailing whitespace until the end of the string
    re.DOTALL,  # "." also matches newlines
)


class Snekbox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    async def upload_output(self, output):
        if len(output) > 10000:
            return "output took too long to upload"
        async with aiohttp.ClientSession() as session:
            data3 = BytesIO(output.encode("utf-8"))
            async with session.post(
                "https://paste.pythondiscsord.com/documents", data=data3
            ) as resp:
                data2 = await resp.json()
                data = data2["key"]
        return f"https://paste.pythondiscsord.com{data}"

    @staticmethod
    def prepare_input(code: str) -> str:
        if match := list(FORMATTED_CODE_REGEX.finditer(code)):
            blocks = [block for block in match if block.group("block")]

            if len(blocks) > 1:
                code = "\n".join(block.group("code") for block in blocks)
                info = "several code blocks"
            else:
                match = match[0] if len(blocks) == 0 else blocks[0]
                code, block, lang, delim = match.group("code", "block", "lang", "delim")
                if block:
                    info = (
                        f"'{lang}' highlighted" if lang else "plain"
                    ) + " code block"
                else:
                    info = f"{delim}-enclosed inline code"
        else:
            code = RAW_CODE_REGEX.fullmatch(code).group("code")
            info = "unformatted or badly formatted code"

        code = textwrap.dedent(code)
        return code

    @staticmethod
    def get_results_message(results: dict) -> Tuple[str, str]:
        stdout, returncode = results["stdout"], results["returncode"]
        msg = f"Your eval code has been completed with code {returncode}"
        error = ""

        if returncode is None:
            msg = "Your eval code has failed"
            error = stdout.strip()
        elif returncode == 128 + SIGKILL:
            msg = "Your eval code timed out or ran out of memory"
        elif returncode == 255:
            msg = "Your eval code has failed"
            error = "A fatal NsJail error occurred"
        else:
            # Try to append signal's name if one exists
            try:
                name = Signals(returncode - 128).name
                msg = f"{msg} ({name})"
            except ValueError:
                pass

        return msg, error

    @staticmethod
    def get_status_emoji(results: dict) -> str:
        if not results["stdout"].strip():  # No output
            return "<:none:820188002022064138>"
        elif results["returncode"] == 0:  # No error
            return f"<:yes:820156388130160670>"
        else:  # Exception
            return f"<:no:820156423509114900>"

    async def format_output(self, output: str) -> Tuple[str, Optional[str]]:

        output = output.rstrip("\n")
        original_output = output  # To be uploaded to a pasting service if needed
        paste_link = None

        if "<@" in output:
            output = output.replace("<@", "<@\u200B")  # Zero-width space

        if "<!@" in output:
            output = output.replace("<!@", "<!@\u200B")  # Zero-width space

        if ESCAPE_REGEX.findall(output):
            paste_link = await self.upload_output(original_output)
            return (
                "You've tried to escape the Code block; will not output result",
                paste_link,
            )

        truncated = False
        lines = output.count("\n")

        if lines > 0:
            output = [
                f"{i:03d} | {line}" for i, line in enumerate(output.split("\n"), 1)
            ]
            output = output[:11]  # Limiting to only 11 lines
            output = "\n".join(output)

        if lines > 10:
            truncated = True
            if len(output) >= 1000:
                output = f"{output[:1000]}\n... (truncated - output too long, and contains too many lines)"
            else:
                output = f"{output}\n... (truncated - output contains too many lines)"
        elif len(output) >= 1000:
            truncated = True
            output = f"{output[:1000]}\n... (output capped - output too long)"

        if truncated:
            paste_link = await self.upload_output(original_output)

        output = output or "[Your code has no output]"

        return output, paste_link

    async def post_eval(self, code: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{ip}:8060/eval", json={"input": code}, raise_for_status=True
            ) as resp:
                return await resp.json()

    async def send_eval(self, ctx, code: str):
        async with ctx.typing():
            results = await self.post_eval(code)
            msg, error = self.get_results_message(results)

            if error:
                output, paste_link = error, None
            else:
                output, paste_link = await self.format_output(results["stdout"])

            icon = self.get_status_emoji(results)
            msg = f"{icon} {msg}.\n\n```\n{output}\n```"
            if paste_link:
                msg = f"{msg}\nFull output: {paste_link}"

            embed = discord.Embed(
                timestamp=ctx.message.created_at, description=msg, color=242424
            )
            embed.set_author(name="Eval Completed", icon_url=ctx.author.avatar_url)
            embed.set_footer(text="PyBot", icon_url="https://i.imgur.com/5SQ08L2.jpg")
            response = await ctx.send(embed=embed)
        return response

    @commands.command(
        aliases=["e", "run", "start", "exec", "do", "py", "python", "code"]
    )
    async def eval(self, ctx, *, text):
        if not text:  # None or empty string
            return await ctx.send_help("Insert Python Code.")

        code = self.prepare_input(text)
        await ctx.send(f"{ctx.author.mention}", delete_after=1)
        response = await self.send_eval(ctx, code)


def setup(bot):
    bot.add_cog(Snekbox(bot))
