from ctypes.wintypes import HINSTANCE
from Emitter import Emitter
from functools import reduce

from Frame import Frame
from abc import ABC
from Visitor import *
from AST import *


class MType:
    def __init__(self, partype, rettype):
        self.partype = partype
        self.rettype = rettype


# class Symbol:
#     def __init__(self, name : str, mtype : MType, value=None):
#         self.name = name
#         self.mtype = mtype
#         self.value = value

#     def __str__(self):
#         return "Symbol(" + self.name + "," + str(self.mtype) + ")"

class Symbol:
    def __init__(self, name, typ: Type):
        self.name = name
        self.typ = typ
    def __str__(self):
        return "Symbol({}, {})".format(self.name, self.typ)


class VarSym(Symbol):
    def __init__(self, name : str, typ : Type):
        super().__init__(name, typ)
        
class ParaSym(Symbol):
    def __init__(self, name : str, typ : Type, out: bool = False, inherit: bool = False):
        super().__init__(name, typ)
        self.out = out
        self.inherit = inherit
    def __str__(self):
        return "ParaSym({}, {}{}{})".format(self.name, 
                                            self.typ, 
                                            ", inherit" if self.inherit else "",
                                            ", out" if self.out else "")
class FuncSym(Symbol):
    def __init__(self, name : str, typ : Type, paramTypes: List[Type] = [], inherit: str or None = None, parentparams: List[ParaSym] = [],):
        super().__init__(name, typ)
        self.paramTypes = paramTypes
        self.inherit = inherit
        self.parentparams = parentparams



class CodeGenerator:
    def __init__(self):
        self.libName = "io"

    def getBuiltinMethods(self):
        # Built-in methods
        return [Symbol("readInteger", MType(list(), IntegerType()), CName(self.libName)),
                Symbol("printInteger", MType([IntegerType()],
                       VoidType()), CName(self.libName))
                ]

    def gen(self, ast, path):
        # ast: AST
        # dir_: String

        gl = self.getBuiltinMethods()
        gc = CodeGenVisitor(ast, gl, path)
        gc.visit(ast, None)


class SubBody():
    def __init__(self, frame, sym):
        self.frame = frame
        self.sym = sym


class Access():
    def __init__(self, frame, sym, isLeft, isFirst=False):
        self.frame = frame
        self.sym = sym
        self.isLeft = isLeft
        self.isFirst = isFirst


class Val(ABC): pass


class Index(Val):
    def __init__(self, value):
        self.value = value


class CName(Val):
    def __init__(self, value):
        self.value = value


class CodeGenVisitor(Visitor):
    def __init__(self, ast, env, path):
        self.ast = ast
        self.env = env
        self.path = path
        self.className = "MT22Class"
        self.emit = Emitter(self.path + "/" + self.className + ".j")


    def visitProgram(self, ast : Program, c):
        self.emit.printout(self.emit.emitPROLOG(self.className, "java.lang.Object"))
        staticDecl = self.env
        for decl in ast.decls:
            if type(decl) is FuncDecl:
                staticDecl = [Symbol(decl.name.name, 
                                        MType([param.varType for param in decl.params], 
                                        decl.returnType), CName(self.className))] + staticDecl
            else:
                newSym = self.visit(decl, SubBody(None, None, isGlobal=True))
                staticDecl = [newSym] + staticDecl
        
        e = SubBody(None, staticDecl)
        [self.visit(x, e) for x in ast.decl if type(x) is FuncDecl]

        # generate default constructor
        self.genMETHOD(FuncDecl(Id("<init>"), list(), list(), list(), None), c, Frame("<init>", VoidType))
        # class init - static field
        self.genMETHOD(FuncDecl(Id("<clinit>"), list(), list(), list(), None), c, Frame("<clinit>", VoidType))
        
        self.emit.emitEPILOG()
        return c

    def visitFuncDecl(self, ast, code): 
        pass

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

    

    

    
