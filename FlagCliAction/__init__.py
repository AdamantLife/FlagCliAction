from argparse import Action, ArgumentParser, HelpFormatter, _ArgumentGroup, SUPPRESS
from enum import EnumType, Flag

class FlagAction(Action):
    """ This class can be used to gather multiple flags into a single Namespace Attribute when an ArgumentParser parses the command line arguments. """
    def __init__(self, *args, nargs=0, help = None, const:Flag|None = None, default:Flag|None = None, **kwargs):
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
        super().__init__(*args, nargs=0, help = help, const = const, default = default, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is None:
            return setattr(namespace, self.dest, self.const)
        value = self.const
        if value is None:
            value = self.default
        setattr(namespace, self.dest, getattr(namespace, self.dest) | self.const)

class FlagClassAction(Action):
    AUTO = "-==AUTO=="
    def __init__(self, option_strings: list[str], dest, nargs=0, flags: list[Flag]|EnumType = [] , **kwargs):
        self.classname = None
        _flags: list[Flag] = []
        if isinstance(flags, EnumType):
            self.classname = flags.__name__
            _flags.extend(list(flags)) ## type: ignore ## Iterating over EnumType is supposed to yield Enum members (Flag is a subclass of Enum), not EnumMeta
        elif isinstance(flags, list) and all([isinstance(flag, Flag) for flag in flags]):
            self.classname = flags[0].__class__.__name__
            _flags.extend(flags)
        else:
            raise ValueError("flags must be a enum.Flag class or a list of Flag members")
        
        self.flags: dict[str, Flag] = dict()
        if not option_strings or option_strings[0] != FlagClassAction.AUTO:
            if len(option_strings) != len(flags):
                raise ValueError("option_strings and flags must be the same length")
            self.flags: dict[str, Flag] = dict(zip(option_strings, _flags))
        else:
            ## afaik Flags need to have a name, but the typechecker says it can be None, so we're checking
            option_strings = [f"--{flag.name.lower()}" for flag in _flags if flag.name]
            self.flags = dict(zip(option_strings, _flags))
            shortstrings = []
            for flag in _flags:
                if not flag.name: continue
                name = flag.name
                while len(name):
                    shortname = f"-{name[0].lower()}"
                    ## Originally we were inserting the shortname into the start of option_strings list
                    ## but that resulted in the shortnames being in the wrong order. We could have kept
                    ## track of the current index, but there didn't seem any particular benefits.
                    if shortname not in option_strings and shortname not in shortstrings:
                        shortstrings.append(shortname)
                        self.flags[shortname] = flag
                        break
                    name = name[1:]
            option_strings = shortstrings + option_strings
                    
        if "help" not in kwargs:
            kwargs["help"] = f"Sets the corresponding Flag from {self.classname}"

        super().__init__(option_strings, dest, nargs = 0, **kwargs)

    def format_usage(self):
        return "-{"+",".join([f[1] for f in self.option_strings if len(f) == 2])+"}"
        

def add_flag_group(parser: ArgumentParser, flags: EnumType|list[Flag|tuple[str, Flag]|tuple[str, str, Flag]], name: str|None = None, description: str|None = None, dest = None, kwargs = {})->_ArgumentGroup:
    """ Provides a convenient method for adding multiple flags to an ArgumentParser using a variety of formats.

    Valid Formats for the flags argument are:
    - A enum.Flag class: Each of its members will be added. Each Member's name attribute will be used as the long name (e.g. "--name"). If there are no collisions with other flags, the short name will be the first letter of the long name (e.g. "-n").
    - A list containg:
        - Flag members: Each of which will be added. The Flag's name attribute will be used as the long name. If there are no collisions with other flags, the short name will be the first letter of the long name.
        - tuples containing a name and a Flag: The name will be used as the long name. If there are no collisions with other flags, the short name will be the first letter of the long name.
        - tuples containing a short name, a long name, and a Flag: short name must be a single character. Results in add_argument("-s", "--long-name", ...etc).
    
    Args:
        parser (ArgumentParser): The ArgumentParser object to add the flags to.
        flags (EnumType|list[Flag]|list[tuple[str, Flag]]|list[tuple[str, str, Flag]]): The flags to add to the parser. This can be a enum.Flag class, a list of Flag members, or a list containing a tuple of (name, flag) or (shortname, long_name, flag).
        name (str, optional): The name of the group. Defaults to None.
        description (str, optional): The description of the group. Defaults to None.
        dest (str, optional): The destination attribute to store the flags. If not provided, the destination will be the lower case name of the flag class. Defaults to None.
        kwargs (dict, optional): Additional keyword arguments to pass to the add_argument_group method. Defaults to {}.

    Returns:
        _ArgumentGroup: The group that was added to the parser.
    """
    args = []
    if name:
        args.append(name)
    if description:
        args.append(description)
    group = parser.add_argument_group(*args, **kwargs)
    if isinstance(flags, EnumType):
        flags = list(flags) ## type: ignore ## Iterating over EnumType is supposed to yield Enum members (Flag is a subclass of Enum), not EnumMeta
    if not isinstance(flags, list):
        raise TypeError("flags must be a enum.Flag class or a list of Flag members")
    
    ## Documenting without importing TypedDict
    ## class Setup(TypedDict):
    ##    shortname: str
    ##    shortsupplied: bool
    ##    longname: str
    ##    flag: Flag
    ##    dest: str
    
    groupdata = list() ## type: list[Setup]

    for flag in flags:
        _flag = dict() ## type: Setup
        groupdata.append(_flag)

        if isinstance(flag, Flag):
            if not flag.name:
                raise ValueError("Flag must have a name")
            _flag["shortname"] = f"-{flag.name[0].lower()}"
            _flag["shortsupplied"] = False
            _flag["longname"] = f"--{flag.name.lower()}"
            _flag["flag"] = flag
            _flag["dest"] = dest or flag.__class__.__name__.lower()
        elif isinstance(flag, tuple) and len(flag) == 2:
            name, flag = flag
            if not name:
                raise ValueError("Flag must have a name")
            _flag["shortname"] = f"-{name[0].lower()}"
            _flag["shortsupplied"] = False
            _flag["longname"] = f"--{name}"
            _flag["flag"] = flag
            _flag["dest"] = dest or flag.__class__.__name__.lower()
        elif isinstance(flag, tuple) and len(flag) == 3:
            shortname, long_name, flag = flag
            if len(shortname) != 1:
                raise ValueError("Short flag must be a single character")
            if not long_name:
                raise ValueError("When specifying a long name, it must not be empty")
            _flag['shortname'] = f"-{shortname}"
            _flag['shortsupplied'] = True
            _flag['longname'] = f"--{long_name}"
            _flag["flag"] = flag
            _flag["dest"] = dest or flag.__class__.__name__.lower()
        else:
            raise ValueError("flags must be a Flag Subclass, a list of Flags, or a list containing a tuple of (name, flag) or (name, long_name, flag)")

    flagcount = len(groupdata)
    if (shorterror := len(set([flag["shortname"] for flag in groupdata])) < flagcount) and all([flag["shortsupplied"] for flag in groupdata]):
        raise ValueError("Shortnames must be unique")
    ## Because shortnames are optional, we can attempt to troubleshoot this error
    elif shorterror:
        duplicates = dict() ## type: dict[str, Setup]
        for data in groupdata:
            if data["shortname"] in duplicates:
                if duplicates[data["shortname"]]['shortsupplied']:
                    ## If both shortnames are supplied, raise an error
                    if data['shortsupplied']:
                        raise ValueError("Shortnames must be unique")
                    ## Otherwise, remove the shortname from this entry
                    data['shortname'] = ""
                ## If this shortname is supplied, remove the shortname from the duplicate and replace it
                elif data['shortsupplied']:
                    duplicates[data["shortname"]]['shortname'] = ""
                    duplicates[data["shortname"]] = data
                ## Not other[supplied] and Not data[supplied]
                ## So remove the shortname from both
                else:
                    data['shortname'] = ""
                    duplicates[data["shortname"]] = data
                    ## We're keeping the original data in the duplicates list
                    ## in case there is another duplicate                    
            else:
                duplicates[data["shortname"]] = data
    ## There's no troubleshooting we can do for this error because longnames are not optional
    if  len(set([flag["longname"] for flag in groupdata])) < flagcount:
        raise ValueError("Longnames must be unique")

    for data in groupdata:
        nameargs = []
        if data['shortname']:
            nameargs.append(data['shortname'])
        nameargs.append(data['longname'])
        print(f"Adding {nameargs} to {data['dest']}")
        group.add_argument(*nameargs, action=FlagAction, dest=data['dest'], const=data['flag'], help=SUPPRESS)
    return group

class FlagHelpFormatter(HelpFormatter):
    def _format_action_invocation(self, action):
        if isinstance(action, FlagClassAction):
            singles = [f[1] for f in action.option_strings if len(f) == 2]
            longs = [f[2:] for f in action.option_strings if len(f) > 2]
            return "-"+"|".join(singles)+", --"+"|".join(longs)
        return super()._format_action_invocation(action)

if __name__ == "__main__":
    import enum

    class MyFlags(enum.Flag):
        A = enum.auto()
        B = enum.auto()
        C = enum.auto()

    import argparse
    parser = argparse.ArgumentParser(formatter_class=FlagHelpFormatter)

    ## Flag Actions
    # parser.add_argument("-a", action=FlagAction, dest="flags", const=MyFlags.A)
    # parser.add_argument("-b", action=FlagAction, dest="flags", const=MyFlags.B)
    # parser.add_argument("-c", action=FlagAction, dest="flags", const=MyFlags.C)

    ## Flag Class Action
    # parser.add_argument(FlagClassAction.AUTO, action=FlagClassAction, dest="flags", flags=MyFlags)

    ## Flag Group
    add_flag_group(parser, MyFlags, "Flags", "Flags for the program")

    ## Group of Flags
    # group = parser.add_argument_group("Flags", "Flags for the program")
    # group.add_argument("-a", action=FlagAction, dest="flags", const=MyFlags.A)
    # group.add_argument("-b", action=FlagAction, dest="flags", const=MyFlags.B)
    # group.add_argument("-c", action=FlagAction, dest="flags", const=MyFlags.C)


    parser.print_help()
    print(parser.parse_args(["-a"]))
    