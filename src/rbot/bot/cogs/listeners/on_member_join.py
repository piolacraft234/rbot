from typing import Optional

import discord
from discord.ext import commands
from io import BytesIO
from loguru import logger

from src.rbot.bot.utilities.image import ImageUtilities
from src.rbot.constants import ChannelsConstants


class MemberJoinListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    @logger.catch
    async def on_member_join(self, member: discord.Member) -> None:
        """
        Event listener for when a new member joins the server.
        :param member: The member that joined the server.
        """
        # Get the welcome channel
        welcome_channel: Optional[discord.TextChannel] = discord.utils.get(
            member.guild.text_channels,
            id=ChannelsConstants.WELCOME_CHANNEL_ID
        )

        if welcome_channel is None:
            logger.error('Welcome channel not found.')
            return

        avatar_url: str = str(member.avatar.url)
        welcome_image: BytesIO = ImageUtilities.create_welcome_image(member.name, avatar_url)
        file: discord.File = discord.File(welcome_image, filename='welcome.png')
        embed: discord.Embed = discord.Embed(
            title='Welcome!',
            description=f'Hello {member.mention}, welcome to the server!',
            color=discord.Color.purple(),
            timestamp=member.joined_at
        )
        embed.set_image(url='attachment://welcome.png')
        await welcome_channel.send(embed=embed, file=file)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MemberJoinListener(bot))
