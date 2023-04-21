import unittest
from TestUtils import TestChecker
from AST import *

class CheckerSuite(unittest.TestCase):
    def test_TypeMismatchInSTMT_for1(self):
        """test_TypeMismatchInBinExp_REMAINDER""" 
        # OPERAND TYPE: INT
        input = """
            main: function void () {
                x : integer = 2.5;
        }"""
        expect = "Type mismatch in Variable Declaration: VarDecl(x, IntegerType, FloatLit(2.5))"
        self.assertTrue(TestChecker.test(input, expect, 4000))  # your code goes here