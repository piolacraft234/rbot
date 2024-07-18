import discord
from discord import app_commands
from discord.ext import commands
from ezjsonpy import translate_message
from loguru import logger

from ....constants import DocsConstants


def create_guide_embed(title: str, description: str, project: str) -> discord.Embed:
    """
    Create a guide embed for the docs command.
    :param title:  The title of the embed.
    :param description:  The description of the embed.
    :param project: The project the guide is for.
    :return: The embed.
    """
    return discord.Embed(
        title=f'{translate_message("commands.docs.embed.title")} {title.capitalize()}'.replace('%project%', project),
        description=description,
        color=discord.Color.green()
    )


class DocsGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="docs", description=translate_message('commands.docs.description'))

    @app_commands.command(
        name="mcptool",
        description=translate_message('commands.docs.projects.mcptool.description')
    )
    @app_commands.describe(guide="MCPTool guide")
    @logger.catch
    async def mcptool(self, interaction: discord.Interaction, guide: str) -> None:
        """
        Send the MCPTool guide.
        :param interaction: The interaction object.
        :param guide: The guide to send.
        """
        if guide not in DocsConstants.MCPTOOL_GUIDES:
            await interaction.response.send_message(
                translate_message('commands.docs.guideNotFound'), ephemeral=True
            )
            return

        embed: discord.Embed = create_guide_embed(guide, DocsConstants.MCPTOOL_GUIDES[guide], 'MCPTool')
        await interaction.response.send_message(embed=embed)

    @mcptool.autocomplete('guide')
    @logger.catch
    async def mcptool_autocomplete(self, interaction: discord.Interaction, current: str) -> list:
        """
        Autocomplete for the MCPTool command.
        :param interaction: The interaction object.
        :param current: The current input.
        :return: The autocomplete list.
        """
        guides: list = list(DocsConstants.MCPTOOL_GUIDES.keys())
        return [app_commands.Choice(name=guide, value=guide) for guide in guides if current.lower() in guide.lower()]

    @app_commands.command(
        name="mcpclient",
        description=translate_message('commands.docs.projects.mcpclient.description')
    )
    @app_commands.describe(guide="MCPClient guide")
    @logger.catch
    async def mcpclient(self, interaction: discord.Interaction, guide: str) -> None:
        """
        Send the MCPClient guide.
        :param interaction: The interaction object.
        :param guide: The guide to send.
        """
        if guide not in DocsConstants.MCPTOOL_GUIDES:
            await interaction.response.send_message(
                translate_message('commands.docs.guideNotFound'), ephemeral=True
            )
            return

        embed: discord.Embed = create_guide_embed(guide, DocsConstants.MCPCLIENT_GUIDES[guide], 'MCPClient')
        await interaction.response.send_message(embed=embed)

    @mcpclient.autocomplete('guide')
    @logger.catch
    async def mcpclient_autocomplete(self, interaction: discord.Interaction, current: str) -> list:
        """
        Autocomplete for the MCPClient command.
        :param interaction: The interaction object.
        :param current: The current input.
        :return: The autocomplete list.
        """
        guides: list = list(DocsConstants.MCPCLIENT_GUIDES.keys())
        return [app_commands.Choice(name=guide, value=guide) for guide in guides if current.lower() in guide.lower()]


class DocsCommand(commands.Cog):
    @logger.catch
    def __init__(self, bot: commands.Bot) -> None:
        """
        Initialize the DocsCommand class.
        :param bot: The bot instance.
        """
        self.bot = bot
        self.bot.tree.add_command(DocsGroup())


async def setup(bot: commands.Bot) -> None:
    """
    Set up the docs command.
    :param bot: The bot instance.
    """
    await bot.add_cog(DocsCommand(bot))

