import discord
from discord.ext import commands
from loguru import logger

from src.rbot.constants import ChannelsConstants


class MessageReactionListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    @logger.catch
    async def on_message(self, message: discord.Message) -> None:
        """
        Event listener for when a new message is sent in the server.
        :param message: The message that was sent.
        """
        if message.author.bot:
            return

        # Check if the message was sent in the suggestion channel
        if message.channel.id == ChannelsConstants.SUGGESTION_CHANNEL_ID:
            try:
                await message.add_reaction('✅')
                await message.add_reaction('❌')
                logger.info(f"Reacted to a message from {message.author} in {message.channel.name}")
            except Exception as e:
                logger.error(f"Failed to add reactions: {e}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MessageReactionListener(bot))
