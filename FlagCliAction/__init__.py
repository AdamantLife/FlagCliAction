from argparse import Action, _ArgumentGroup, _ActionsContainer
from enum import Flag
from typing import Callable

def make_flag_names(flags: list[Flag], container: _ActionsContainer)->dict[Flag, list[str]]:
    names = {flag: [f"--{flag.name.lower()}",] for flag in flags if flag.name}
    if any(names[0] in container._option_string_actions for names in names.values()):
        raise ValueError("Flag names must be unique")
    shortnames = {}
    for flag in flags:
        if not flag.name: continue
        name = flag.name
        while len(name):
            shortname = f"-{name[0].lower()}"
            if shortname not in shortnames and shortname not in container._option_string_actions:
                shortnames[shortname] = flag
                break
            name = name[1:]
        if not name:
            break
    if len(shortnames) == len(names):
        for shortname, flag in shortnames.items():
            names[flag].insert(0,shortname)
    return names

class FlagGroup(_ArgumentGroup):
    def __init__(self, container: _ActionsContainer, flags:type[Flag]|list[Flag], title: str|None=None, description: str|None=None, dest:str|None = None, name_callback: Callable[[list[Flag], _ActionsContainer],dict[Flag,list[str]]] = make_flag_names, **kwargs):
        if isinstance(flags, list):
            if not all(f.__class__ is flags[0].__class__ for f in flags):
                raise ValueError("Flags must all be of the same type")
        flags = list(flags)
        if title is None:
            title = flags[0].__class__.__name__
        if description is None:
            description = f"Flags for the {title} class"
        super().__init__(container, title=title, description=description, **kwargs)
        container._action_groups.append(self)
        self.flags = flags
        flagnames = name_callback(list(flags), container)
        if dest is None:
            dest = flags[0].__class__.__name__.lower()
        for action in container._actions:
            if action.dest == dest:
                otherflag = action.const or action.default
                if otherflag.__class__ is not flags:
                    raise ValueError(f"FlagGroup {title} conflicts with existing dest {dest} for {otherflag.__class__}")

        first = None
        for flag in self.flags:
            names = flagnames[flag]
            faction = self.add_argument(*names, action=FlagAction, dest=dest, const=flag)
            if first is None:
                first = faction
                fnames = [f[0].lstrip("-") for f in flagnames.values()]
                fstring = "-"+"|".join(fnames)
                faction.format_usage = lambda: fstring
            else: faction.format_usage = lambda: ""

class FlagAction(Action):
    """ This class can be used to gather multiple flags into a single Namespace Attribute when an ArgumentParser parses the command line arguments. """
    def __init__(self,dest, nargs=0, help = None, const:Flag|None = None, default:Flag|None = None, option_strings: list[str] = [], **kwargs):
        ## This class allows const or default to be used to set the value of the flag
        value = const
        if value is None:
            value = default
        if value is None:
            raise ValueError("const or default must be set")
        ## Default help message
        if help is None:
            help = f"Sets the flag {value}"
        ## nargs needs to be set to 0 to prevent argparse from consuming the next argument
        super().__init__(nargs=0, help = help, const = const, default = default, dest=dest, option_strings=option_strings, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is None:
            return setattr(namespace, self.dest, self.const)
        value = self.const
        if value is None:
            value = self.default
        setattr(namespace, self.dest, getattr(namespace, self.dest) | self.const)

if __name__ == "__main__":
    import enum

    class MyFlags(Flag):
        Flag1 = enum.auto()
        Flag2 = enum.auto()
        Flag3 = enum.auto()
    class OtherFlags(Flag):
        FLAG4 = enum.auto()
        FLAG5 = enum.auto()
        FLAG6 = enum.auto()

    import argparse
    parser = argparse.ArgumentParser()

    group = FlagGroup(parser, MyFlags)
    group2 = FlagGroup(parser, OtherFlags)


    parser.print_help()
    print(parser.parse_args(["-fl6"]))