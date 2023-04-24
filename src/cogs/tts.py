import sqlite3
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
        self.voice = self.all_voices['Pokimane']
        self.voice_suggestions = [app_commands.Choice(name=name, value=name) for name in self.all_custom_voices.keys()]
        self.db_conn = self.init_db()

    @property
    def all_voices(self):
        return {voice.get_name(): voice for voice in self.user.get_all_voices()}

    @property
    def all_custom_voices(self):
        return {name: voice for name, voice in self.all_voices.items(
        ) if name not in ['Rachel', 'Domi', 'Bella', 'Antoni', 'Elli', 'Josh', 'Arnold', 'Adam', 'Sam']}

    def init_db(self):
        if not os.path.isfile("/data/tts_history.db"):
            conn = sqlite3.connect("/data/tts_history.db")
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE tts_history
                            (id INTEGER PRIMARY KEY, voice_initial_name TEXT, content TEXT, audio BLOB)''')
            conn.commit()
        else:
            conn = sqlite3.connect("/data/tts_history.db")
        return conn

    
    async def ensure_voice_ctx(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
    
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


    @commands.Cog.listener("on_message")
    async def tts(self, message):
        if message.channel.id != 1081842185135198208:
            return

        ctx = await self.bot.get_context(message)
        await self.ensure_voice_ctx(ctx)

        if message.content.lower() == "replay":
            # No need to fetch from the database; just play the existing .wav file
            pass
        else:
            tts_audio = self.voice.generate_audio_bytes(message.content)

            # Save to database
            cursor = self.db_conn.cursor()
            cursor.execute("INSERT INTO tts_history (voice_initial_name, content, audio) VALUES (?, ?, ?)", (self.voice.initialName, message.content, tts_audio))
            self.db_conn.commit()

            # Write audio to a .wav file
            with open("ElevenLabs_tts.wav", mode="wb") as f:
                f.write(tts_audio)

        # Play audio
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("ElevenLabs_tts.wav"))
        ctx.voice_client.play(source)

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

    @app_commands.command(name="play_tts_history", description="Play historical tts requests by voice")
    async def play_tts_history(self, interaction: discord.Interaction, voice: str, tts_audio: str):
        await interaction.response.defer()

        cursor = self.db_conn.cursor()
        cursor.execute("SELECT audio FROM tts_history WHERE id = ?", (tts_audio,))
        audio = cursor.fetchall()[0][0]

        # Write audio to a .wav file
        with open("ElevenLabs_tts.wav", mode="wb") as f:
            f.write(audio)

        await self.ensure_voice_interaction(interaction)

        # Play audio
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("ElevenLabs_tts.wav"))
        interaction.guild.voice_client.play(source)

    @play_tts_history.autocomplete(name="voice")
    async def play_history_voice_autocomplete(self, interaction: discord.Interaction, value: str):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT DISTINCT voice_initial_name FROM tts_history")
        voice_names = [row[0] for row in cursor.fetchall()]

        suggestions = [app_commands.Choice(name=name, value=name) for name in voice_names if name.lower().startswith(value.lower())]
        return suggestions
    
    @play_tts_history.autocomplete(name="tts_audio")
    async def play_history_message_autocomplete(self, interaction: discord.Interaction, value: str):
        selected_voice = interaction.namespace.voice
        
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT content, id FROM tts_history WHERE voice_initial_name = ?", (selected_voice,))
        query = cursor.fetchall()[::-1]

        if value == "":
            suggestions = [app_commands.Choice(name=msg_audio[0], value=str(msg_audio[1])) for msg_audio in query]
        else:
            suggestions = [app_commands.Choice(name=msg_audio[0], value=str(msg_audio[1])) for msg_audio in query if value.lower() in msg_audio[0].lower()]

        return suggestions


async def setup(bot):
    await bot.add_cog(TTSCog(bot))
