import logging

VERSION = '0.0.1'

logger = None
if not logger:
    logger = logging.getLogger(name='varan')
    logger.propagate = False
    # default behavior is to log on console
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] %(message)s'))
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
