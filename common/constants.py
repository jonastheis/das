import logging

class ACTIONS:
    MOVE = 'move'
    HEAL = 'heal'
    ATTACK = 'attack'

class DIRECTIONS:
    H = 'h'
    V = 'v'

class TRANSPORT:
    host = 'localhost'
    port = 8081

class USERS:
    PLAYER = 'p'
    DRAGON = 'd'


logger = logging.getLogger()

def init_logger(file):
    # clear contents from previous run
    open(file, 'w').close()

    handler = logging.FileHandler(file)

    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.debug("Logger initialized")
