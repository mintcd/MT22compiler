from typing import List

from Visitor import Visitor
from StaticError import *
from AST import *
from abc import ABC


class StmtType(Type):
    pass


class DeclType(Type):
    pass


class Symbol:
    def __init__(self, name, typ: Type):
        self.name = name
        self.typ = typ


class VarSym(Symbol):
    def __init__(self, name, typ):
        super().__init__(name, typ)


class ParaSym(Symbol):
    def __init__(self, name, typ, out: bool = False, inherit: bool = False):
        super().__init__(name, typ)
        self.out = out
        self.inherit = inherit


class FuncSym(Symbol):
    def __init__(
        self,
        name,
        typ,
        params: List[Symbol] = [],
        inherit: str or None = None,
        parentparams: List[ParaSym] = [],
    ):
        super().__init__(name, typ)
        self.params = params
        self.inherit = inherit
        self.parentparams = parentparams


class Scope:
    def __init__(self, syms: List[Symbol] = []):
        self.syms = syms


class SymbolTable:
    def __init__(self, inners: List[Scope] = [Scope()], outer: List[Symbol] = []):
        self.inners = inners
        self.outer = outer


class Utils:
    def inferParam(params, paramName, typ):
        for param in params:
            if param.name == paramName:
                param.typ.typ = typ
                return typ

    def inferId():
        pass

    def checkDuplicate(decls: List[ParamDecl]):
        seen = {}
        for decl in decls:
            if decl.name in seen:
                raise Redeclared(Parameter(), decl.name)


class PreCheck(Visitor):
    # decls: List[Decl]
    def visitProgram(self, ast: Program, st: SymbolTable):
        st = SymbolTable()
        for decl in ast.decls:
            if type(decl) is FuncDecl:
                st.outer.append(
                    FuncSym(
                        decl.name,
                        decl.return_type,
                        list(
                            map(
                                lambda paramdecl: ParaSym(
                                    paramdecl.name,
                                    paramdecl.typ,
                                    paramdecl.out,
                                    paramdecl.inherit,
                                ),
                                decl.params,
                            )
                        ),
                    )
                )
        return st


class StaticChecker(Visitor):

    def __init__(self, ast):
        self.ast = ast
 
    def check(self):
        return self.visitProgram(self.ast, [])
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
            st, exptyp = self.visit(exp, st)
            if typ == AutoType():
                typ = exptyp
            else:
                if typ != exptyp:
                    raise IllegalArrayLiteral(ast)

        if type(typ) is ArrayType:
            return st, ArrayType([len(ast.explist)] + typ.dimensions, typ.typ)
        return st, ArrayType([len(ast.explist)], typ)

    # name: str
    def visitId(self, ast, st: SymbolTable):
        for scope in st.inners:
            for var in scope.syms:
                if var.name == ast.name:
                    return st, var.typ
        raise Undeclared(Identifier(), ast.name)

    # name: str, cell: List[Expr]
    def visitArrayCell(self, ast, st):
        arraysym = Utils.checkUndeclared(ast.name, st)
        if type(arraysym) is not ArrayType:
            raise TypeMismatchInExpression(ast)
        for idx in ast.cell:
            st, idxtype = self.visit(idx, st)
            if type(idxtype) is not IntegerLit:
                raise TypeMismatchInExpression(ast)
        arrsym = Utils.checkUndeclared(ast.name, st)
        if len(ast.cell) == len(arrsym.typ.dimensions):
            return st, arrsym.typ.typ
        return st, ArrayType(arrsym.typ.dimesions[len(ast.cell) :], arrsym.typ.typ)

    # op: str, left: Expr, right: Expr
    def visitBinExpr(self, ast, st):
        op = ast.op
        st, rtype = self.visit(ast.right, st)
        st, ltype = self.visit(ast.left, st)

        if type(rtype) is AutoType:
            Utils.infer()

        if op in ["+", "-", "*"]:
            if type(rtype) not in [IntegerType, FloatType] or type(ltype) not in [
                IntegerType,
                FloatType,
            ]:
                raise TypeMismatchInExpression(ast)
            if FloatType in [type(rtype), type(ltype)]:
                return st, FloatType()
            return st, IntegerType()
        elif op == "/":
            if type(rtype) not in [IntegerType, FloatType] or type(ltype) not in [
                IntegerType,
                FloatType,
            ]:
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
            if type(rtype) not in [IntegerType, FloatType] or ltype not in [
                IntegerType,
                FloatType,
            ]:
                raise TypeMismatchInExpression(ast)
            return st, BooleanType()

    # op: str, val: Expr
    def visitUnExpr(self, ast, st):
        op = ast.op
        st, typ = self.visit(ast.val, st)
        if op == "-":
            if type(typ) not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            return st, typ
        elif op == "!":
            if type(typ) is not BooleanType:
                raise TypeMismatchInExpression(ast)
            return st, typ

    # name: str, args: List[Expr]
    def visitFuncCall(self, ast, st):
        # Check if there is callee
        funcsym = None
        for sym in st.outer:
            if sym.name == ast.name:
                funcsym = sym
        if not funcsym: raise Undeclared(Function(), ast.name)
        if funcsym.typ == VoidType(): raise TypeMismatchInExpression(ast)
        # Check its parameters
        if len(funcsym.params) != len(ast.args): raise TypeMismatchInExpression(ast)
        for i in range(len(funcsym.params)):
            if funcsym.params[i].out: 
                if type(ast.args[i]) is not LHS:
                    raise TypeMismatchInExpression(ast)              
        for i in range(len(funcsym.params)):
            argType = self.visit(ast.args[i], st)
            if funcsym.params[i].typ == AutoType():
                _, funcsym.params[i] = argType
            elif funcsym.params[i].typ == FloatType():
                if argType == IntegerType(): continue
            elif funcsym.params[i].typ != argType:
                raise TypeMismatchInExpression(ast)    
        return st, funcsym.typ

    # lhs: LHS, rhs: Expr
    def visitAssignStmt(self, ast, st):
        st, rhstype = self.visit(ast.rhs, st)
        st, lhstype = self.visit(ast.lhs, st)

        if type(lhstype) == AutoType:
            lhssym = Utils.checkUndeclared(ast.lhs.name, st)
            lhssym.typ = rhstype
        else:
            if type(ast.rhs) is Id:
                if type(rhstype) is not type(lhstype):
                    raise TypeMismatchInStatement(ast)
            else:
                if type(rhstype) is not type(lhstype) and not (
                    type(rhstype) is IntegerType and type(lhstype) is FloatType
                ):
                    raise TypeMismatchInStatement(ast)
        return st, StmtType()

    # body: List[Stmt or VarDecl]
    def visitBlockStmt(self, ast, st): 
        for ele in ast.body:
            st, _ = self.visit(ele, st)
        return st, StmtType()

    # cond: Expr, tstmt: Stmt, fstmt: Stmt or None = None
    def visitIfStmt(self, ast, st):
        _, condtype = self.visit(ast.cond, st)
        if type(condtype) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        st, _ = self.visit(ast.tstmt, st)
        if ast.fstmt:
            st, _ = self.visit(ast.fstmt, st)

        return st, StmtType()

    # init: AssignStmt, cond: Expr, upd: Expr, stmt: Stmt
    def visitForStmt(self, ast, st):
        # Ở đây gọi lại AssignStmt nhưng có vẻ chưa handle được index operator. Ví dụ: a[1]
        st, assType = self.visit(ast.init, st)
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
        if ast.expr is not None:
            st, _ =  self.visit(ast.expr, st)
        return st, StmtType()

    # name: str, args: List[Expr]
    def visitCallStmt(self, ast : CallStmt, st : SymbolTable):
        # Check if there is callee
        funcsym = None
        for sym in st.outer:
            if sym.name == ast.name:
                funcsym = sym
        if not funcsym: raise Undeclared(Function(), ast.name)
        # Check its parameters
        if len(funcsym.params) != len(ast.args): raise TypeMismatchInStatement(ast)
        for i in range(len(funcsym.params)):
            if funcsym.params[i].out: 
                if type(ast.args[i]) is not LHS:
                    raise TypeMismatchInStatement(ast)                
        for i in range(len(funcsym.params)):
            argType = self.visit(ast.args[i], st)
            if funcsym.params[i].typ == AutoType():
                _, funcsym.params[i] = argType
            elif funcsym.params[i].typ == FloatType():
                if argType == IntegerType(): continue
            elif funcsym.params[i].typ != argType:
                raise TypeMismatchInStatement(ast)
            
        return st, StmtType()

    # name: str, typ: Type, init: Expr or None = None
    def visitVarDecl(self, ast: VarDecl, st: SymbolTable):
        """Check if there is the same name in scope 0"""
        for sym in st.inners[0].syms:
            if sym.name == ast.name:
                raise Redeclared(Variable(), ast.name)

        """Check semantics"""
        # There is no init
        if not ast.init:
            if ast.typ == AutoType():
                raise Invalid(Variable(), ast.name)
            st.inners[0].syms.append(VarSym(ast.name, ast.typ))
            return st, DeclType()
        # There is init
        else:
            st, inityp = self.visit(ast.init, st)
            if type(ast.typ) is AutoType:
                st.inners[0].syms.append(VarSym(ast.name, inityp))
                return st, DeclType()
            else:
                print("381")
                st, inittyp = self.visit(ast.init,st)
                if type(ast.typ) is not type(inittyp):
                    raise TypeMismatchInVarDecl(ast)
                if type(ast.typ) is ArrayType():
                    if ast.typ != inityp:
                        if ast.typ.dimensions != inityp.dimensions:
                            raise TypeMismatchInVarDecl(ast)
                        if ast.typ.typ == AutoType():
                            st.inners[0].syms.append(VarSym(ast.name, inityp.typ))
                            return st
                        raise TypeMismatchInVarDecl(ast)
                st.inners[0].syms.append(VarSym(ast.name, ast.typ))
                return st, DeclType()

    # name: str, typ: Type, out: bool = False, inherit: bool = False
    def visitParamDecl(self, ast: ParamDecl, st: SymbolTable):
        pass

    # name: str, return_type: Type, params: List[ParamDecl], inherit: str or None, body: BlockStmt
    def visitFuncDecl(self, ast: FuncDecl, st: SymbolTable):
        # If there is already the same name, raise
        for sym in st.inners[0].syms:
            if sym.name == ast.name:
                raise Redeclared(Function(), ast.name)
        """ If this function inherits """
        funcsym = FuncSym(ast.name, ast.return_type, list(
                            map(
                                lambda paramdecl: ParaSym(
                                    paramdecl.name,
                                    paramdecl.typ,
                                    paramdecl.out,
                                    paramdecl.inherit,
                                ),
                                ast.params,
                            )
                        ),
                    )
        

        st.inners[0].syms.append(funcsym)
        newst = SymbolTable([Scope()] + st.inners, st.outer)

        if ast.inherit:
            # Find its parent, if there is not raise Undeclared
            parentsym = None
            for funcsym in newst.outer:
                if ast.inherit == funcsym.name: 
                    parentsym = funcsym
                    break
            if not parentsym: raise Undeclared(Function(), ast.inherit)

            """ Append its parent's inherit params into scope 0 """
            for parentparam in parentsym.params:
                if parentparam.inherit:
                    newst.inners[0].syms.append(parentparam)

            """ Traverse its params """
            # If same name as parent's raise Invalid
            for param in funcsym:
                for parentparam in newst.inners[0].syms:
                    if param.name == parentparam.name:
                        raise Invalid(Parameter(), param.name)
            # If same nams as its own raise Redeclared
            for param in funcsym:
                for currentparam in newst.inners[0].syms:
                    if param.name == currentparam.name:
                        raise Redeclared(Parameter(), param.name)
                newst.inners[0].syms.append(param)
        
            """Traverse first statement"""
            # Nothing or not in ['prevendefaut', 'super']
            if len(ast.body.body) == 0 or ast.body.body[0].name not in ['preventDefault', 'super']: 
                if len(parentsym.params) != 0:
                    raise TypeMismatchInExpression()
            elif ast.body.body[0].name == 'preventDefault': pass
            # super(args) === parentsym.name(args)
            else:
                newst, _ = self.visit(CallStmt(parentsym.name, ast.body.body[0].args), newst)

            """ Visit body as a normal Blockstmt """
            newst, _ = self.visit(ast.body, newst)
        else:
            """Traverse its own params"""
            for param in funcsym.params:
                for currentparam in newst.inners[0].syms:
                    if param.name == currentparam.name:
                        raise Redeclared(Parameter(), param.name)
                newst.inners[0].syms.append(param)
            
            if len(ast.body.body) > 0 and type(ast.body.body[0]) is CallStmt and ast.body.body[0].name in ['preventDefault', 'super']:
                raise InvalidStatementInFunction(ast.name)
                

            """Traverse its body"""
            newst, _ = self.visit(ast.body, newst)

        return st, DeclType()

    # decls: List[Decl]
    def visitProgram(self, ast, st):
        st = PreCheck().visit(ast, st)
        for decl in ast.decls:
            st, _ = self.visit(decl, st)
