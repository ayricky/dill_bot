import logging
import os

import aiohttp
import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class DillBot(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(
            roles=False,
            everyone=False,
            users=True,
        )
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=False,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
            message_content=True,
        )
        super().__init__(
            command_prefix=">",
            intents=intents,
            allowed_mentions=allowed_mentions,
        )
        self.initial_extensions = [
            "cogs.admin",
            "cogs.dice",
            "cogs.music",
            "cogs.tts",
        ]

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        for ext in self.initial_extensions:
            log.info(f"loading {ext}")
            await self.load_extension(ext)

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = discord.utils.utcnow()

        log.info(f"Ready: {self.user} (ID: {self.user.id})")


if __name__ == "__main__":
    bot = DillBot()
    bot.run(
        os.getenv("DISCORD_TOKEN"),
        root_logger=True,
    )
