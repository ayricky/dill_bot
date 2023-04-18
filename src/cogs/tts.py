import logging
import os

import discord
from discord import app_commands
from discord.ext import commands
from elevenlabslib import ElevenLabsUser

log = logging.getLogger(__name__)


class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user = ElevenLabsUser(os.getenv("ELEVENLABS_TOKEN"))
        self.voice = self.all_voices['Pokimane']  # Set Pokimane by default
    
    @property
    def all_voices(self):
        return {voice.get_name(): voice for voice in self.user.get_all_voices()}

    @property
    def all_custom_voices(self):
        return {name: voice for name, voice in self.all_voices.items(
        ) if name not in ['Rachel', 'Domi', 'Bella', 'Antoni', 'Elli', 'Josh', 'Arnold', 'Adam', 'Sam']}

    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @app_commands.command(name="select_voice", description="Select custom voice")
    async def select_voice(self, interaction: discord.Interaction, item: str):
        # Acknowledge the interaction
        await interaction.response.defer(ephemeral=True)

        valid_items = [name for name in self.all_custom_voices.keys()]

        if item not in valid_items:
            await interaction.followup.send("Invalid voice name, please select a suggested voice")
            return

        self.voice = self.all_custom_voices[item]
        await interaction.followup.send(f"Voice set to {item}")


    @select_voice.autocomplete(name="item")
    async def skin_autocomplete(self, interaction: discord.Interaction, value: str):
        suggestions = [app_commands.Choice(name=name, value=name) for name in self.all_custom_voices.keys()]

        return suggestions

    @commands.Cog.listener("on_message")
    async def tts(self, message):
        if message.channel.id != 1081842185135198208:
            return

        ctx = await self.bot.get_context(message)
        await self.ensure_voice(ctx)

        if message.content.lower() != "replay":
            tts_audio = self.voice.generate_audio_bytes(message.content)
            with open("ElevenLabs_tts.wav", mode="wb") as f:
                f.write(tts_audio)

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("ElevenLabs_tts.wav"))
        ctx.voice_client.play(source)


async def setup(bot):
    await bot.add_cog(TTSCog(bot))
