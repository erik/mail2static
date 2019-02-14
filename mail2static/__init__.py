import logging

from mail2static import configuration, post, web


def start_server():
    logging.basicConfig(level='DEBUG')

    config = configuration.load()
    manager = post.PostManager(config)

    web.create_app(config, manager)\
       .run(**config.get('http', {}))


if __name__ == '__main__':
    start_server()
