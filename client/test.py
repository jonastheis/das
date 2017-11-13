import game
import user
import command
import sys


g = game.Game()

h = user.User("p")
h1 = user.User("p")
g.add_user(h, 0, 0)
g.add_user(h1, 2, 0)
d = user.User("d")
g.add_user(d, 1, 0)


g.commands = [
    command.MoveCommand(h.id, 1, 'h'),
    command.AttackCommand(h.id, d.id),
    command.AttackCommand(d.id, h1.id),
    command.MoveCommand(h.id, 1, 'h'),
    command.HealCommand(h.id, h1.id)
]
try:
    g.emulate_all()
    # g._simulate(100)
    # g.emulate(1)

except KeyboardInterrupt:
    sys.exit()