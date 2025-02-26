from argparse import Action

class FlagAction(Action):
    def __init__(self, *args, nargs=0, **kwargs):
        ## nargs needs to be set to 0 to prevent argparse from consuming the next argument
        super().__init__(*args, nargs=nargs, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is None:
            return setattr(namespace, self.dest, self.const)
        setattr(namespace, self.dest, getattr(namespace, self.dest) | self.const)