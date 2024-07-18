from ezjsonpy import load_language, set_language, load_configurations


if __name__ == '__main__':
    load_configurations(
        [
            {'name': 'default', 'path': 'settings/settings.json'},
            {'name': 'channels', 'path': 'settings/channels.json'},
            {'name': 'partners', 'path': 'settings/partners.json'},
            {'name': 'roles', 'path': 'settings/roles.json'}
        ]
    )
    load_language('en', 'languages/en.json')
    set_language('en')
    from src.rbot import Main
    Main()
