from typing import Union

import discord
from discord import app_commands
from discord.ext import commands
from ezjsonpy import get_config_value, set_config_value, translate_message
from loguru import logger

from src.rbot.bot.utilities.embed import EmbedUtilities
from src.rbot.utilities.url import UrlUtilities


class PartnerCommandGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="partner", description="Partner commands.")

    @app_commands.command(
        name="add",
        description="Add a new partner."
    )
    @has_permissions(administrator=True)
    @logger.catch
    async def add(self, interaction: discord.Interaction, name: str, description: str, logo: str, invite: str):
        """
        Add a new partner to the list.
        :param interaction: The interaction object.
        :param name: The name of the partner.
        :param description: The description of the partner.
        :param logo: The logo of the partner.
        :param invite: The invite link of the partner.
        """

        partners: list[dict[str, str]] = self.get_partners()
        partners_name: list = [partner['name'] for partner in partners]

        if name in partners_name:
            await interaction.response.send_message(
                translate_message('commands.partner.partnerExists'),
                ephemeral=True
            )
            return

        if UrlUtilities.is_valid_url(logo) is False:
            await interaction.response.send_message(
                f'{translate_message("generalErrors.invalidUrl")} (logo)',
                ephemeral=True
            )
            return

        if UrlUtilities.is_valid_url(invite) is False:
            await interaction.response.send_message(
                f'{translate_message("generalErrors.invalidUrl")} (invite)',
                ephemeral=True
            )
            return

        # Get the partners channel and send the embed
        channel: discord.TextChannel = self.get_partners_channel(interaction)

        if channel is None:
            return

        embed = EmbedUtilities.create_embed(
            title=name,
            description=description,
            color=discord.Color.purple(),
            thumbnail=logo,
            url=invite,
            footer=translate_message('commands.partner.embed.footer')
        )
        partner_message_id: discord.Message = await channel.send(embed=embed)
        # Add the partner to the list
        partners.append({
            'name': name,
            'description': description,
            'logo': logo,
            'invite': invite,
            'messageId': partner_message_id.id
        })
        set_config_value('partners', partners, 'partners')
        await interaction.response.send_message(
            translate_message('commands.partner.partnerAdded'),
            ephemeral=True
        )

    @app_commands.command(
        name="remove",
        description="Remove a partner."
    )
    @has_permissions(administrator=True)
    @logger.catch
    async def remove(self, interaction: discord.Interaction, name: str):
        """
        Remove a partner from the list.
        :param interaction: The interaction object.
        :param name: The name of the partner.
        """

        partners: list[dict[str, str]] = self.get_partners()
        partners_name: list = [partner['name'] for partner in partners]

        if name not in partners_name:
            await interaction.response.send_message(
                translate_message('commands.partner.partnerNotFound'),
                ephemeral=True
            )
            return

        # Get the partners channel and remove the embed
        channel: discord.TextChannel = self.get_partners_channel(interaction)

        if channel is None:
            return

        # Get embed partner message by id
        partner: dict = [partner for partner in partners if partner['name'] == name][0]
        partner_message_id: int = int(partner['messageId'])
        partner_message = await channel.fetch_message(partner_message_id)

        if partner_message is None:
            await interaction.response.send_message(
                translate_message('commands.partner.partnerMessageNotFound'),
                ephemeral=True
            )

        # Delete message
        await partner_message.delete()
        # Update partners config
        partners = [partner for partner in partners if partner['name'] != name]
        set_config_value('partners', partners, 'partners')
        await interaction.response.send_message(
            translate_message('commands.partner.partnerRemoved'),
            ephemeral=True
        )

    @staticmethod
    @logger.catch
    def get_partners() -> list[dict[str, str]]:
        """
        Get the partners from the config.
        :return: The partners.
        """
        partners: list[dict[str, str]] = get_config_value('partners', 'partners')
        return partners

    @staticmethod
    @logger.catch
    def get_partners_channel(interaction: discord.Interaction) -> Union[discord.TextChannel, None]:
        """
        Get the partners channel.
        :return: The partners channel.
        """
        channel_id: int = get_config_value('partners.channelId', 'channels')
        channel: discord.TextChannel = discord.utils.get(interaction.guild.text_channels, id=channel_id)
        return channel


class PartnerCommand(commands.Cog):
    @logger.catch
    def __init__(self, bot: commands.Bot) -> None:
        """
        Initialize the DocsCommand class.
        :param bot: The bot instance.
        """
        self.bot = bot
        self.bot.tree.add_command(PartnerCommandGroup())


async def setup(bot: commands.Bot) -> None:
    """
    Set up the docs command.
    :param bot: The bot instance.
    """
    await bot.add_cog(PartnerCommand(bot))
