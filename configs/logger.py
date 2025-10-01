import logging


def config_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# Logger root
logger = logging.getLogger()
