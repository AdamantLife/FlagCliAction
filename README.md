# FlagCliAction

While the `Flag` class from the `enum` module is very useful, it doesn't play well with `argparse` out of the box.
This module includes several utilities for working with `Flags` in `argparse`.

### Install
```
pip install git+https://github.com/AdamantLife/FlagCliAction.git
```

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

### Adding Multiple Flags at Once
The module also provides `add_flag_group()` which can be used to more simply add `Flags`.
```python
class MyOtherFlags(Flag):
    Delta = auto()
    Echo = auto()
    Foxtrot = auto()

parser = ArgumentParser()
add_flag_group(parser, MyOtherFlags)
parser.print_help()
# > usage: __init__.py [-h] [-d] [-e] [-f]
# >
# > options:
# >   -h, --help     show this help message and exit
# >
# >   -d, --delta    Sets the flag MyOtherFlags.Delta
# >   -e, --echo     Sets the flag MyOtherFlags.Echo
# >   -f, --foxtrot  Sets the flag MyOtherFlags.Foxtrot

parser.parse_args(["-de",])
# > Namespace(myotherflags=<MyOtherFlags.Delta|Echo: 3>)
```

`add_flag_group()` can handle other input formats which can be used to customize the argument names (such as to avoid name collisions), use subsets of flags, or to include `Flags` from different Classes (though it is an error to assign `Flags` from different classes to the same `dest` since they cannot be `|` OR'd).

### Adapting the Usage/Help Results
The basic example has the following usage description:
```
usage: __init__.py [-h] [-a] [-b]

options:
  -h, --help  show this help message and exit
  -a, --one   Sets the flag MyFlags.A        
  -b          Sets the flag MyFlags.B        
```
This can be improved by using an argument group and supplying a name (and optionally description) or by using `add_flag_group()` and likewise assigning the `name` and `description` arguments.
```python
parser = ArgumentParser()
flaggroup = parser.add_argument_group("MyFlags", "MyFlags for Doing Things")
flaggroup.add_argument('-a', "--one", action=FlagAction, const=MyFlags.A, dest="flags")
flaggroup.add_argument('-b', action=FlagAction, const=MyFlags.B, dest="flags")
parser.print_help()
# > usage: __init__.py [-h] [-a] [-b]
# >
# > options:
# >   -h, --help  show this help message and exit
# >
# > MyFlags:
# >   MyFlags for Doing Things
# >
# >   -a, --one   Sets the flag MyFlags.A
# >   -b          Sets the flag MyFlags.B
```

### Alternative
If you don't want to go through the trouble of adding an additional abstraction, one alternative is to use the `choices` and `nargs` argument and convert the result to `Flags` afterwards.

```python
parser = argparse.ArgumentParser()
parser.add_argument("test")
parser.add_argument("-f", "--flag", choices = ["a", "b", "c"], nargs="*",  default= [], help="MyFlags to set")

args = parser.parse_args("test -f a b".split())

flags = MyFlags(0)
for flag in args.flag:
    if flag == "a":
        flags |= MyFlags.A
    elif flag == "b":
        flags |= MyFlags.B
    elif flag == "c":
        flags |= MyFlags.C
    else:
        ## This should never happen
        raise ValueError(f"Unknown flag {flag}")
print(flags)
# > MyFlags.A|B
```
Note that all positional arguments (e.g.- *test*) ***must*** appear before any `nargs="*"|"+"` arguments. e.x.- `python mytest.py -f a b test` throws the error:

`mytest.py: error: argument -f/--flag: invalid choice: 'test' (choose from 'a', 'b', 'c')` 

You should probably include the `default=[]` argument so you don't need to test the `Namespace` value.