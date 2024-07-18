import subprocess
import os

import discord
from ezjsonpy import get_config_value
from discord.ext.commands.bot import Bot
from loguru import logger
from dotenv import load_dotenv

from .bot.bot import DiscordBot


class Main:
    def __init__(self):
        subprocess.run('cls || clear', shell=True)
        logger.add(
            'debug.log',
            format='[{time:YYYY-MM-DD HH:mm:ss} {level} - {file}, {line}] ⮞ <level>{message}</level>',
            retention='16 days',
            rotation='12:00',
            enqueue=True
        )
        load_dotenv()
        self._bot: Bot = DiscordBot.create_bot(
            command_prefix='!!!!!!!!!!!!!!',
            help_command=None,
            intents=discord.Intents.all()
        )
        self._start_bot()

    def _start_bot(self) -> None:
        """Start the bot."""
        self._bot.run(os.getenv('DISCORD_TOKEN'))
