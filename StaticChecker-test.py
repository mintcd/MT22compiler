from Visitor import Visitor
from AST import *
from StaticError import *
from typing import List


class VarSym:
    def __init__(self, name, typ):
        self.name = name
        self.typ = typ  # Type of a variable must be known after declaration


class ParaSym:
    def __init__(self, name, typ = AutoType(), inherit=False, out=False):
        self.name = name
        self.typ = typ
        self.inherit = inherit
        self.out = out


class FuncSym:
    def __init__(self, name, params: List[ParaSym] = [], inherit=None, typ=AutoType()):
        self.name = name
        self.params = params
        self.inherit = inherit
        self.typ = typ


class Scope:
    def __init__(self, varsyms, funcsyms, parasyms=None, funcname=None):
        self.varsyms = varsyms
        self.funcsyms = funcsyms
        self.parasyms = parasyms
        self.funcname = funcname

    def contains(self, name):
        for var in self.varsyms:
            if var.name == name:
                return var
        for func in self.funcsyms:
            if func.name == name:
                return func
        for para in self.parasyms:
            if para.name == name:
                return para
        return None


class SymbolTable:
    @classmethod
    def checkUndeclared(name, st):
        for scope in st:
            res = scope.contains(name)
            return res
        raise Undeclared(Id(), name)


# def checkUndeclared(st, ):
#     for scope in st:
#         if scope.contains(name): return
#     raise Undeclared()


class StaticChecker(Visitor):

    # val: int
    def visitIntegerLit(self, ast, st):
        return IntegerType()

    # val: float
    def visitFloatLit(self, ast, st):
        return FloatType()

    # val: str
    def visitStringLit(self, ast, st):
        return StringType()

    # val: bool
    def visitBooleanLit(self, ast, st):
        return BooleanType()

    # explist: List[Expr]
    # ArrayType: dimensions: List[int], typ: AtomicType
    def visitArrayLit(self, ast, st):
        curType = self.visit(exp, st)
        for exp in ast.explist:
            if self.visit(exp, st) != curType:
                raise IllegalArrayLiteral(ast)
        return ArrayType(len(self.explist), curType)

    # name: str
    def visitId(self, ast, st):
        _id = SymbolTable.checkUndeclared(ast.name, st)
        return _id.typ

    # name: str, cell: List[Expr]
    def visitArrayCell(self, ast, st):
        for idx in ast.cell:
            if type(self.visit(idx, st)) is not IntegerLit():
                raise TypeMismatchInExpression(ast)
        arrsym = SymbolTable.checkUndeclared(ast.name, st)
        return arrsym.typ

    # op: str, left: Expr, right: Expr
    def visitBinExpr(self, ast, st):
        op = ast.op
        rtype = self.visit(ast.right, st)
        ltype = self.visit(ast.left, st)

        if op in ["+", "-", "*"]:
            if type(rtype) not in [IntegerType, FloatType] or type(ltype) not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            if FloatType in [type(rtype), type(ltype)]:
                return FloatType()
            return IntegerType()
        elif op == "/":
            if type(rtype) not in [IntegerType, FloatType] or type(ltype) not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            return FloatType()
        elif op == "%":
            if type(rtype) is not IntegerType or type(ltype) is not IntegerType:
                raise TypeMismatchInExpression(ast)
            return IntegerType()
        elif op in ["&&", "||"]:
            if type(rtype) is not BooleanType or type(ltype) is not BooleanType:
                raise TypeMismatchInExpression(ast)
            return BooleanType()
        elif op == "::":
            if type(rtype) is not StringType or type(ltype) is not StringType:
                raise TypeMismatchInExpression(ast)
            return StringType()
        elif op in ["==", "!="]:
            if type(rtype) is not type(ltype):
                raise TypeMismatchInExpression(ast)
            if ltype not in [IntegerType, BooleanType]:
                raise TypeMismatchInExpression(ast)
            return BooleanType()
        elif op in ["<", ">", "<=", ">="]:
            if type(rtype) not in [IntegerType, FloatType] or ltype not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            return BooleanType()
        return None

    # op: str, val: Expr
    def visitUnExpr(self, ast, st):
        op = ast.op
        typ = self.visit(ast.val, st)
        if op == "-":
            if type(typ) not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            return typ
        elif op == "!":
            if type(typ) is not BooleanType:
                raise TypeMismatchInExpression(ast)
            return typ
        return None

    # name: str, args: List[Expr]
    def visitFuncCall(self, ast, st):
        funcsym = SymbolTable.checkUndeclared(ast, st)
        if type(funcsym.typ) is not VoidType: 
            raise TypeMismatchInExpression(ast)
        if len(ast.args) != len(funcsym.params):
            raise TypeMismatchInExpression(ast)
        for i in range(len(ast.args)):
            argtype = self.visit(ast.args[i], st)
            if type(funcsym.params.typ) == AutoType:
                funcsym.params.typ = argtype
            else:
                if type(funcsym.params.typ) != argtype:
                    raise TypeMismatchInExpression(ast)
        return funcsym.typ

    # lhs: LHS, rhs: Expr
    def visitAssignStmt(self, ast, st):
        rhstype = self.visit(ast.rhs, st)
        lhstype = self.visit(ast.lhs, st)   

        if lhstype == AutoType:
            lhssym = SymbolTable.checkUndeclared(ast.lhs.name, st)
            lhssym.typ = rhstype
        else: 
            if type(ast.rhs) is Id:
                if rhstype is not lhstype:
                    raise TypeMismatchInStatement(ast)
            else:
                if rhstype is not lhstype and not (type(rhstype) is IntegerType and type(lhstype) is FloatType):
                    raise TypeMismatchInStatement(ast)
        return st      

    # body: List[Stmt or VarDecl]
    def visitBlockStmt(self, ast, param):
        pass

    # cond: Expr, tstmt: Stmt, fstmt: Stmt or None = None
    def visitIfStmt(self, ast, param):
        pass

    # init: AssignStmt, cond: Expr, upd: Expr, stmt: Stmt
    def visitForStmt(self, ast, param):
        pass

    # cond: Expr, stmt: Stmt
    def visitWhileStmt(self, ast, param):
        pass

    # cond: Expr, stmt: BlockStmt
    def visitDoWhileStmt(self, ast, param):
        pass

    def visitBreakStmt(self, ast, param):
        pass

    def visitContinueStmt(self, ast, param):
        pass

    # expr: Expr or None = None
    def visitReturnStmt(self, ast, param):
        pass

    # name: str, args: List[Expr]
    def visitCallStmt(self, ast, param):
        pass

    # name: str, typ: Type, init: Expr or None = None
    def visitVarDecl(self, ast, param):
        pass

    # name: str, typ: Type, out: bool = False, inherit: bool = False
    def visitParamDecl(self, ast, param):
        pass

    # name: str, return_type: Type, params: List[ParamDecl], inherit: str or None, body: BlockStmt
    def visitFuncDecl(self, ast, param):
        pass

    # decls: List[Decl]
    def visitProgram(self, ast, param):
        pass
