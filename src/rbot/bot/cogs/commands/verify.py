import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions
from ezjsonpy import translate_message
from loguru import logger

from src.rbot.bot.utilities.embed import EmbedUtilities
from src.rbot.constants import ChannelsConstants, MessagesConstants, RolesConstants


class VerificationView(discord.ui.View):
    @logger.catch
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RedButton(custom_id='red_button_left'))
        self.add_item(VerificationButton())
        self.add_item(RedButton(custom_id='red_button_right'))


class VerificationButton(discord.ui.Button):
    @logger.catch
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.success,
            label=translate_message('commands.verify.embed.buttonText'),
            custom_id='verify_button'
        )

    @logger.catch
    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback function for the verification button.
        :param interaction: The interaction object.
        """

        # Get the role by id
        role: discord.Role = interaction.guild.get_role(RolesConstants.VERIFIED_ROLE_ID)

        if not role:
            logger.critical(translate_message('commands.verify.embed.roleNotFoundLog'))
            await interaction.response.send_message(
                translate_message('commands.verify.embed.roleNotFound'), ephemeral=True
            )
            return

        await interaction.user.add_roles(role)
        await interaction.response.send_message(
            translate_message('commands.verify.verifySuccess'), ephemeral=True
        )


class RedButton(discord.ui.Button):
    @logger.catch
    def __init__(self, custom_id: str):
        super().__init__(
            style=discord.ButtonStyle.danger,
            label=translate_message('commands.verify.embed.buttonText'),
            custom_id=custom_id
        )

    @logger.catch
    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback function for the red button.

        :param interaction: The interaction object.
        """

        await interaction.response.send_message(
            translate_message('commands.verify.redButtonText'), ephemeral=True
        )


class VerifyCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permissions(administrator=True)
    @app_commands.command(name='send_verification', description='Send the verification message')
    @logger.catch
    async def send_verification(self, interaction: discord.Interaction) -> None:
        """
        Send the verification message.
        :param interaction: The interaction object.
        """
        logger.info("Sending verification message")

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        view: VerificationView = VerificationView()
        embed: discord.Embed = EmbedUtilities.create_embed(
            title=translate_message('commands.verify.embed.title'),
            description=translate_message('commands.verify.embed.description'),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, view=view)

    @logger.catch
    async def on_ready(self):
        """
        The on_ready function for the verification cog.
        This loads the verification message and sets the view.
        """
        channel: discord.TextChannel = self.bot.get_channel(ChannelsConstants.VERIFICATION_CHANNEL_ID)
        message: discord.Message = await channel.fetch_message(MessagesConstants.VERIFICATION_MESSAGE_ID)
        view: VerificationView = VerificationView()
        await message.edit(view=view)

    @send_verification.error
    @logger.catch
    async def send_verification_error(self, interaction: discord.Interaction, error: Exception) -> None:
        """
        Error handler for the send_verification command.
        :param interaction: The interaction object.
        :param error: The error that occurred.
        """

        if isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message(
                translate_message('commands.noPerms'), ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    cog: VerifyCommand = VerifyCommand(bot)
    await bot.add_cog(cog)
    bot.add_listener(cog.on_ready, 'on_ready')
