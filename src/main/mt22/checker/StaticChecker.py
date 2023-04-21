from typing import List
from Visitor import Visitor
from StaticError import *
from AST import *
from abc import ABC


class StmtType(Type): pass
class DeclType(Type): pass

class VarDeclType(Type): pass
class FuncDeclType(Type): pass


class LoopStmtType(StmtType): pass
class MustInLoopStmtType(StmtType): pass
class AssignStmtType(StmtType): pass
class IfStmtType(StmtType): pass
class ReturnStmtType(StmtType): pass
class BlockStmtType(StmtType): pass
class CallStmtType(StmtType): pass

class Symbol:
    def __init__(self, name, typ: Type):
        self.name = name
        self.typ = typ


class VarSym(Symbol):
    def __init__(self, name : str, typ : Type):
        super().__init__(name, typ)


class ParaSym(Symbol):
    def __init__(self, name : str, typ : Type, out: bool = False, inherit: bool = False):
        super().__init__(name, typ)
        self.out = out
        self.inherit = inherit


class FuncSym(Symbol):
    def __init__(self, name : str, typ : Type, params: List[Symbol] = [], inherit: str or None = None, parentparams: List[ParaSym] = [],):
        super().__init__(name, typ)
        self.params = params
        self.inherit = inherit
        self.parentparams = parentparams


""" Every node points to a symbol table where there is a field received from parent and its own field
Function prototypes must be saved separately in precheck
Every node returns a pair of st and type which can be used by parent
"""

class SymbolTable:
    def __init__(self, env : List[List[Symbol]] = [[]], funcprototype : List[FuncSym] = [], fromParent = [], fromChildren = []):
        """To receive information from parent"""
        self.fromParent = fromParent

        """To receive information from child"""
        self.fromChildren = fromChildren

        """Local environments"""
        self.env = env

        """Global function prototypes"""
        self.funcprototype = funcprototype

class Utils:
    def findSym(name : str, st : SymbolTable):
        for scope in st.env:
            for sym in scope:
                if sym.name == name: return sym
        return None
    
    def infer(name : str, typ : Type, st : SymbolTable):
        for scope in st.env:
            for sym in scope:
                if sym.name == name and type(sym) is VarSym or type(sym) is ParaSym:
                    sym.typ = typ
                    return sym
        return None

    def passToParent(info, st : SymbolTable):
        """Remove a scope and pass it to parent"""
        return SymbolTable(st.env, st.funcprototype, [], st.fromChildren + [info])
    
    def passToChild(info, st : SymbolTable):
        """Create a new scope and pass it to child""" 
        return SymbolTable(st.env, st.funcprototype, st.fromParent + [info], [])
    
    def createScope(st : SymbolTable):
        return SymbolTable([[]] + st.env, st.funcprototype, st.fromParent, st.fromChildren)
    
    def removeScope(st : SymbolTable):
        return SymbolTable(st.env[1:], st.funcprototype, st.fromParent, st.fromChildren)

        

class PreCheck(Visitor):
    """Visit funcdecls"""
    def visitProgram(self, ast: Program, st: SymbolTable):
        for decl in ast.decls:
            if type(decl) is FuncDecl: 
                st = self.visit(decl, st)
        return st
    
    """Append prototypes"""
    def visitFuncDecl(self, ast : FuncDecl, st : SymbolTable):
        return SymbolTable(st.env, st.funcprototype + [FuncSym(ast.name, ast.return_type, ast.params, ast.inherit, [])], st.fromParent, st.fromChildren)


class StaticChecker(Visitor):

    def __init__(self, ast):
        self.ast = ast
 
    def check(self):
        return self.visitProgram(self.ast, [])

    def visitIntegerLit(self, ast : IntegerLit, st): return st, IntegerType()

    def visitFloatLit(self, ast : FloatLit, st): return st, FloatType()

    def visitStringLit(self, ast : StringLit, st): return st, StringType()

    def visitBooleanLit(self, ast : BooleanLit, st): return st, BooleanType()

    def visitArrayLit(self, ast : ArrayLit, st : SymbolTable):
        """ All elements must be of the same type and not be AutoType"""
        typ = AutoType()
        for exp in ast.explist:
            st, exptyp = self.visit(exp, st)
            if type(typ) is AutoType:
                typ = exptyp
            else:
                # If they are of different types or array type with different dicts
                if type(typ) is not type(exptyp): raise IllegalArrayLiteral(ast)
                if type(typ) is ArrayType and (typ.dimensions != exptyp.dimensions or typ.typ != exptyp.typ): 
                    raise IllegalArrayLiteral(ast)

        # All elements are of AutoType       
        if type(typ) is AutoType: raise IllegalArrayLiteral(ast)

        # Elements are arrays
        if type(typ) is ArrayType:
            return st, ArrayType([len(ast.explist)] + typ.dimensions, typ.typ)
        return st, ArrayType([len(ast.explist)], typ)

    def visitId(self, ast : Id, st: SymbolTable):
        sym = Utils.findSym(ast.name, st)
        if not sym: raise Undeclared(Identifier(), ast.name)
        if type(sym) not in [VarSym, ParaSym]: raise TypeMismatchInExpression(ast) 
        return st, sym.typ

    def visitArrayCell(self, ast : ArrayCell, st : SymbolTable):
        sym = Utils.findSym(st, ast.name)
        if not sym: raise Undeclared(Identifier(), ast.name)
        if type(sym) is not ArrayType: raise TypeMismatchInExpression(ast)

        for idx in ast.cell:
            st, idxtype = self.visit(idx, st)
            if type(idxtype) is not IntegerLit: 
                raise TypeMismatchInExpression(ast)

        if len(ast.cell) == len(sym.typ.dimensions):
            return st, sym.typ
        return st, ArrayType(sym.typ.dimensions[len(ast.cell):], sym.typ.typ)

    def visitBinExpr(self, ast : BinExpr, st : SymbolTable):
        st, rtype = self.visit(ast.right, st)
        st, ltype = self.visit(ast.left, st)

        # Both are AutoType, raise Exeption
        if type(rtype) is AutoType and type(ltype) is AutoType: 
            raise TypeMismatchInExpression(ast)
        
        # One is AutoType, infer the other
        if type(rtype) is AutoType:
            Utils.infer(ast.right.name, ltype, st)
        if type(ltype) is AutoType:
            Utils.infer(ast.left.name, rtype, st)

        if ast.op in ["+", "-", "*"]:
            if type(rtype) not in [IntegerType, FloatType] or type(ltype) not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            if FloatType in [type(rtype), type(ltype)]:
                return st, FloatType()
            return st, IntegerType()
        elif ast.op == "/":
            if type(rtype) not in [IntegerType, FloatType] or type(ltype) not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            return st, FloatType()
        elif ast.op == "%":
            if type(rtype) is not IntegerType or type(ltype) is not IntegerType:
                raise TypeMismatchInExpression(ast)
            return st, IntegerType()
        elif ast.op in ["&&", "||"]:
            if type(rtype) is not BooleanType or type(ltype) is not BooleanType:
                raise TypeMismatchInExpression(ast)
            return st, BooleanType()
        elif ast.op == "::":
            if type(rtype) is not StringType or type(ltype) is not StringType:
                raise TypeMismatchInExpression(ast)
            return st, StringType()
        elif ast.op in ["==", "!="]:
            if type(rtype) is not type(ltype):
                raise TypeMismatchInExpression(ast)
            if ltype not in [IntegerType, BooleanType]:
                raise TypeMismatchInExpression(ast)
            return st, BooleanType()
        elif ast.op in ["<", ">", "<=", ">="]:
            # The same type?
            if type(rtype) not in [IntegerType, FloatType] or ltype not in [IntegerType, FloatType]:
                raise TypeMismatchInExpression(ast)
            return st, BooleanType()

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

    def visitFuncCall(self, ast: FuncCall, st: SymbolTable):
        # Check if there is callee
        funcsym = Utils.findSym(ast.name, st)
        if not funcsym: raise Undeclared(Function(), ast.name)
        if type(funcsym) is not FuncSym: raise TypeMismatchInExpression(ast)

        if funcsym.typ == VoidType():  raise TypeMismatchInExpression(ast)
        
        """ Check its args """

        # Different number of arguments
        if len(funcsym.params) != len(ast.args): raise TypeMismatchInExpression(ast)

        # Out but not LHS
        for i in range(len(funcsym.params)):
            if funcsym.params[i].out: 
                if type(ast.args[i]) is not LHS:
                    raise TypeMismatchInExpression(ast)     

        # Infer for param or check param - arg agreements
        for i in range(len(funcsym.params)):
            argType = self.visit(ast.args[i], st)
            if funcsym.params[i].typ == AutoType():
                funcsym.params[i].typ = argType
            elif funcsym.params[i].typ == FloatType():
                if argType == IntegerType(): continue
            elif funcsym.params[i].typ != argType:
                raise TypeMismatchInExpression(ast)    
        return st, funcsym.typ

    def visitAssignStmt(self, ast : AssignStmt, st : SymbolTable):
        st, rtype = self.visit(ast.rhs, st)
        st, ltype = self.visit(ast.lhs, st)

        if type(ltype) in [VoidType, ArrayType]: raise TypeMismatchInStatement(ast)

        if type(ltype) is AutoType:
            if type(rtype) is AutoType: raise TypeMismatchInStatement(ast)
            Utils.infer(ast.lhs.name, rtype, st)
        else:
            """Different types and not Float - Int"""
            if type(rtype) is not type(ltype) and not (type(rtype) is IntegerType and type(ltype) is FloatType):
                raise TypeMismatchInStatement(ast)
            
        return st, AssignStmtType()

    def visitBlockStmt(self, ast : BlockStmt, st : SymbolTable): 
        """Create a new environment"""
        newst = Utils.createScope(st)
        """ Information all got from parent """
        for ele in ast.body:
            # Ignore super or preventDefault
            if type(ele) is CallStmt and ele.name in ['super', 'preventDefault']: continue
            newst, _ = self.visit(ele, newst)
        """Return the original st with some more information"""
        return st, BlockStmtType()

    def visitIfStmt(self, ast : IfStmt, st : SymbolTable):
        """Check cond"""
        _, condtype = self.visit(ast.cond, st)
        if type(condtype) is not BooleanType: raise TypeMismatchInStatement(ast)
        newst, _ = self.visit(ast.tstmt, st)
        if ast.fstmt:
            newst, _ = self.visit(ast.fstmt, st)

        if len(st.fromChildren) == 2: 
            if type(st.fromChildren[0]) is not type(st.fromChildren[1]):
                raise TypeMismatchInStatement(ast)
        if len(st.fromChildren) == 1:
            return Utils.passToParent(st[0], st), IfStmtType()


        return st, IfStmtType()

    # init: AssignStmt, cond: Expr, upd: Expr, stmt: Stmt
    def visitForStmt(self, ast : ForStmt, st : SymbolTable):
        """ Visit assign statement to infer if there is any"""
        st, _ = self.visit(ast.init, ast)
        st, lhs = self.visit(ast.init.lhs, ast)
        st, rhs = self.visit(ast.init.rhs, ast)

        """ One of them is not of IntegerType"""
        if type(rhs) is not IntegerType or type(lhs) is not IntegerType: raise TypeMismatchInStatement(ast)
        """ Make sure cond is BooleanType"""
        st, condType = self.visit(ast.cond, st)
        if type(condType) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        
        """Make sure upd is IntegerType"""
        st, updType = self.visit(ast.upd, st)
        if type(updType) is not IntegerType: raise TypeMismatchInStatement(ast)

        """Pass infor before visiting child stmt"""
        st, stmt = self.visit(ast.stmt, Utils.passToChild(LoopStmtType(), st))
        return st, LoopStmtType()

    def visitWhileStmt(self, ast : WhileStmt, st : SymbolTable):
        st, condType = self.visit(ast.cond, st)
        if type(condType) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        
        st, stmt = self.visit(ast.stmt, Utils.passToChild(LoopStmtType(), st))
        return st, LoopStmtType()

    # cond: Expr, stmt: BlockStmt
    def visitDoWhileStmt(self, ast, st):
        st, condType = self.visit(ast.cond, st)
        if type(condType) is not BooleanType: raise TypeMismatchInStatement(ast)

        st, stmt = self.visit(ast.stmt, Utils.passToChild(LoopStmtType(), st))
        return st, LoopStmtType()
    
    def visitBreakStmt(self, ast : BreakStmt, st : SymbolTable):
        inLoop = False
        for info in st.fromParent:
            if type(info) is LoopStmtType: 
                inLoop = True
                break
        if not inLoop: raise MustInLoop(ast)
        return st, MustInLoopStmtType()

    def visitContinueStmt(self, ast : ContinueStmt, st : SymbolTable):
        inLoop = False
        for info in st.fromParent:
            if type(info) is LoopStmtType: 
                inLoop = True
                break
        if not inLoop: raise MustInLoop(ast)
        return st, MustInLoopStmtType()

    def visitReturnStmt(self, ast : ReturnStmt, st : SymbolTable):
        if ast.expr is not None:
            st, exprtyp =  self.visit(ast.expr, st)
            """ Return type of the return statement expression"""
            return Utils.passToParent(exprtyp, st), ReturnStmt()    
        
        return Utils.passToParent(VoidType(), st), ReturnStmt()  

    def visitCallStmt(self, ast : CallStmt, st : SymbolTable):
        # Check if there is callee
        funcsym = Utils.findSym(ast.name, st)
        if not funcsym: raise Undeclared(Function(), ast.name)
        if type(funcsym) is not FuncSym: raise TypeMismatchInExpression(ast)
        
        """ Check its args """
        # Different number of arguments
        if len(funcsym.params) != len(ast.args): raise TypeMismatchInExpression(ast)

        # Out but not LHS
        for i in range(len(funcsym.params)):
            if funcsym.params[i].out: 
                if type(ast.args[i]) is not LHS:
                    raise TypeMismatchInExpression(ast)     

        # Infer for param or check param - arg agreements
        for i in range(len(funcsym.params)):
            argType = self.visit(ast.args[i], st)
            if funcsym.params[i].typ == AutoType():
                funcsym.params[i].typ = argType
            elif funcsym.params[i].typ == FloatType():
                if argType == IntegerType(): continue
            elif funcsym.params[i].typ != argType:
                raise TypeMismatchInExpression(ast)    
        return st, CallStmtType()

    def visitVarDecl(self, ast: VarDecl, st: SymbolTable):
        """Check if there is the same name in scope 0"""
        for sym in st.env[0]:
            if sym.name == ast.name: raise Redeclared(Variable(), ast.name)

        """Check semantics"""
        # There is no init
        if not ast.init:
            if ast.typ == AutoType():
                raise Invalid(Variable(), ast.name)
            st.env[0].append(VarSym(ast.name, ast.typ))
            return st, DeclType()
        # There is init
        else:
            st, inityp = self.visit(ast.init, st)
            if type(ast.typ) is AutoType:
                st.env[0].append(VarSym(ast.name, inityp))
                return st, DeclType()
            else:
                st, inittyp = self.visit(ast.init,st)
                if type(ast.typ) is not type(inittyp):
                    raise TypeMismatchInVarDecl(ast)
                if type(ast.typ) is ArrayType():
                    if ast.typ != inityp:
                        if ast.typ.dimensions != inityp.dimensions:
                            raise TypeMismatchInVarDecl(ast)
                        if ast.typ.typ == AutoType():
                            st.env[0].append(VarSym(ast.name, inityp.typ))
                            return st
                        raise TypeMismatchInVarDecl(ast)
                st.env[0].append(VarSym(ast.name, ast.typ))
                return st, DeclType()

    def visitParamDecl(self, ast: ParamDecl, st: SymbolTable): pass

    # name: str, return_type: Type, params: List[ParamDecl], inherit: str or None, body: BlockStmt
    def visitFuncDecl(self, ast: FuncDecl, st: SymbolTable):
        # If there is already the same name, raise
        for sym in st.env[0]:
            if sym.name == ast.name:
                raise Redeclared(Function(), ast.name)
        """ If this function inherits """
        funcsym = FuncSym(ast.name, ast.return_type, 
                          list
                          (map
                           (lambda paramdecl: ParaSym(paramdecl.name, paramdecl.typ, paramdecl.out, paramdecl.inherit), ast.params,)
                        ),
                    )
        

        st.env[0].append(funcsym)
        """Create a new scope"""
        newst = Utils.createScope(st)
        if ast.inherit:
            # Find its parent, if there is not raise Undeclared
            parentsym = None
            for funcsym in st.funcprototype:
                if ast.inherit == funcsym.name: 
                    parentsym = funcsym
                    break
            if not parentsym: raise Undeclared(Function(), ast.inherit)

            """ Append its parent's inherit params into scope 0 """
            for parentparam in parentsym.params:
                if parentparam.inherit:
                    newst.env[0].append(parentparam)

            """ Traverse its params """
            # If same name as parent's raise Invalid
            for param in funcsym.params:
                if Utils.findSym(param.name, st): raise Invalid(Parameter(), param.name)
            # If same nams as its own raise Redeclared
            for param in funcsym.params:
                if Utils.findSym(param.name, st): raise Redeclared(Parameter(), param.name)
                newst.env[0].append(param)
        
            """Traverse first statement"""
            # Nothing or not in ['prevendefaut', 'super'], does not have name 
            if len(ast.body.body) == 0 or not hasattr(ast.body.body[0], 'name') or ast.body.body[0].name not in ['preventDefault', 'super']: 
                if len(parentsym.params) != 0: raise TypeMismatchInExpression()
            elif ast.body.body[0].name == 'super':
                newst, _ = self.visit(CallStmt(parentsym.name, ast.body.body[0].args), newst)

            """ Visit body as a normal Blockstmt """
            newst, _ = self.visit(ast.body, newst)
        else:
            """Traverse its own params"""
            for param in funcsym.params:
                if Utils.findSym(param.name, st): raise Redeclared(Parameter(), param.name)
                newst.env[0].append(param)
            
            if len(ast.body.body) > 0 and type(ast.body.body[0]) is CallStmt and ast.body.body[0].name in ['preventDefault', 'super']:
                raise InvalidStatementInFunction(ast.name)
                

            """Traverse its body"""
            newst, _ = self.visit(ast.body, newst)

        return st, DeclType()

    # decls: List[Decl]
    def visitProgram(self, ast : Program, st : SymbolTable):
        st = SymbolTable()
        st = PreCheck().visit(ast, st)
        for decl in ast.decls:
            st, _ = self.visit(decl, st)