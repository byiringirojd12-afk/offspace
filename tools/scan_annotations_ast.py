import ast
from pathlib import Path

p = Path('backend/database/models.py')
src = p.read_text()
mod = ast.parse(src)

class Visitor(ast.NodeVisitor):
    def visit_AnnAssign(self, node):
        # node.annotation is AST for annotation
        if isinstance(node.annotation, ast.BinOp) and isinstance(node.annotation.op, ast.BitOr):
            print('Found PEP604 at line', node.lineno)
            print('  target:', ast.unparse(node.target))
            print('  annotation:', ast.unparse(node.annotation))
        # also check Subscript like Mapped[str | None]
        if isinstance(node.annotation, ast.Subscript):
            ann = node.annotation.slice
            # for Python ast, ann may be ast.BinOp inside Subscript
            if isinstance(ann, ast.BinOp) and isinstance(ann.op, ast.BitOr):
                print('Found PEP604 inside Subscript at line', node.lineno)
                print('  target:', ast.unparse(node.target))
                print('  annotation slice:', ast.unparse(ann))
        self.generic_visit(node)

Visitor().visit(mod)
