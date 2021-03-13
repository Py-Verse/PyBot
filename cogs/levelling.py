import os

import discord
import motor.motor_asyncio
import nest_asyncio
from discord.ext import commands

nest_asyncio.apply()

mongo_url = os.environ.get("mongo")

cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
levelling = cluster["discord"]["levelling"]

bot_channel = 813687679014797332
talk_channels = [813721664789151755, 813687603693617183]
level = [818422360596021269, 818422705241456681, 818423232502956032, 818422958699184128]
levelnum = [5, 10, 20, 40]


class Level(commands.Cog):
    """
    Levelling system for PyBot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Level cog loaded successfully")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in talk_channels:
            stats = await levelling.find_one({"id": message.author.id})
            if not message.author.bot or message.guild is None:
                if stats is None:
                    newuser = {"id": message.author.id, "xp": 10}
                    await levelling.insert_one(newuser)
                else:
                    xp = stats["xp"] + 5
                    await levelling.update_one(
                        {"id": message.author.id}, {"$set": {"xp": xp}}
                    )

                    lvl = 0

                    while True:
                        if xp < ((50 * (lvl ** 2)) + (50 * (lvl))):
                            break
                        lvl += 1
                    xp -= (50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1))

                    if xp == 0:
                        await message.channel.send(
                            f"{message.author.mention} You levelled up to **level: {lvl}**"
                        )

                        try:
                            for i in range(len(level)):
                                if lvl == levelnum[i]:
                                    role = message.guild.get_role(level[i])
                                    await message.author.add_roles(role)
                        except Exception as e:
                            # print(e)
                            pass


def setup(bot):
    bot.add_cog(Level(bot))
