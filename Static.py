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
        funcsym = SymbolTable.checkUndeclared(ast.name, st)
        if type(funcsym.typ) is not VoidType:
            raise TypeMismatchInStatement(ast)
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
    def visitVarDecl(self, ast, st):
        symbol = SymbolTable.checkRedeclared(ast.name, st)
        if type(ast.typ) is AutoType:
            if ast.init is None:
                raise Invalid(Variable(), ast.name)
        return

    # name: str, typ: Type, out: bool = False, inherit: bool = False
    def visitParamDecl(self, ast, param):
        pass

    # name: str, return_type: Type, params: List[ParamDecl], inherit: str or None, body: BlockStmt
    def visitFuncDecl(self, ast, param):
        pass

    # decls: List[Decl]
    def visitProgram(self, ast, st):
        st = []
        for decl in ast.decls:
            st = self.visit(decl, st)