import logging
import os
from random import randint

import aiofiles
import discord
from discord import app_commands, Embed
from discord.ext import commands
from elevenlabslib import ElevenLabsUser
import psycopg2

log = logging.getLogger(__name__)


class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user = ElevenLabsUser(os.getenv("ELEVENLABS_TOKEN"))
        self.voice = self.all_custom_voices["Bokimane"]
        self.voice_suggestions = [app_commands.Choice(name=name, value=name) for name in self.all_custom_voices.keys()]
        # self.audio = self.voice.generate_audio_v3("test")
        # breakpoint()
        # self.db_conn = self.init_db()

    @property
    def all_custom_voices(self):
        return {
            voice.get_name(): voice
            for voice in self.user.get_all_voices()
            if voice.category == "cloned"
        }

    def init_db(self):
        return psycopg2.connect(host="db", port="5432", dbname="dill_bot_db", user="dill_bot", password=os.getenv("POSTGRES_PASSWORD"))

    async def ensure_voice_interaction(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(interaction.user.id)
        if interaction.guild.voice_client is None:
            if member.voice:
                await member.voice.channel.connect()
            else:
                await interaction.response.send_message("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
            
        elif interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()

    async def save_tts_to_db(self, voice_name, content, tts_audio):
        with self.db_conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tts_history (voice_initial_name, content, audio) VALUES (%s, %s, %s)",
                (voice_name, content, psycopg2.Binary(tts_audio)),
            )
        self.db_conn.commit()
        await self.write_audio_to_file(tts_audio)

    async def write_audio_to_file(self, tts_audio):
        async with aiofiles.open("ElevenLabs_tts.wav", mode="wb") as f:
            await f.write(tts_audio)

    @app_commands.command(name="select_voice", description="Select custom voice")
    async def select_voice(self, interaction: discord.Interaction, voice_name: str):
        await interaction.response.defer()

        valid_items = [name for name in self.all_custom_voices.keys()]

        if voice_name not in valid_items:
            await interaction.followup.send("Invalid voice name, please select a suggested voice")
            return

        self.voice = self.all_custom_voices[voice_name]
        await interaction.followup.send(f"Voice set to {voice_name}")

    @select_voice.autocomplete(name="voice_name")
    async def voice_autocomplete(self, interaction: discord.Interaction, value: str):
        return self.voice_suggestions
    
    @app_commands.command(name="tts", description="Text to speech")
    async def tts(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer()
        tts_audio = self.voice.generate_audio_v3(text)
        await self.save_tts_to_db(self.voice.name, text, tts_audio[0].result())

        await self.write_audio_to_file(tts_audio[0].result())
        await self.ensure_voice_interaction(interaction)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("ElevenLabs_tts.wav"))
        interaction.guild.voice_client.play(source)

    @app_commands.command(name="play_tts_history", description="Play historical tts requests by voice")
    async def play_tts_history(self, interaction: discord.Interaction, voice: str, tts_audio: str):
        await interaction.response.defer()

        with self.db_conn.cursor() as cursor:
            cursor.execute(f"SELECT audio, content FROM tts_history WHERE id = '{tts_audio}'")
            query = cursor.fetchall()
        audio = query[0][0]

        await self.write_audio_to_file(audio)
        await self.ensure_voice_interaction(interaction)

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("ElevenLabs_tts.wav"))
        interaction.guild.voice_client.play(source)

    @play_tts_history.autocomplete(name="voice")
    async def play_history_voice_autocomplete(self, interaction: discord.Interaction, value: str):
        with self.db_conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT voice_initial_name FROM tts_history")
            voice_names = [row[0] for row in cursor.fetchall()]

            suggestions = [
                app_commands.Choice(name=name, value=name)
                for name in voice_names
                if name.lower().startswith(value.lower())
            ]
            return suggestions

    @play_tts_history.autocomplete(name="tts_audio")
    async def play_history_message_autocomplete(self, interaction: discord.Interaction, value: str):
        selected_voice = interaction.namespace.voice

        with self.db_conn.cursor() as cursor:
            cursor.execute(f"SELECT content, id FROM tts_history WHERE voice_initial_name = '{selected_voice}'")
            query = cursor.fetchall()[::-1]

        if value == "":
            suggestions = [
                app_commands.Choice(name=f"ID: {msg_audio[1]} | {msg_audio[0]}"[:99], value=str(msg_audio[1]))
                for msg_audio in query
            ][:25]
        else:
            suggestions = [
                app_commands.Choice(name=f"ID: {msg_audio[1]} | {msg_audio[0]}"[:99], value=str(msg_audio[1]))
                for msg_audio in query
                if value.lower() in f"ID: {msg_audio[1]} | {msg_audio[0]}".lower()
            ][:25]

        return suggestions


async def setup(bot):
    await bot.add_cog(TTSCog(bot))
