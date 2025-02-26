# Test Target
from FlagCliAction import FlagAction
# Test Framework
import unittest

from argparse import ArgumentParser
from enum import Flag, auto

class TestCase(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()