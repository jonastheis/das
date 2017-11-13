# Distributed Systems Project

## Run

```
$ python server/network/server.py
$ python client/test.py
```

## Known Issues:

```
Exception in thread Thread-2:
Traceback (most recent call last):
  File "/usr/local/Cellar/python/2.7.10_2/Frameworks/Python.framework/Versions/2.7/lib/python2.7/threading.py", line 810, in __bootstrap_inner
    self.run()
  File "/usr/local/Cellar/python/2.7.10_2/Frameworks/Python.framework/Versions/2.7/lib/python2.7/threading.py", line 763, in run
    self.__target(*self.__args, **self.__kwargs)
  File "/Users/Kian/Desktop/VU/P2/DS/assigmnet/client/game.py", line 178, in _emulate
    self.epoch()
  File "/Users/Kian/Desktop/VU/P2/DS/assigmnet/client/game.py", line 61, in epoch
    self.apply_command(command)
  File "/Users/Kian/Desktop/VU/P2/DS/assigmnet/client/game.py", line 91, in apply_command
    if self.map[target_row][target_col] != 0:
IndexError: list index out of range
```

> Probably because move is not checked on boundaries