# Test Targets
from FlagCliAction import FlagAction, FlagGroup
# Test Framework
import unittest

from argparse import ArgumentParser
from enum import Flag, auto

class FlagActionTestCase(unittest.TestCase):
    class TestFlags(Flag):
        FLAG1 = auto()
        FLAG2 = auto()
        FLAG3 = auto()
    def test_basic(self):
        parser = ArgumentParser()
        parser.add_argument('--one', action=FlagAction, const=self.TestFlags.FLAG1)
        parser.add_argument('-t','--two', action=FlagAction, const=self.TestFlags.FLAG2)
        args = parser.parse_args(['--one', '--two'])
        self.assertEqual(args.one, self.TestFlags.FLAG1)
        self.assertEqual(args.two, self.TestFlags.FLAG2)
        self.assertEqual(args.one | args.two, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)
    def test_samedest_1(self):
        parser = ArgumentParser()
        parser.add_argument('--one', action=FlagAction, const=self.TestFlags.FLAG1, dest='flags')
        parser.add_argument('--two', action=FlagAction, const=self.TestFlags.FLAG2, dest='flags')
        args = parser.parse_args(['--one',])
        self.assertEqual(args.flags, self.TestFlags.FLAG1)
    def test_samedest_2(self):
        parser = ArgumentParser()
        parser.add_argument('--one', action=FlagAction, const=self.TestFlags.FLAG1, dest='flags')
        parser.add_argument('--two', action=FlagAction, const=self.TestFlags.FLAG2, dest='flags')
        args = parser.parse_args(['--one', '--two'])
        self.assertEqual(args.flags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)
    def test_repeat(self):
        parser = ArgumentParser()
        parser.add_argument('--one', action=FlagAction, const=self.TestFlags.FLAG1)
        parser.add_argument('--two', action=FlagAction, const=self.TestFlags.FLAG2)
        args = parser.parse_args(['--one', '--two', '--one'])
        self.assertEqual(args.one, self.TestFlags.FLAG1)
        self.assertEqual(args.two, self.TestFlags.FLAG2)
        self.assertEqual(args.one | args.two, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)
    def test_repeat_samedest(self):
        parser = ArgumentParser()
        parser.add_argument('--one', action=FlagAction, const=self.TestFlags.FLAG1, dest='flags')
        parser.add_argument('--two', action=FlagAction, const=self.TestFlags.FLAG2, dest='flags')
        args = parser.parse_args(['--one', '--two', '--one'])
        self.assertEqual(args.flags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)

    def test_sanitytests(self):
        parser = ArgumentParser()
        parser.add_argument('-o', '--one', action=FlagAction, const=self.TestFlags.FLAG1, dest='flags')
        parser.add_argument('-t', action=FlagAction, const=self.TestFlags.FLAG2, dest='flags')
        parser.add_argument('-r', action=FlagAction, const=self.TestFlags.FLAG3, dest='flags')
        args = parser.parse_args(['-o', '-t', '-r'])
        self.assertEqual(args.flags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2 | self.TestFlags.FLAG3)
        args = parser.parse_args(['-o', '-t', '-r', '-o'])
        self.assertEqual(args.flags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2 | self.TestFlags.FLAG3)
        args = parser.parse_args(['-otr'])
        self.assertEqual(args.flags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2 | self.TestFlags.FLAG3)
        args = parser.parse_args(['--one', '-t'])
        self.assertEqual(args.flags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)
        args = parser.parse_args(['-o', '--one', '-t'])
        self.assertEqual(args.flags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)
        args = parser.parse_args(['-tr', '--one'])
        self.assertEqual(args.flags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2 | self.TestFlags.FLAG3)

    def test_different_classes_same_dest_error(self):
        class OtherFlags(Flag):
            FLAG4 = auto()
            FLAG5 = auto()
            FLAG6 = auto()
        parser = ArgumentParser()
        parser.add_argument('--one', action=FlagAction, const=self.TestFlags.FLAG1, dest='flags')
        parser.add_argument('--two', action=FlagAction, const=OtherFlags.FLAG4, dest='flags')
        with self.assertRaises(TypeError):
            parser.parse_args(['--one', '--two'])

class FlagGroupTestCase(unittest.TestCase):
    class TestFlags(Flag):
        FLAG1 = auto()
        FLAG2 = auto()
        FLAG3 = auto()
    class OtherFlags(Flag):
        FLAG4 = auto()
        FLAG5 = auto()
        FLAG6 = auto()
    ## NOTE - The default naming callback results in the following option strings:
    ## -f|--flag1
    ## -l|--flag2
    ## -a|--flag3
    ## -g|--flag4
    ## -5|--flag5
    ## -6|--flag6
    def test_basic(self):
        parser = ArgumentParser()
        FlagGroup(parser, self.TestFlags)
        args = parser.parse_args(['--flag1', '--flag2'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)
    def test_shortnames(self):
        parser = ArgumentParser()
        FlagGroup(parser, self.TestFlags)
        args = parser.parse_args(['-fa',])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG3)
    def test_dest(self):
        parser = ArgumentParser()
        FlagGroup(parser, self.TestFlags, dest='myflags')
        args = parser.parse_args(['--flag1', '--flag2'])
        self.assertEqual(args.myflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)
    def test_name_callback(self):
        parser = ArgumentParser()
        def my_counter(flag: list[Flag], container)-> dict[Flag, list[str]]:
            """ Names flags in ASCII order starting at 'a' """
            out = dict()
            i = 96
            for f in flag:
                i += 1
                out[f] = [f"-{chr(i)}",f"--{f.name.lower() if f.name else f.__name__.lower()}"]
            return out
        FlagGroup(parser, self.TestFlags, name_callback=my_counter)
        args = parser.parse_args(['-ac',])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG3)

    def test_list_of_flags(self):
        parser = ArgumentParser()
        FlagGroup(parser, [self.TestFlags.FLAG1, self.TestFlags.FLAG3])
        args = parser.parse_args(['--flag1'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1)
        args = parser.parse_args(['--flag3'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG3)
        ## Because Flag2 was omitted, -l is assigned to Flag3
        args = parser.parse_args(['-fl'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG3)

        
    def test_multiple_groups(self):
        """ Full Option Strings """
        parser = ArgumentParser()
        FlagGroup(parser, self.TestFlags)
        FlagGroup(parser, self.OtherFlags)
        args = parser.parse_args(['--flag1', '--flag4'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1)
        self.assertEqual(args.otherflags, self.OtherFlags.FLAG4)
    def test_multiple_groups_2(self):
        """ Short names """
        parser = ArgumentParser()
        FlagGroup(parser, self.TestFlags)
        FlagGroup(parser, self.OtherFlags)
        args = parser.parse_args(['-f5'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1)
        self.assertEqual(args.otherflags, self.OtherFlags.FLAG5)

    def test_multiple_groups_same_dest_error(self):
        parser = ArgumentParser()
        FlagGroup(parser, self.TestFlags, dest='flags')
        with self.assertRaises(ValueError):
            FlagGroup(parser, self.OtherFlags, dest='flags')
        

if __name__ == '__main__':
    unittest.main()