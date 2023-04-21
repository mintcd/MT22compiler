from main.mt22.checker.StaticChecker import SymbolTable, StaticChecker
from main.mt22.utils.AST import *

st, typ = StaticChecker.visitArrayLit(ArrayLit({{4,4,4},{4,4,4}}), SymbolTable())

print(typ)