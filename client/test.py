import game
import user


g = game.Game()

h = user.Player("p")
h1 = user.Player("p")
g.add_user(h, 0, 0)
g.add_user(h1, 2, 0)
d = user.Player("d")
g.add_user(d, 1, 0)


g.commands = [
    {'type': 'move', 'direction': 'h', 'value': 1, 'user': h.id},
    {'type': 'attack', 'target': d.id, 'user': h.id},
    {'type': 'attack', 'target': h1.id, 'user': d.id},
    {'type': 'move', 'direction': 'h', 'value': 1, 'user': h.id},
    {'type': 'heal', 'target': h1.id, 'user': h.id}
]

g._simulate(100)
g.emulate(.5)
