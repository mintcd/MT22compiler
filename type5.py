from functools import reduce


class IntType:
    pass


class FloatType:
    pass


class BoolType:
    pass


class NoneType:
    pass


class VarSym:
    def __init__(self, name, typ=NoneType(), isParam=None):
        self.name = name
        self.typ = typ
        self.isParam = isParam


class FuncSym:
    def __init__(self, name, paramTypes=[]):
        self.name = name
        self.paramTypes = paramTypes


class Scope:
    def __init__(self, inFunction=None):
        self.varsyms = []
        self.funcsyms = []
        self.inFunction = inFunction


class SymbolTable:
    @classmethod
    def contains(cls, st, name):
        for scope in st.scopes:
            for sym in scope.varsyms:
                if name == sym.name:
                    return sym
            for sym in scope.funcsyms:
                if name == sym.name:
                    return sym
        return None

    @classmethod
    def containslocal(cls, st, name):
        for sym in st.scopes[0].varsyms:
            if sym.name == name:
                return sym
        for sym in st.scopes[0].funcsyms:
            if sym.name == name:
                return sym
        return None

    @classmethod
    def append(cls, st, decl):
        if type(decl) is VarDecl:
            st.scopes[0].varsyms.append(VarSym(decl.name))
        if type(decl) is FuncDecl:
            st.scopes[0].funcsyms.append(
                FuncSym(decl.name, [NoneType()]*len(decl.param)))
        if type(decl) is

    @classmethod
    def newScopeST(cls, st, funcName):
        return SymbolTable([Scope(funcName)] + st.scopes)

    @classmethod
    def infer(cls, st, name, typ):
        sym = contains(st, name)
        sym.typ = typ

    def __init__(self, scopes=[Scope()]):
        self.scopes = scopes


class StaticCheck(Visitor):

    # decl:List[Decl],stmts:List[Stmt]
    def visitProgram(self, ctx: Program, st):
        st = SymbolTable()
        for decl in ctx.decl:
            if type(decl) is VarDecl:
                st = self.visit(decl, st)

        for decl in ctx.decl:
            if type(decl) is FuncDecl:
                st = self.visit(decl, st)

        for stmt in ctx.stmts:
            self.visit(stmt, st)

    # name:str
    def visitVarDecl(self, ctx: VarDecl, st):
        if SymbolTable.containslocal(st, ctx.name):
            raise Redeclared(ctx)
        SymbolTable.append(st, ctx)
        return st

    # name:str,param:List[VarDecl],local:List[Decl],stmts:List[Stmt]
    def visitFuncDecl(self, ctx: FuncDecl, st):
        if SymbolTable.containslocal(st, ctx.name):
            raise Redeclared(ctx)
        SymbolTable.append(st, ctx)
        sym = SymbolTable.contains(st, ctx.name)

        newst = SymbolTable.newScopeST(st)
        newst = reduce(lambda _, param: self.visit(param, _), ctx.param, newst)
        newst = reduce(lambda _, param: self.visit(param, _), ctx.local, newst)

        for stmt in ctx.stmts:
            self.visit(stmt, newst)

        return st

    # name:str,args:List[Exp]
    def visitCallStmt(self, ctx: CallStmt, st):
        print("Callee", ctx.name)
        sym = SymbolTable.contains(st, ctx.name)
        if not sym:
            raise UndeclaredIdentifier(ctx.name)

        for i in range(len(ctx.args)):
            argType = self.visit(ctx.args[i], st)
            print("Argtype", type(argType))
            print("Paramtype", type(sym.paramTypes[i]))
            if type(sym.paramTypes[i]) is NoneType:
                if type(argType) is NoneType:
                    TypeCannotBeInferred(ctx)
                sym.paramTypes[i] = argType
            if type(sym.paramTypes[i]) is not type(argType):
                raise TypeMismatchInStatement(ctx)
            return st

    # lhs:Id,rhs:Exp
    def visitAssign(self, ctx: Assign, st):
        rtype = self.visit(ctx.rhs, st)
        ltype = self.visit(ctx.lhs, st)

        if type(rtype) is IntType:
            print(type(ltype), type(rtype))

        sym = SymbolTable.contains(st, ctx.lhs.name)

        if type(ltype) is NoneType and type(rtype) is NoneType:
            raise TypeCannotBeInferred(ctx)
        elif type(ltype) is NoneType:
            sym.typ = rtype
            if (sym.isParam):
                funcsym = SymbolTable.contains(st, st[0].inFunction)
                funcsym.
        elif type(ltype) is not type(rtype):
            raise TypeMismatchInStatement(ctx)

        return st

    def visitIntLit(self, ctx: IntLit, o): return IntType()
    def visitFloatLit(self, ctx, o): return FloatType()
    def visitBoolLit(self, ctx, o): return BoolType()

    def visitId(self, ctx, st):
        sym = SymbolTable.contains(st, ctx.name)
        if not sym:
            raise UndeclaredIdentifier(ctx.lhs.name)
        return sym.typ
