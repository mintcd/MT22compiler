import unittest
from TestUtils import TestCodeGen
from AST import *


class CheckCodeGenSuite(unittest.TestCase):
    def test_float1(self):
        """Simple program: int main() {} """
        input = """main : function void () {putFloat(1.23);}"""
        expect = "1.23"
        self.assertTrue(TestCodeGen.test(input,expect,500))
    def test_int1(self):
        input =  Program([FuncDecl("main",VoidType(),[],None,BlockStmt([FuncCall("putInt",[IntegerLit(5)])]))])  
        expect = "5"
        self.assertTrue(TestCodeGen.test(input,expect,501))
    def test_int2(self):
        input = """void main() {putInt(1+2+3);}"""
        expect = "6"
        self.assertTrue(TestCodeGen.test(input,expect, 502))
    def test_floatint(self):
        input = """void main() {putFloat(1.2+3);}"""
        expect = "4.2"
        self.assertTrue(TestCodeGen.test(input,expect, 503))