import os

import aiohttp
import discord
from discord import AsyncWebhookAdapter, Webhook
from discord.ext import commands

url = os.environ.get("logs")
colors = [""]


class PyEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("PyEvents cog loaded")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if (
            before.author.bot
            or after.author.bot
            or after.author.id == 808890188117442611
        ):
            return
        elif before.guild is None:
            return

        elif before.pinned or after.pinned:
            try:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(
                        url, adapter=AsyncWebhookAdapter(session)
                    )
                    e = discord.Embed()
                    e.add_field(
                        name=f"Pins changed by {after.author.name} ({after.author.id}) in {after.channel}",
                        value=f"[Message Link]({after.jump_url}) | {after.channel.mention} |{after.author.mention}",
                    )
                    e.set_thumbnail(url=after.author.avatar_url)
                    e.set_author(name="Log", icon_url=after.author.avatar_url)
                    await webhook.send(embed=e)

            except Exception as e:
                print(e)
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(
                        url, adapter=AsyncWebhookAdapter(session)
                    )
                    e = discord.Embed()
                    e.add_field(
                        name=f"Changes by - {after.author.name} ({after.author.id})",
                        value=f"From -> {before.content}\n to -> {after.content}\n**[Message link]({after.jump_url})**  |"
                        " {after.channel.mention} | {after.author.mention}",
                        inline=False,
                    )
                    e.set_author(name="Log", icon_url=after.author.avatar_url)
                    await webhook.send(embed=e)
            except Exception as e:
                print(e)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
                e = discord.Embed()
                e.add_field(
                    name=f"{user.name} ({user.id}) got banned",
                    value="\u200b",
                    inline=False,
                )
                await webhook.send(embed=e)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
                e = discord.Embed()
                e.add_field(
                    name="\u200b", value=f"**[Invite created]({invite})**", inline=False
                )
                e.set_author(name="Log", icon_url="https://i.imgur.com/fXUI76n.png")
                e.set_footer(text="PyBot Logging")
                await webhook.send(embed=e)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
                e = discord.Embed()
                e.add_field(name="\u200b", value="Invite deleted", inline=False)
                e.set_author(name="Log", icon_url="https://i.imgur.com/fXUI76n.png")
                e.set_footer(text="PyBot Logging")
                await webhook.send(embed=e)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
                e = discord.Embed()
                e.add_field(
                    name=f"{user.name} ({user.id}) got unbanned",
                    value="\u200b",
                    inline=False,
                )
                await webhook.send(embed=e)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
                e = discord.Embed()
                e.add_field(
                    name=f"Message deleted of - {message.author.name} ({message.author.id})",
                    value=f"Message -> {message.content}\n{message.author.mention} | {message.channel.mention}",
                    inline=False,
                )
                e.set_author(name="Log", icon_url=message.author.avatar_url)
                await webhook.send(embed=e)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
                e = discord.Embed()
                e.add_field(
                    name="Message Deleted in Bulk",
                    value=f"{len(messages)} got deleted in {messages[0].channel.mention}",
                    inline=False,
                )
                e.set_author(name="Log", icon_url="https://i.imgur.com/fXUI76n.png")
                await webhook.send(embed=e)
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
                e = discord.Embed()
                e.add_field(
                    name=f"Role created -> {role.name} ({role.id})",
                    value=f"{role.mention} | Logging",
                    inline=False,
                )
                e.set_author(name="Log", icon_url="https://i.imgur.com/fXUI76n.png")
                await webhook.send(embed=e)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
                e = discord.Embed()
                e.add_field(
                    name=f"Role deleted -> {role.name} ({role.id})",
                    value=f"{role.mention} | Logging",
                    inline=False,
                )
                e.set_author(name="Log", icon_url="https://i.imgur.com/fXUI76n.png")
                await webhook.send(embed=e)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            try:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(
                        url, adapter=AsyncWebhookAdapter(session)
                    )
                    e = discord.Embed()
                    e.add_field(
                        name=f"Nickname changed of {after.name}",
                        value=f"Before -> {before.nick}\nNow -> {after.nick}\n{after.id} | {after.mention}",
                    )
                    e.set_author(name="Log", icon_url=after.avatar_url)
                    await webhook.send(embed=e)
            except Exception:
                pass

        else:
            pass


def setup(bot):
    bot.add_cog(PyEvents(bot))
