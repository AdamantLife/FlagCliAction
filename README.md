# FlagCliAction

While the `Flag` class from the `enum` module is very useful, it doesn't play well with `argparse` out of the box.
This module includes utilities for working with `Flags` in `argparse`.

### Install
```
pip install git+https://github.com/AdamantLife/FlagCliAction.git
```

### Usage
Individual `Flags` are typically not used in isolation; instead they're combined with others from their Flag Type. For this reason you'll typically use the `FlagGroup` class to add them to the commandline parser.
```python
class BurgerCondiments(Flag):
    Pickle = auto()
    Tomato = auto()
    Lettuce = auto()
    Mayo = auto()
    Ketchup = auto()
    Mustard = auto()

burgerparser = argparse.ArgumentParser()

group = FlagGroup(burgerparser, BurgerCondiments)

parsed = burgerparser.parse_args(["--tomato",]).burgercondiments
BurgerCondiments.Tomato in parsed
# > True
```

By default `Flags` are stored under their Class' lowercased name (using `.lower()`). `FlagGroup` will also provide a shortform option string to make it easier to combine them.
```python
burgerparser.parse_args(["-plm",]).burgercondiments
# > BurgerCondiments.Pickle|Lettuce|Mayo

## Because Mayo and Mustard both start with "M",
## Mustard is stored under its second character

burgerparser.parse_args(["-u",]).burgercondiments
# > BurgerCondiments.Mustard
```

`FlagGroup` also accepts a list of `Flags` instead of a `FlagType` (the `enum.Flag` subclass which was created). This is useful if you only want to expose a subset of the available `Flags`

```python
BC = BurgerCondiments

myresturaunt = argparse.ArgumentParser()
myburgers = FlagGroup(myresturaunt, [BC.Pickles, BC.Mayo, BC.Ketchup, BC.Mustard])

## Note that the Flags are still stored under their class name
## this can be changed by explicitly setting the "dest" parameter

myresturaunt.parse_args(["-PKU",]).burgercondiments
# > BurgerCondiments.Pickles|Ketchup|Mustard
```

When initialized `FlagGroup` adds the individual `Flags` using the `FlagAction` class. If you find it necessary, `FlagActions` can be added directly.
```python
## dest must be set explicitly to group Flags, otherwise add_argument
## will assign their dest based on the option strings
## (e.g.- parsedargs.mustard)
parser.add_argument("-m", "--mustard", action= FlagAction, const= BurgerCondiments.Mustard, dest="mycondiments")

## IMO the Action.const attribute seems to be more idiomatic, but
## on initialization FlagAction will also check the "default" parameter
## if const is not set
parser.add_argument("-a", "--mayo", action= FlagAction, default= Burgercondiments.Mayo, dest="mycondiments")

parser.parse_args(["-ma",]).mycondiments
# > BurgerCondiments.Mayo|Mustard
```

## Additional Notes
* `FlagGroup` is preferred over using the `FlagAction` class directly because it makes the `--help/usage` output prettier.

* `FlagGroup` can accept a callback for generating option strings via the `name_callback` parameter; the callback should match `Callable[ [list[Flag], _ActionsContainer ] , dict[ Flag, list[str] ] ]`.

* Unlike `_ActionsContainer.add_argument()` (superclass of `ArgumentParser`), the `add_argument_group()` method does not allow for a custom subclass which is why `FlagGroup` adds itself to the parser when initialized.

* If providing `FlagGroup` with a list of `Flags`, all `Flags` must be of the same `FlagType`.

* If adding `FlagActions` individually, `Flags` from different `FlagTypes` must be assigned to different `dest` (Namespace attributes). `A.foo | B.bar` would raise a `TypeError`.

* *Historical note*- Originally I wrote this as a simple howto for implementing an `Action` subclass to handle `Flags` and showing a couple of different patterns for working with them. After using them more I decided to reorganize the repository as an actual module with a higher-level interface. I'm pretty sure I cleared out all the anachronisms, but if you see anything that seems to have been orphaned from the original project, let me know.