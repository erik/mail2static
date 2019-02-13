import logging
import os

from mail2static import configuration, post, web


def start_server():
    # TODO: this sucks
    config_file = os.environ.get(
        'MAIL2STATIC_CONFIG',
        './mail2static.toml'
    )

    logging.basicConfig(level='DEBUG')

    config = configuration.load(config_file)
    manager = post.PostManager(config)

    web.create_app(config, manager)\
       .run(**config.get('http', {}))


if __name__ == '__main__':
    start_server()
