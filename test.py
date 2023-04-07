Assign(Id("z"),
       BinOp("&&",
             BinOp(">",BinOp("-",Id("x"),IntLit(3)),UnOp("-",Id("y"))),
             UnOp("!",Id("y"))))