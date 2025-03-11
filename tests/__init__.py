# Test Targets
from typing import NoReturn
from FlagCliAction import FlagAction, add_flag_group
# Test Framework
import unittest

from argparse import ArgumentParser, ArgumentError
from enum import Flag, auto

class FlagActionTestCase(unittest.TestCase):
    class TestFlags(Flag):
        FLAG1 = auto()
        FLAG2 = auto()
        FLAG3 = auto()
    def test_basic(self):
        parser = ArgumentParser()
        parser.add_argument('--one', action=FlagAction, const=self.TestFlags.FLAG1)
        parser.add_argument('--two', action=FlagAction, const=self.TestFlags.FLAG2)
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

class AddFlagGroupTestCase(unittest.TestCase):
    class TestFlags(Flag):
        FLAG1 = auto()
        FLAG2 = auto()
        FLAG3 = auto()
    class OtherFlags(Flag):
        FLAG4 = auto()
        FLAG5 = auto()
        FLAG6 = auto()
    def test_basic(self):
        parser = ArgumentParser()
        add_flag_group(parser, self.TestFlags, dest='flags')
        args = parser.parse_args(['--flag1', '--flag2'])
        self.assertEqual(args.flags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)
    def test_dest(self):
        parser = ArgumentParser()
        add_flag_group(parser, self.TestFlags, dest='myflags')
        args = parser.parse_args(['--flag1', '--flag2'])
        self.assertEqual(args.myflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)
    def test_nodest(self):
        parser = ArgumentParser()
        add_flag_group(parser, self.TestFlags)
        args = parser.parse_args(['--flag1', '--flag2'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)
    def test_list_flags(self):
        parser = ArgumentParser()
        add_flag_group(parser, [self.TestFlags.FLAG1, self.TestFlags.FLAG3])
        args = parser.parse_args(['--flag1', '--flag3'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG3)
    def test_list_name_flag_tuples(self):
        parser = ArgumentParser()
        add_flag_group(parser, [('flag1', self.TestFlags.FLAG1), ('flag3', self.TestFlags.FLAG3)])
        args = parser.parse_args(['--flag1', '--flag3'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG3)
    def test_list_short_long_flag_tuples(self):
        parser = ArgumentParser()
        add_flag_group(parser, [('o', 'flag1', self.TestFlags.FLAG1), ('t', 'flag2', self.TestFlags.FLAG2)])
        for test, result in [
            (['-o', '--flag2'], self.TestFlags.FLAG1 | self.TestFlags.FLAG2),
            (['-ot'], self.TestFlags.FLAG1 | self.TestFlags.FLAG2)]:
            with self.subTest(test=test, result=result):
                args = parser.parse_args(test)
                self.assertEqual(args.testflags, result)
    def test_overlapping_shortnames(self):
        parser = ArgumentParser()
        add_flag_group(parser, [('flag1', self.TestFlags.FLAG1), ('f', 'flag2', self.TestFlags.FLAG2)])
        args = parser.parse_args(['--flag1', '-f'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2)
        args = parser.parse_args(['-f', '--flag2'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG2)
    def test_overlapping_shortnames_2(self):
        parser = ArgumentParser()
        add_flag_group(parser, [self.TestFlags.FLAG1, ('f', 'flag3', self.TestFlags.FLAG3)])
        args = parser.parse_args(['--flag1', '-f'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG3)
        args = parser.parse_args(['-f', '--flag3'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG3)
    def test_mixed_flag_classes_same_dest(self):
        parser = ArgumentParser()
        add_flag_group(parser, [self.TestFlags.FLAG1, self.OtherFlags.FLAG4], dest = "allflags")
        for test, result in [
            (['--flag1'], self.TestFlags.FLAG1),
            (['--flag4'], self.OtherFlags.FLAG4)]:
            with self.subTest(test=test, result=result):
                args = parser.parse_args(test)
                self.assertEqual(args.allflags, result)
    def test_mixed_flag_classes_no_dest(self):
        parser = ArgumentParser()
        add_flag_group(parser, [self.TestFlags.FLAG1, self.OtherFlags.FLAG4])
        for test, attr, result in [
            (['--flag1'], "testflags", self.TestFlags.FLAG1),
            (['--flag4'], "otherflags", self.OtherFlags.FLAG4)]:
            with self.subTest(test=test, attr= attr, result=result):
                args = parser.parse_args(test)
                self.assertEqual(getattr(args, attr), result)


    ## Bad Tests
    def test_bad_longnames_flags(self):
        parser = ArgumentParser()
        with self.assertRaises(ValueError):
            add_flag_group(parser, [self.TestFlags.FLAG1, self.TestFlags.FLAG1])
    def test_bad_longnames_tuples(self):
        parser = ArgumentParser()
        with self.assertRaises(ValueError):
            add_flag_group(parser, [('flag1', self.TestFlags.FLAG1), ('flag1', self.TestFlags.FLAG2)])
    def test_bad_shortnames(self):
        parser = ArgumentParser()
        with self.assertRaises(ValueError):
            add_flag_group(parser, [('o', 'flag1', self.TestFlags.FLAG1), ('o', 'flag2', self.TestFlags.FLAG2)])
    def test_mixed_flag_classes_same_dest_bad(self):
        parser = ArgumentParser()
        add_flag_group(parser, [self.TestFlags.FLAG1, self.OtherFlags.FLAG4], dest = "allflags")
        ## The TypeError is actually raised because "unsupported operand type(s) for |: 'TestFlags' and 'OtherFlags'"
        ## Different Flag classes cannot have boolean operations performed on them
        with self.assertRaises(TypeError):
            parser.parse_args(['--flag1', '--flag4'])

    ## Multiple Calls
    def test_mulitple_calls(self):
        parser = ArgumentParser()
        add_flag_group(parser, [('o', 'flag1', self.TestFlags.FLAG1), ('t', 'flag2', self.TestFlags.FLAG2)])
        add_flag_group(parser, [('r', 'flag3', self.TestFlags.FLAG3)])
        args = parser.parse_args(['-otr'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG2 | self.TestFlags.FLAG3)
    def test_multiple_calls_2(self):
        parser = ArgumentParser()
        add_flag_group(parser, [('o', 'flag1', self.TestFlags.FLAG1), ('t', 'flag2', self.TestFlags.FLAG2)])
        add_flag_group(parser, [self.TestFlags.FLAG3,])
        args = parser.parse_args(['-o', '--flag3'])
        self.assertEqual(args.testflags, self.TestFlags.FLAG1 | self.TestFlags.FLAG3)
    def test_multiple_calls_bad_shortnames(self):
        parser = ArgumentParser()
        add_flag_group(parser, [('o', 'flag1', self.TestFlags.FLAG1), ('t', 'flag2', self.TestFlags.FLAG2)])
        ## When multiple calls are made, the error is actually caught by the ArgumentParser
        with self.assertRaises(ArgumentError):
            add_flag_group(parser, [('o', 'flag3', self.TestFlags.FLAG3)])
    def test_multiple_calls_bad_longnames(self):
        parser = ArgumentParser()
        add_flag_group(parser, [('o', 'flag1', self.TestFlags.FLAG1), ('t', 'flag2', self.TestFlags.FLAG2)])
        ## When multiple calls are made, the error is actually caught by the ArgumentParser
        with self.assertRaises(ArgumentError):
            add_flag_group(parser, [('r', 'flag1', self.TestFlags.FLAG3)])


if __name__ == '__main__':
    unittest.main()