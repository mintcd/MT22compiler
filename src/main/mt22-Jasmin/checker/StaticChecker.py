from Visitor import Visitor
from StaticError import *
from typing import List
from AST import *


class MType:
    def __init__(self,partype,rettype):
        self.partype = partype
        self.rettype = rettype

class Symbol:
    def __init__(self,name,mtype,value = None):
        self.name = name
        self.mtype = mtype
        self.value = value

class Type: pass

class StmtType(Type): pass
class DeclType(Type): pass

class IntegerType(AtomicType):
    def __eq__(self, other): return True
class FloatType(AtomicType):
    def __eq__(self, other): return True  
class StringType(AtomicType):
    def __eq__(self, other): return True

class BooleanType(AtomicType):
    def __eq__(self, other): return True   

class AutoType(Type): 
    def __eq__(self, other): return True   

class ArrayType(Type):
    def __init__(self, dimensions: List[int], typ: AtomicType):
        self.dimensions = dimensions
        self.typ = typ

    def __eq__(self, other):
        return self.dimensions == other.dimensions and self.typ == other.typ
        
class Scope:
    def __init__(self,vardecls:List[VarDecl] = [], 
                 func:FuncDecl=None):
        self.vardecls = vardecls
        self.func = func

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
    def __init__(self, scopes:List[Scope] = [], funcdecls:List[FuncDecl] = []):
        self.scopes = scopes
        self.funcdecls = funcdecls

class Utils:

    def checkDuplicate(decls : List[ParamDecl]):
        seen = {}
        for decl in decls:
            if decl.name in seen:
                raise Redeclared(Parameter(), decl.name)
 
    def findFunc(name, st): 
        for funcdecl in st.funcdecls:
            if name == funcdecl.name: return funcdecl
        return None

    def findVar(name, st:SymbolTable):
        for scope in st.scopes:
            for vardecl in scope.vardecls:
                if name == vardecl.name: return vardecl
        return None
        
    def precheck(ast):
        st = SymbolTable()
        # decls: List[Decl]
        # Take functions and their own params
        for decl in ast.decls:
            if type(decl) is FuncDecl:
                Utils.checkDuplicate(decl.params)
                st.funcdecls.append(decl)

        # Take their inherit params if any
        for decl in st.funcdecls:
            flag = False
            if decl.inherit is not None:
                flag = False
                for parent in st.funcdecls:
                    if parent.name == decl.inherit:
                        flag = True
                        for parentParam in parent.params:
                            if parentParam.inherit:
                                decl.params.append(parentParam)
                        Utils.checkDuplicate(decl.params)
                if not flag: raise Undeclared(Function(), decl.inherit)  
        Utils.checkDuplicate(decl.funcdecls)
        return st


""" Return new Symbol Table and type"""
class StaticChecker(Visitor):

    # val: int
    def visitIntegerLit(self, ast, st):
        return st, IntegerType()

    # val: float
    def visitFloatLit(self, ast, st):
        return st, FloatType()

    # val: str
    def visitStringLit(self, ast, st):
        return st, StringType()

    # val: bool
    def visitBooleanLit(self, ast, st):
        return st, BooleanType()

    
    # explist: List[Expr]
    # ArrayType: dimensions: List[int], typ: AtomicType
    def visitArrayLit(self, ast, st):
        typ = AutoType()
        for exp in ast.explist:
            _, exptyp = self.visit(exp, st)
            if typ == AutoType(): 
                typ = exptyp
            else:
                if typ != exptyp: raise IllegalArrayLiteral(ast)
        
        if type(typ) is ArrayType:
            return st, ArrayType([len(ast.explist)] + typ.dimensions, typ.typ)
        return st, ArrayType([len(ast.explist)], typ)

    # name: str
    def visitId(self, ast, st):
        _id = Utils.checkUndeclared(ast.name, st)
        return st, _id.typ

    # name: str, cell: List[Expr]
    def visitArrayCell(self, ast, st):
        arraysym = Utils.checkUndeclared(ast.name, st)
        if type(arraysym) is not ArrayType:
            raise TypeMismatchInExpression(ast)
        for idx in ast.cell:
            _, idxtype = self.visit(idx, st)
            if type(idxtype) is not IntegerLit:
                raise TypeMismatchInExpression(ast)
        arrsym = Utils.checkUndeclared(ast.name, st)
        if len(ast.cell) == len(arrsym.typ.dimensions): 
            return st, arrsym.typ.typ
        return st, ArrayType(arrsym.typ.dimesions[len(ast.cell):], arrsym.typ.typ)

    # op: str, left: Expr, right: Expr
    def visitBinExpr(self, ast, st):
        op = ast.op
        _, rtype = self.visit(ast.right, st)
        _, ltype = self.visit(ast.left, st)

        if op in ["+", "-", "*"]:
            if type(rtype) not in [IntegerType, FloatType] or type(ltype) not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            if FloatType in [type(rtype), type(ltype)]:
                return FloatType()
            return st, IntegerType()
        elif op == "/":
            if type(rtype) not in [IntegerType, FloatType] or type(ltype) not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            return st, FloatType()
        elif op == "%":
            if type(rtype) is not IntegerType or type(ltype) is not IntegerType:
                raise TypeMismatchInExpression(ast)
            return st, IntegerType()
        elif op in ["&&", "||"]:
            if type(rtype) is not BooleanType or type(ltype) is not BooleanType:
                raise TypeMismatchInExpression(ast)
            return st, BooleanType()
        elif op == "::":
            if type(rtype) is not StringType or type(ltype) is not StringType:
                raise TypeMismatchInExpression(ast)
            return st, StringType()
        elif op in ["==", "!="]:
            if type(rtype) is not type(ltype):
                raise TypeMismatchInExpression(ast)
            if ltype not in [IntegerType, BooleanType]:
                raise TypeMismatchInExpression(ast)
            return st, BooleanType()
        elif op in ["<", ">", "<=", ">="]:
            # The same type?
            if type(rtype) not in [IntegerType, FloatType] or ltype not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            return st, BooleanType()
        return None

    # op: str, val: Expr
    def visitUnExpr(self, ast, st):
        op = ast.op
        _, typ = self.visit(ast.val, st)
        if op == "-":
            if type(typ) not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            return st, typ
        elif op == "!":
            if type(typ) is not BooleanType:
                raise TypeMismatchInExpression(ast)
            return st, typ
        return None
    # name: str, args: List[Expr]
    def visitFuncCall(self, ast, st):
        funcsym = Utils.checkUndeclared(ast, st)
        if type(funcsym.typ) is VoidType: 
            raise TypeMismatchInExpression(ast)
        if len(ast.args) != len(funcsym.params):
            raise TypeMismatchInExpression(ast)
        for i in range(len(ast.args)):
            st, argtype = self.visit(ast.args[i], st)
            if type(funcsym.params[i].typ) is AutoType:
                funcsym.params[i].typ = argtype
            else:
                if type(funcsym.params.typ) is not type(argtype):
                    raise TypeMismatchInExpression(ast)
        return st, funcsym.typ

    # lhs: LHS, rhs: Expr
    def visitAssignStmt(self, ast, st):
        _, rhstype = self.visit(ast.rhs, st)
        _, lhstype = self.visit(ast.lhs, st)   

        if type(lhstype) == AutoType:
            lhssym = Utils.checkUndeclared(ast.lhs.name, st)
            lhssym.typ = rhstype
        else: 
            if type(ast.rhs) is Id:
                if type(rhstype) is not type(lhstype):
                    raise TypeMismatchInStatement(ast)
            else:
                if type(rhstype) is not type(lhstype) and not (type(rhstype) is IntegerType and type(lhstype) is FloatType):
                    raise TypeMismatchInStatement(ast)
        return  st, StmtType()

    # body: List[Stmt or VarDecl]
    def visitBlockStmt(self, ast, st):
        st = Utils.newscope(ast, st)
        for ele in ast.body:
            st, _ = self.visit(ast.body, st)
        return st, StmtType()


    # cond: Expr, tstmt: Stmt, fstmt: Stmt or None = None
    def visitIfStmt(self, ast, st):
        _, condtype = self.visit(ast.cond, st)
        if type(condtype) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        st, _ = self.visit(ast.tstmt, st)
        if ast.fstmt: st, _ = self.visit(ast.fstmt, st)

        return st, StmtType()


    # init: AssignStmt, cond: Expr, upd: Expr, stmt: Stmt
    def visitForStmt(self, ast, st):
        # Ở đây gọi lại AssignStmt nhưng có vẻ chưa handle được index operator. Ví dụ: a[1]
        st, assType = self.visit(ast.AssignStmt, st)
        if type(assType) is not IntegerType:
            raise TypeMismatchInStatement(ast)
        st, condType = self.visit(ast.cond, st)
        if type(condType) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        st, updType = self.visit(ast.upd, st)
        if type(updType) is not IntegerType:
            raise TypeMismatchInStatement(ast)
        st, stmt = self.visit(ast.stmt, st)
        return st, StmtType()

    # cond: Expr, stmt: Stmt
    def visitWhileStmt(self, ast, st):
        st, condType = self.visit(ast.cond, st)
        if type(condType) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        st, stmt = self.visit(ast.stmt, st)
        return st, StmtType()

    # cond: Expr, stmt: BlockStmt
    def visitDoWhileStmt(self, ast, st):
        st, condType = self.visit(ast.cond, st)
        if type(condType) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        st, stmt = self.visit(ast.stmt, st)
        return st, StmtType()

    def visitBreakStmt(self, ast, param):
        pass

    def visitContinueStmt(self, ast, param):
        pass

    # expr: Expr or None = None
    def visitReturnStmt(self, ast, param):
        if ast.expr is None:
            return None
        st, expr = self.visit(ast.expr, st)
        return st, expr

    # name: str, args: List[Expr]
    def visitCallStmt(self, ast, param):
        funcsym = Utils.findFunc(ast.name, st)
        if not funcsym: raise Undeclared(Function(), ast.name)

        if len(ast.args) != len(funcsym.params):
            raise TypeMismatchInStatement(ast)
        for i in range(len(ast.args)):
            st, argtype = self.visit(ast.args[i], st)
            if type(funcsym.params[i].typ) == AutoType:
                funcsym.params[i].typ = argtype
            else:
                if type(funcsym.params[i].typ) is not type(argtype):
                    raise TypeMismatchInStatement(ast)
        return st, VoidType()

    # name: str, typ: Type, init: Expr or None = None
    def visitVarDecl(self, ast, st:SymbolTable):
        # Check redeclared
        for vardecl in st.scopes[0].vardecls:
            if vardecl.name == ast.name:
                raise Redeclared(Variable(), ast.name)
        # Check type agreement
        if type(ast.typ) is FloatType:
            if type(ast.init) not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression()
        elif type(ast.typ) is AutoType:
            if ast.init is None:
                raise Invalid(Variable(), ast.name)
            _, ast.typ = self.visit(ast.init)
        else:
            _, initType = self.visit(ast.init)
            if type(ast.typ) is not type(initType):
                raise TypeMismatchInExpression()
        st.scopes[0].vardecls.append(ast)

    # name: str, typ: Type, out: bool = False, inherit: bool = False
    def visitParamDecl(self, ast, st):
        pass
        

    # name: str, return_type: Type, params: List[ParamDecl], inherit: str or None, body: BlockStmt
    def visitFuncDecl(self, ast:FuncDecl, st:SymbolTable):
        funcdecl = Utils.findFunc(ast.name, st)
        if not funcdecl.inherit:
            for ele in ast.body.body: st = self.visit(ele, st)
        else:
            parentFunc = Utils.fincFunc(funcdecl.inherit)
            firststmt = ast.body.body[0]
            if firststmt.name == 'super': 
                self.visit(CallStmt(parentFunc.name, firststmt.args), st)
            elif firststmt.name != 'preventDefault':
                self.visit(CallStmt(parentFunc.name, []), st)
        return st, DeclType()
                

    # decls: List[Decl]
    def visitProgram(self, ast, st):
        st = Utils.precheck(ast)
        for decl in ast.decls:
            st = self.visit(decl, st)
        return ast

