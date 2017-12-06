import logging
import os


class ACTIONS:
    MOVE = 'move'
    HEAL = 'heal'
    ATTACK = 'attack'

class DIRECTIONS:
    H = 'h'
    V = 'v'

class TRANSPORT:
    host = '0.0.0.0'
    port = 8000
    UDP_DELAY_PER_PLAYER = .001

class USERS:
    PLAYER = 'p'
    DRAGON = 'd'

class GLOBAL :
    MAX_LOG_LENGTH = -1

class MSG_TYPE:
    COMMAND = 'cmd'
    INIT = 'init'
    EXIT = 'exit'
    BCAST = 'bc'
    HBEAT = 'hb'

    INIT_REQ = 'init_req'
    INIT_RES = 'init_res'

    PING = 'ping'

    LOG = 'log_req'

class HEARTBEAT:
    INIT = 30
    INC = 10

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

game_file = None

def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[1].levelno
        if(levelno>=50):
            color = '\x1b[31m' # red
        elif(levelno>=40):
            color = '\x1b[31m' # red
        elif(levelno>=30):
            color = '\x1b[33m' # yellow
        elif(levelno >= 20):
            color = '\x1b[32m' # green
        elif(levelno>=10):
            color = '\x1b[94m' # pink
        else:
            color = '\x1b[0m' # normal
        args[1].levelname = color + args[1].levelname +  '\x1b[0m'  # normal
        args[1].name = '.'.join([bcolors.BOLD + args[1].name.split(".")[0] + bcolors.ENDC] + args[1].name.split(".")[1:])
        #print "after"
        return fn(*args)
    return new

def init_logger(file, separate_game_log=True, log_lvl=10):
    global game_file
    # Two base logger types
    sysLogger = logging.getLogger("sys")
    gameLogger = logging.getLogger("game")

    logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)

    #If log directory doesn't exist creates it
    dirname = os.path.dirname(file)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # clear contents from previous run
    open(file, 'w').close()

    fileHandler = logging.FileHandler(file)
    formatter = logging.Formatter(bcolors.HEADER + '%(asctime)s' + bcolors.ENDC + ' ' + bcolors.UNDERLINE + '%(name)s' + bcolors.ENDC + ' ' + bcolors.BOLD + ' %(levelname)s' + bcolors.ENDC + ' :: %(message)s')
    fileHandler.setFormatter(formatter)

    sysLogger.addHandler(fileHandler)
    sysLogger.setLevel(log_lvl)
    sysLogger.addHandler(fileHandler)

    gameLogger.setLevel(log_lvl)
    if separate_game_log:
        game_file = file.split(".")[0] + "_game.log"
        open(game_file, 'w').close()
        gameFileHandler = logging.FileHandler(game_file)
        gameFileHandler.setFormatter(formatter)
        gameLogger.addHandler(gameFileHandler)

    else:
        gameLogger.addHandler(fileHandler)

    sysLogger.info("System Logger initialized")
    sysLogger.info("Game Logger initialized")

def get_game_log():
    with open(game_file) as gf:
        logs = gf.read()
        return logs

def set_game_log(log):
    with open(game_file, 'w') as gf:
        logging.getLogger("sys").info("Previous game logs written to {}".format(game_file))
        gf.write(log)