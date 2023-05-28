from ctypes.wintypes import HINSTANCE
from Emitter import Emitter
from functools import reduce
from StaticChecker import StaticChecker
from Allocator import Allocator

from Frame import Frame
from abc import ABC
from Visitor import *
from AST import *


class CodeGenerator:
    def __init__(self):
        self.libName = "io"

    def getBuiltinMethods(self):
        # Built-in methods
        return []

    def gen(self, ast : AST, path : str):
        
        # Static checking        
        StaticChecker(ast).check()
        gl = self.getBuiltinMethods()
        
        gc = CodeGenVisitor(ast, gl, path)
        gc.visit(ast, None)

class CodeGenVisitor(Visitor):
    def __init__(self, ast, env, path):
        # The code object can just be appended so we can set it as global
        self.code = ""
        self.allocator = Allocator()
        self.st = self.allocator.st


    def visitProgram(self, ast : Program, st): 
        # Find main function
        mainFunc = filter(lambda decl: decl.name == 'main', ast.decls)
        
        # Visit function declaration one by one
        

    def visitFuncDecl(self, ast, code): pass

    def visitParamDecl(self, ast, param):
        return super().visitParamDecl(ast, param)

    def visitVarDecl(self, ast, code): pass
    
    def visitCallStmt(self, ast, param):
        return super().visitCallStmt(ast, param)
    
    def visitReturnStmt(self, ast, param):
        return super().visitReturnStmt(ast, param)
    
    def visitContinueStmt(self, ast, param):
        return super().visitContinueStmt(ast, param)
    
    def visitBreakStmt(self, ast, param):
        return super().visitBreakStmt(ast, param)
    
    def visitDoWhileStmt(self, ast, param):
        return super().visitDoWhileStmt(ast, param)
    
    def visitWhileStmt(self, ast, param):
        return super().visitWhileStmt(ast, param)
    
    def visitForStmt(self, ast, param):
        return super().visitForStmt(ast, param)
    
    def visitIfStmt(self, ast, param):
        return super().visitIfStmt(ast, param)
    
    def visitBlockStmt(self, ast, param):
        return super().visitBlockStmt(ast, param)
    
    def visitAssignStmt(self, ast, param):
        return super().visitAssignStmt(ast, param)
    
    def visitFuncCall(self, ast, param):
        return super().visitFuncCall(ast, param)
    
    def visitArrayLit(self, ast, param):
        return super().visitArrayLit(ast, param)
    
    def visitBooleanLit(self, ast, param):
        return super().visitBooleanLit(ast, param)
    
    def visitStringLit(self, ast, param):
        return super().visitStringLit(ast, param)
    
    def visitFloatLit(self, ast, param): pass
    
    def visitIntegerLit(self, ast, param): pass
    
    def visitId(self, ast, param): pass
    
    def visitUnExpr(self, ast, code): 
        code += self.emit.emitNEGOP
    
    def visitBinExpr(self, ast, param): pass

    

    

    
