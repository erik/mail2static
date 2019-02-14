import os
import os.path
import sys
import textwrap

import toml


_DEFAULT_CONFIGURATION = dict(
    http=dict(
        host='127.0.0.1',
        port=8080,
        debug=True
    ),
    smtp=dict(
        # host
        # port
        # email
        # password
    ),
    mailgun=dict(
        # api_key: required
    ),
    sites=dict()
)

_REQUIRED_CONFIGURATION = dict(
    smtp=['host', 'port', 'email', 'password'],
    mailgun=['api_key'],
    sites=dict(),
)


_DEFAULT_SITE_CONFIGURATION = dict(
    before_run=None,
    after_run=None,

    approved_senders=[],

    post_base_path='_posts/',
    asset_base_dir='assets/',
    asset_base_url='/assets/',

    post_template=textwrap.dedent('''\
    ---
    layout: post
    title: {title}
    ---
    {content}
    ''')
)

_REQUIRED_SITE_CONFIGURATION = [
    'directory',
    'inbox_address',
    'secret'
]


def _discover_config_file():
    config_file = os.environ.get(
        'MAIL2STATIC_CONFIG',
        './mail2static.toml')

    config_file = os.path.expanduser(config_file)

    if not os.path.exists(config_file):
        sys.exit(f'file not found: {config_file}')

    return config_file


def _parse_file(file_name):
    with open(file_name, 'r') as fp:
        return toml.load(fp)


def _validate_required(config):
    for section, required in _REQUIRED_CONFIGURATION.items():
        if section not in config:
            sys.exit(f'missing required configuration section: "{section}"')

        for k in required:
            if k not in config[section]:
                sys.exit(f'missing required configuration: "{section}.{k}"')

    for required in _REQUIRED_SITE_CONFIGURATION:
        for site, site_config in config['sites'].items():
            if required not in site_config:
                sys.exit(f'missing required configuration for "sites.{site}": '
                         '{required}')


def _merge_default_configuration(config):
    """Destructively merge ``config`` with default configurations."""
    for section, values in _DEFAULT_CONFIGURATION.items():
        if section not in config:
            config[section] = {}

        for k, v in values.items():
            if k not in config[section]:
                config[section][k] = v

    for site in config['sites'].values():
        for k, v in _DEFAULT_SITE_CONFIGURATION.items():
            if k not in site:
                site[k] = v

    return config


def load():
    name = _discover_config_file()
    config = _parse_file(name)

    _validate_required(config)

    return _merge_default_configuration(config)
