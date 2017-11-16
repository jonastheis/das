import client.game
import client.user
import client.command
import sys
from common.constants import USERS

g = client.game.Game()


h = client.user.User(USERS.PLAYER)
h1 = client.user.User(USERS.PLAYER)
g.add_user(h, 0, 0)
g.add_user(h1, 2, 0)
d = client.user.User(USERS.DRAGON)
g.add_user(d, 1, 0)


g.commands = [
    client.command.MoveCommand(h.id, 1, 'h'),
    client.command.AttackCommand(h.id, d.id),
    client.command.AttackCommand(d.id, h1.id),
    client.command.MoveCommand(h.id, 1, 'h'),
    client.command.HealCommand(h.id, h1.id)
]
try:
    # g.emulate_all()
    g._simulate(1)
    g.emulate(5)

except KeyboardInterrupt:
    sys.exit()