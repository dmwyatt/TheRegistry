Basic Usage
-----------
```python
from the_registry import RegistryHkey
r = Registry('HKEY_LOCAL_MACHINE')

# Get all the named values as a dictionary
values = r.get_values(r'SOFTWARE\EA Games\Battlefield 4')
```
```python
from the_registry import RegistryHkey
r = Registry('HKEY_LOCAL_MACHINE')

# Add a value
r.set_value(r'SOFTWARE\EA Games\Battlefield 4', 'my_key', 'is now set to this value')
r.set_value(r'this\is\a\custom\path', 'my_key', 'we automatically created the specified path')
```

64 bit OS, 32 bit Python
------------------------
I don't claim to understand exactly what goes on with the registry, but I do know that if you're running 32-bit
python on 64-bit Windows some different things can happen.

```python
from the_registry import RegistryHkey
r = Registry('HKEY_LOCAL_MACHINE')

# Add a value
r.set_value(r'SOFTWARE\this\is\a\custom\path', 'my_key', 'we automatically created the specified path')
```
Surprisingly, the above doesn't create `SOFTWARE\this\is\a\custom\path` if you're using a 32 bit
python on a 64 bit Windows.  It actually creates `SOFTWARE\Wow6432Node\this\is\a\custom\path`.  If this is
unacceptable to you, do this:

```python
from the_registry import RegistryHkey
r = Registry('HKEY_LOCAL_MACHINE')
r.arch64 = True  # This line opens the key in 64-bit view

# Add a value
r.set_value(r'SOFTWARE\this\is\a\custom\path', 'my_key', 'we automatically created the specified path')
```
