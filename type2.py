from functools import reduce


class Symbol:
    def __init__(self, name, typ, val, params=None):
        self.name = name
        self.typ = typ
        self.val = val
        self.params = params
        self.isFunction = True if params else False


class STManipulator:
    def append(st, decl):
        if type(decl) is VarDecl:
            st[0].append(Symbol(decl.name, decl.typ, None))
        elif type(decl) is ConstDecl:
            st[0].append(Symbol(decl.name, None, decl.val))
        else:
            st[0].append(Symbol(decl.name, None, None, decl.param))

    def contains(st, name):
        for scope in st:
            for sym in scope:
                if sym.name == name:
                    return sym
        return None

    def containslocal(st, name):
        for sym in st[0]:
            if sym.name == name:
                return True
        return False


class StaticCheck(Visitor):

    def visitProgram(self, ctx: Program, st):
        st = reduce(lambda st, decl: self.visit(decl, st), ctx.decl, [[]])
        self.visit(ctx.exp, st)

    def visitVarDecl(self, ctx: VarDecl, st):
        if STManipulator.containslocal(st, ctx.name):
            raise RedeclaredVariable(ctx.name)
        STManipulator.append(st, ctx)
        return st

    def visitBinOp(self, ctx: BinOp, o):
        ltype = self.visit(ctx.e1, o)
        rtype = self.visit(ctx.e2, o)
        ret = ltype
        if type(ltype) != type(rtype):
            if BoolType in [type(ltype), type(rtype)]:
                raise TypeMismatchInExpression(ctx)
            else:
                ret = FloatType()
        if ctx.op in ['+', '-', '*', '/']:
            if type(ret) is BoolType:
                raise TypeMismatchInExpression(ctx)
            elif ctx.op == '/':
                return FloatType()
            else:
                return ret
        elif ctx.op in ["&&", "||"]:
            if type(ret) is not BoolType:
                raise TypeMismatchInExpression(ctx)
            else:
                return ret
        elif type(ltype) is not type(rtype):
            raise TypeMismatchInExpression(ctx)
        else:
            return BoolType()

    def visitUnOp(self, ctx: UnOp, o):
        typ = self.visit(ctx.e, o)
        if (ctx.op == "-" and type(typ) is BoolType) or (ctx.op == "!" and type(typ) is not BoolType):
            raise TypeMismatchInExpression(ctx)
        else:
            return typ

    def visitIntLit(self, ctx: IntLit, o): return IntType()

    def visitFloatLit(self, ctx, o): return FloatType()

    def visitBoolLit(self, ctx, o): return BoolType()

    def visitId(self, ctx, st):
        sym = STManipulator.contains(st, ctx.name)
        if not sym:
            raise UndeclaredIdentifier(ctx.name)
        return sym.typ
