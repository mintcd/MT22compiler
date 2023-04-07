from functools import reduce
import copy

class IntType: pass
class FloatType: pass

class Symbol:
    def __init__(self, name):
        self.name = name
        
class SymbolTable:
    def __init__(self, scopes = []):
        self.scopes = scopes
        
    def contains(self, name):
        return name in self.scopes
        
    def append(self, name):
        return SymbolTable(self.scopes + [name])

class StaticCheck(Visitor):

    def visitProgram(self,ctx:Program,st):
        reduce(lambda st,decl: self.visit(decl,st), ctx.decl, SymbolTable())

    def visitVarDecl(self,ctx:VarDecl,st):
        if st.contains(ctx.name): raise RedeclaredDeclaration(ctx.name)
        return st.append(ctx.name)

    def visitConstDecl(self,ctx:ConstDecl,st):
        if st.contains(ctx.name): raise RedeclaredDeclaration(ctx.name)
        return st.append(ctx.name)
        
    def visitIntLit(self,ctx:IntLit,o:object): return IntType()





from functools import reduce

class IntType: pass
class FloatType: pass

class Symbol:
    def __init__(self, name):
        self.name = name
        
class SymbolTable:
    def __init__(self, scopes = [[]]):
        self.scopes = scopes
        
    def contains(self, name):
        for scope in self.scopes:
            for sym in scope:
                if sym.name == name: return sym
        return None
        
    def containslocal(self, name):
        for sym in self.scopes[0]:
            if sym.name == name: return True
        return False
        
    def append(self, name):
        self.scopes[0] += [Symbol(name)]
        return SymbolTable(self.scopes)
        
    def newscopeST(self):
        return SymbolTable([[]] + self.scopes)

class StaticCheck(Visitor):

    def visitProgram(self,ctx:Program,st):
        reduce(lambda st,decl: self.visit(decl,st), ctx.decl, SymbolTable())

    def visitVarDecl(self,ctx:VarDecl,st):
        if st.containslocal(ctx.name): raise RedeclaredVariable(ctx.name)
        return st.append(ctx.name)

    def visitConstDecl(self,ctx:ConstDecl,st):
        if st.containslocal(ctx.name): raise RedeclaredConstant(ctx.name)
        return st.append(ctx.name)
    
    def visitFuncDecl(self,ctx:FuncDecl,st):
        if st.containslocal(ctx.name): raise RedeclaredFunction(ctx.name)
        newst = st.newscopeST()
        newst = reduce(lambda _,ele: self.visit(ele,_), ctx.param, newst)
        newst = reduce(lambda _,ele: self.visit(ele,_), ctx.body, newst)
        return st.append(ctx.name)
        
        
        
    def visitIntLit(self,ctx:IntLit,o:object): return IntType()