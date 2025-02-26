# FlagCliAction

While the `Flag` class from the `enum` module is very useful, it doesn't play well with `argparse` out of the box. This module shows how to implement a simple `Action` class to allow your `argparse` Command-line programs to utilize `Flags`.

### Install
The class is simple enough that it's more practical to copy/paste it into your code, but if you want to install it as a module you can run:
```
pip install git+https://github.com/AdamantLife/FlagCliAction.git
````

### Usage
Typical usage requires you to provide the following three arguments to `parser.add_argument()`:

1) `action = FlagAction`- Use `FlagAction` as the callback when the flag's token is parsed
2) `dest = "flags"`- Gathers all the flags in the same `Namespace` attribute (can be whatever name you want to use)
3)  `const = {MyFlagMember}`- The flag to set when this argument is parsed
```python
class MyFlags(Flag):
    A = auto()
    B = auto()

parser = ArgumentParser()
parser.add_argument('-a', "--one", action=FlagAction, const=MyFlags.A, dest="flags")
parser.add_argument('-b', action=FlagAction, const=MyFlags.B, dest="flags")

parser.parse_args(['--one',])
# > Namespace(flags=MyFlags.A)
parser.parse_args(['-b',])
# > Namespace(flags=MyFlags.B)
parser.parse_args(['-a', '-b'])
# > Namespace(flags=MyFlags.A|MyFlags.B)
parser.parse_args(['-ba',])
# > Namespace(flags=MyFlags.A|MyFlags.B)
```
