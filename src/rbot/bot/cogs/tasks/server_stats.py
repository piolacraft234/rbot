from typing import Union

import discord
from discord.ext import commands, tasks
from loguru import logger

from src.rbot.constants import ChannelsConstants


class UpdateServerStatsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.update_stats_task.start()

    @tasks.loop(minutes=5)
    @logger.catch
    async def update_stats_task(self) -> None:
        """Update the server stats (member count and bot count)."""

        guild: discord.Guild = self.bot.get_guild(self.bot.guild_id)
        total_members = len([member for member in guild.members if not member.bot])
        total_bots = len([member for member in guild.members if member.bot])

        members_channel: Union[discord.VoiceChannel, None] = discord.utils.get(
            guild.voice_channels,
            id=ChannelsConstants.MEMBERS_COUNT_CHANNEL_ID
        )

        bots_channel: Union[discord.VoiceChannel, None] = discord.utils.get(
            guild.voice_channels,
            id=ChannelsConstants.BOTS_COUNT_CHANNEL_ID
        )

        if members_channel is not None:
            await members_channel.edit(name=f'Members: {total_members}')

        else:
            logger.error(f'Channel with id "{ChannelsConstants.MEMBERS_COUNT_CHANNEL_ID}" not found.')

        if bots_channel is not None:
            await bots_channel.edit(name=f'Bots: {total_bots}')

        else:
            logger.error(f'Channel with id "{ChannelsConstants.BOTS_COUNT_CHANNEL_ID}" not found.')

    @update_stats_task.before_loop
    @logger.catch
    async def before_update(self) -> None:
        """Wait until the bot is ready before starting the cleanup task."""
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UpdateServerStatsCog(bot))
