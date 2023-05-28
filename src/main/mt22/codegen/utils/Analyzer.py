from Visitor import *
from StaticError import *
from AST import *
from SymbolTable import *
from functools import reduce
import networkx as nx

""" Generate a runtime SymbolTable object """
class Preprocessor(Visitor):
    def __init__(self, ast : Program):
        self.ast = ast
    
    def getSymbolTable(self):
        st = SymbolTable()
        for decl in self.ast.decls:
            if type(decl) is VarDecl:
                st.vars.append(VarSym(decl.name, decl.typ, decl.init))
            elif type(decl) is FuncDecl:
                if decl.name == 'main':
                    st.entry = FuncSym('main', VoidType(), decl.body, [])
                else: st.funcs.append(FuncSym(decl.name, decl.typ, decl.body, decl.params))
        return st

class SubGraph:
    def __init__(self, begin : int = 0):
        self.begin = begin
        self.vertices = [[]]
        self.edges = []
        self.end = [0]
        
    def addVertex(self, v : int):
        self.vertices.append(v)
    
    def addEdge(self, u : int, v : int):
        self.edges.append((u, v))
        
        
class BasicBlockGenerator(Visitor):
    def __init__(self, ast : Program):
        self.ast = ast
        self.st = Preprocessor(ast).getSymbolTable() 
        
        # Each block is a list of Stmt, the same as BlockStmt
        self.blocks = []
        
        self.currentValue = 0
        
    def newBlock(self):
        self.currentValue += 1
        self.blocks.append([])
        
        return self.currentValue
        
    """ Visitor - blockNum object is the current block at the time visiting this AST node"""
    
    def visitFuncDecl(self, ast : FuncDecl, subgraph : SubGraph):
        
        for param in ast.params:
            subgraph.addVertex
        
        for stmt in ast.body:
            # Add parameter declaration to the block
            self.visit(ast.stmt, subgraph)
    
    def visitAssignStmt(self, ast : AssignStmt, blockNum : int):
        
        subgraph = SubGraph(blockNum)
        
        # No more block is added
        if type(ast.rhs) in [IntegerLit, FloatLit, StringLit, BooleanLit, ArrayLit]:
            self.blocks[blockNum].append(ast)
        
        else: 
            rhsSubGraph = self.visit(ast.rhs)

            
            
        
        

class ControlFlowGraphGenerator(Visitor):
    
    class Node:
        def __init__(self, stmts, parent = None, children = None):
            self.stmts = stmts
            self.parent = parent
            self.children = children
            
    
    def __init__(self, ast : Program):
        self.ast = ast
        self.preprocessor = Preprocessor(self.ast)
        self.st = self.preprocessor.st
        
        self.currentvar = 0
        
    def generate(self):
        mainFunction = self.st.entry
        graph = nx.DiGraph()
        graph = reduce(lambda _, ele: self.visit(ele, graph), mainFunction.decls)
    
    """Retrievers"""
    def getNextVar(self):
        self.currentvar += 1
        return self.currentvar
    

    """ Only actual statements modify the graph """
    
    def visitBlockStmt(self, ast, graph):
        pass
    
    def visitAssignStmt(self, ast, graph):
        pass
    
    def visitIfStmt(self, ast, graph):
        pass 
    
    def visitForStmt(self, ast, graph):
        pass 
    
    def visitWhile(self, ast, graph):
        pass 
    
    def visitDoWhile(self, ast, graph):
        pass 
    
    def visitCallStmt(self, ast, graph):
        pass 
    
    """ In another block only """
    def visitBreak(self, ast, graph):
        pass 
    
    def visitContinueStmt(self, ast, graph):
        pass 
    
    def visitReturnStmt(self, ast, graph):
        pass 
    
    def visitIntegerLit(self, ast, graph): pass
    
    
class LiveRangeAnalyzer(Visitor):
    def __init__(self, ast):
        self.ast = ast
        self.CFGGenerator = ControlFlowGraphGenerator()
        self.CFG = self.CFGGenerator.generate()
        self.st = self.CFGGenerator.st
        
    def visitProgram(self, ast : Program, liveranges):
        mainDecl = Preprocessor.findMain(self.ast)
        
    def calculateLiveRange():
        pass