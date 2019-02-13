import os.path

import toml


DEFAULT_CONFIGURATION = dict(
    http=dict(
        # host
        # port
        # debug
    ),
    git=dict(
        # clone_dir: required
        # commit_author: required
    ),
    smtp=dict(
        # host
        # port
        # email
        # password
    ),
    mailgun=dict(
        # api_key: required
    )
)


DEFAULT_SITE_CONFIG = dict(
    # git_remote: required
    # inbox_address: required
    # subject_line_secret: required
    git_branch='master',
    post_base_dir='_posts/',
    asset_base_dir='_assets/',
    asset_base_url='/assets/',
    approved_senders=None
)


def load(file_name):
    # TODO: merge with defaults, do some kind of configuration checking
    file_name = os.path.expanduser(file_name)

    with open(file_name, 'r') as fp:
        return toml.load(fp)
