from Visitor import Visitor
from AST import *


class NoneType(Type):
    pass


class VarSym:
    def __init__(self, name, typ, val=None):
        self.name = name
        self.typ = typ    # Type of a variable must be known after declaration


class FuncSym:
    def __init__(self, name, params=[], inherit=None, typ=NoneType()):
        self.name = name
        self.params = params
        self.inherit = inherit
        self.typ = typ


class ParaSym:
    def __init__(self, name, typ, inheritFunc=None, out=False):
        self.name = name
        self.typ = typ
        self.inheritFunc = inheritFunc
        self.out = out


class SymbolTable:
    def __init__(self, vardecls, funcdecls, paramdecls=None):
        self.vardecls = vardecls
        self.funcdecls = funcdecls
        self.paramdecls = paramdecls


class StaticChecker(Visitor):
    def visitIntegerType(self, ast, param): pass
    def visitFloatType(self, ast, param): pass
    def visitBooleanType(self, ast, param): pass
    def visitStringType(self, ast, param): pass
    def visitAutoType(self, ast, param): pass
    def visitVoidType(self, ast, param): pass

    # dimensions: List[int], typ: AtomicType
    def visitArrayType(self, ast, param): pass

    # op: str, left: Expr, right: Expr
    def visitBinExpr(self, ast, param): pass

    # op: str, val: Expr
    def visitUnExpr(self, ast, param): pass

    # name: str
    def visitId(self, ast, param): pass

    # name: str, cell: List[Expr]
    def visitArrayCell(self, ast, param): pass

    # val: int
    def visitIntegerLit(self, ast, param): pass

    # val: float
    def visitFloatLit(self, ast, param): pass

    # val: str
    def visitStringLit(self, ast, param): pass

    # val: bool
    def visitBooleanLit(self, ast, param): pass

    # explist: List[Expr]
    def visitArrayLit(self, ast, param): pass

    # name: str, args: List[Expr]
    def visitFuncCall(self, ast, param): pass

    # lhs: LHS, rhs: Expr
    def visitAssignStmt(self, ast, param): pass

    # body: List[Stmt or VarDecl]
    def visitBlockStmt(self, ast, param): pass

    # cond: Expr, tstmt: Stmt, fstmt: Stmt or None = None
    def visitIfStmt(self, ast, param): pass

    # init: AssignStmt, cond: Expr, upd: Expr, stmt: Stmt
    def visitForStmt(self, ast, param): pass

    # cond: Expr, stmt: Stmt
    def visitWhileStmt(self, ast, param): pass

    # cond: Expr, stmt: BlockStmt
    def visitDoWhileStmt(self, ast, param): pass

    def visitBreakStmt(self, ast, param): pass

    def visitContinueStmt(self, ast, param): pass

    # expr: Expr or None = None
    def visitReturnStmt(self, ast, param): pass

    # name: str, args: List[Expr]
    def visitCallStmt(self, ast, param): pass

    # name: str, typ: Type, init: Expr or None = None
    def visitVarDecl(self, ast, param): pass

    # name: str, typ: Type, out: bool = False, inherit: bool = False
    def visitParamDecl(self, ast, param): pass

    # name: str, return_type: Type, params: List[ParamDecl], inherit: str or None, body: BlockStmt
    def visitFuncDecl(self, ast, param): pass

    # decls: List[Decl]
    def visitProgram(self, ast, param): pass
