from typing import Union

import discord
from discord.ext import commands, tasks
from ezjsonpy import translate_message
from loguru import logger

from src.rbot.constants import ChannelsConstants


class CleanupCog(commands.Cog):
    def __init__(self, bot, channel_names):
        self.bot = bot
        self.channel_names = channel_names
        self.cleanup_task.start()

    @tasks.loop(hours=24)
    @logger.catch
    async def cleanup_task(self) -> None:
        """Cleanup task to recreate the channels."""

        for channel_name in self.channel_names:
            channel: Union[discord.TextChannel, None] = discord.utils.get(
                self.bot.get_all_channels(),
                name=channel_name
            )

            if channel is None:
                logger.error(f'Channel with name "{channel_name}" not found.')
                continue

            if not isinstance(channel, discord.TextChannel):
                logger.error(f'Channel with name "{channel_name} is not a text channel.')

            await self.recreate_channel(channel)

    @staticmethod
    @logger.catch
    async def recreate_channel(channel: discord.TextChannel) -> None:
        """
        Recreate the channel to clean up messages.
        :param channel: The channel to recreate.
        """
        try:
            new_channel: discord.TextChannel = await channel.clone(
                reason=translate_message('tasks.canalCleaning.cloneReason')
            )
            await new_channel.edit(position=channel.position)
            await channel.delete(reason=translate_message('tasks.canalCleaning.deleteReason'))
            await new_channel.send(content=translate_message('tasks.canalCleaning.success'))

        except Exception as e:
            logger.error(f'Failed to recreate channel {channel.name}: {e}')

    @cleanup_task.before_loop
    @logger.catch
    async def before_cleanup(self) -> None:
        """Wait until the bot is ready before starting the cleanup task."""
        await self.bot.wait_until_ready()


async def setup(bot) -> None:
    channel_names: list[str] = ChannelsConstants.CHANNELS_TO_CLEAR
    await bot.add_cog(CleanupCog(bot, channel_names))
