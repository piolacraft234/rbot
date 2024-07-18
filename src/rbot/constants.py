from ezjsonpy import translate_message, get_config_value


class PathConstants:
    COGS_PATH: str = 'src/rbot/bot/cogs'
    COG_PATH: str = 'src.rbot.bot.cogs'


class ChannelsConstants:
    VERIFICATION_CHANNEL_ID: int = get_config_value('verify.channelId', 'channels')
    MEMBERS_COUNT_CHANNEL_ID: int = get_config_value('stats.membersCountChannelId', 'channels')
    BOTS_COUNT_CHANNEL_ID: int = get_config_value('stats.botsCountChannelId', 'channels')
    CHANNELS_TO_CLEAR: list = get_config_value('toClean.channelsName', 'channels')


class MessagesConstants:
    VERIFICATION_MESSAGE_ID: int = get_config_value('verify.messageId', 'channels')


class RolesConstants:
    VERIFIED_ROLE_ID: int = get_config_value('memberRoleId', 'roles')


class DocsConstants:
    MCPTOOL_GUIDES = translate_message('commands.docs.projects.mcptool.guides')
    MCPCLIENT_GUIDES = translate_message('commands.docs.projects.mcpclient.guides')
