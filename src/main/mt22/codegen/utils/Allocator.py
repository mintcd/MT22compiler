from Analyzer import LiveRangeAnalyzer

class Allocator:
    def __init__(self, ast):
        self.ast = ast
        self.analyzer = LiveRangeAnalyzer()
        self.st = self.analyzer.st
    
    def chaitin():
        pass