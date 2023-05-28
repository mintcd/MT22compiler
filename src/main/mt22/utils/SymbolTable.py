from AST import *
import numpy as np

class Symbol:
    def __init__(self, name, typ, value): 
        self.name = name
        self.typ = typ
        self.value = value
        
class VarSym(Symbol):
    def __init__(self, name : str, typ : Type, value = None):
        super().__init__(name, typ)
class ParamSym(Symbol):
    def __init__(self, name : str, typ : Type, value = None):
        super().__init__(name, typ)
class FuncSym(Symbol):
    # Type cannot be auto for simplicity.
    def __init__ (self, name : str, typ : Type, body : BlockStmt, params : List[ParamSym] = []):
        super().__init__(name, typ)
        self.params = params
        self.body = body
        
class SymbolTable:
    def __init__(self, entry : FuncSym = None, funcs : List[FuncSym] = [], vars : List[VarSym] = []):
        self.entry = entry
        self.funcs = funcs
        self.vars = vars