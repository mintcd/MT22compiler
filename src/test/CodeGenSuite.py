import unittest
from TestUtils import TestCodeGen
from AST import *


import unittest
from TestUtils import TestCodeGen
from AST import *


class CheckCodeGenSuite(unittest.TestCase):
    def test_int(self):
        """Simple program: int main() {} """
        input = """void main() {putFloat(10.1);}"""
        expect = "10.1"
        self.assertTrue(TestCodeGen.test(input,expect,500))
    def test_int_ast(self):
        input =  Program([FuncDecl("main",VoidType(),[],None,BlockStmt([FuncCall("putInt",[IntegerLit(5)])]))])  
        expect = "5"
        self.assertTrue(TestCodeGen.test(input,expect,501))
    def test_int_1(self):
        input = """void main() {putInt(2+9+1);}"""
        expect = "12"
        self.assertTrue(TestCodeGen.test(input,expect, 502))
    def test_float_2(self):
        input = """void main() {putFloat(2+9.1);}"""
        expect = "11.1"
        self.assertTrue(TestCodeGen.test(input,expect, 503))