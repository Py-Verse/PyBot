import os
from datetime import datetime

import discord
from discord.ext import commands


class ReactionRoles(commands.Cog):
    """
    Reaction roles stuff
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Reaction role Cog Loaded Succesfully")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == 820167136461979668:
            guild = self.bot.get_guild(payload.guild_id)
            user = await guild.fetch_member(payload.user_id)
            emoji_id = payload.emoji.id

            if emoji_id == 819940534751199252:
                # Windows - 819939970869231666 -> role id
                role = guild.get_role(819939970869231666)
                await user.add_roles(role)

            elif emoji_id == 819940542283644988:
                # Linux - 819940076090949642 -> role id
                role = guild.get_role(819940076090949642)
                await user.add_roles(role)

            elif emoji_id == 820155872914833459:
                # Announcement - 819770725170675722 -> role id
                role = guild.get_role(819770725170675722)
                await user.add_roles(role)

            elif emoji_id == 820145356209389590:
                # chat revive - 820127343901278219 -> role id
                role = guild.get_role(820127343901278219)
                await user.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id == 820167136461979668:
            guild = self.bot.get_guild(payload.guild_id)
            user = await guild.fetch_member(payload.user_id)
            emoji_id = payload.emoji.id

            if emoji_id == 819940534751199252:
                # Windows - 819939970869231666 -> role id
                role = guild.get_role(819939970869231666)
                await user.remove_roles(role)

            elif emoji_id == 819940542283644988:
                # Linux - 819940076090949642 -> role id
                role = guild.get_role(819940076090949642)
                await user.remove_roles(role)

            elif emoji_id == 820155872914833459:
                # Announcement - 819770725170675722 -> role id
                role = guild.get_role(819770725170675722)
                await user.remove_roles(role)

            elif emoji_id == 820145356209389590:
                # chat revive - 820127343901278219 -> role id
                role = guild.get_role(820127343901278219)
                await user.remove_roles(role)


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
