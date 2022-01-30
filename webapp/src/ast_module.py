import ast


class Visitor(ast.NodeVisitor):
    _blacklist = {'os', 'sys', 'subprocess', 'builtins', 'shutil', 'open', 'eval',
                  'exec', 'flask', 'redis', 'celery', '__import__', '__builtins__'}
    errors = []

    def rules(self, node):
        # open(), eval() i.e.
        if isinstance(node, ast.Call) and not isinstance(node.func, ast.Attribute)\
                and node.func.id in Visitor._blacklist:
            Visitor.errors.append(node.func.id)

        # __builtins__.exec
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.value.id in Visitor._blacklist:
            Visitor.errors.append(node.func.value.id)

        # getattr(__builtins__, 'exec')
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) \
                and node.value.args \
                and isinstance(node.value.args[0], ast.Name) and \
                node.value.args[0].id in Visitor._blacklist:
            Visitor.errors.append(node.value.args[0].id)

        # import os
        elif isinstance(node, ast.Import) and node.names[0].name in Visitor._blacklist:
            Visitor.errors.append(node.names[0].name)

        # from os import chdir
        elif isinstance(node, ast.ImportFrom) and node.module in Visitor._blacklist:
            Visitor.errors.append(node.module)

        # a = __import__, a('os')
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            if node.value.func.id in Visitor._blacklist:
                Visitor.errors.append(node.value.func.id)

        # __import__('os')
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Name):
            if node.value.id in Visitor._blacklist:
                Visitor.errors.append(node.value.id)

    def visit(self, node: ast.AST):
        self.rules(node)
        self.generic_visit(node)


def check_code(code):
    node = ast.parse(code)
    Visitor().visit(node)
    to_return = Visitor.errors
    Visitor.errors = []
    return to_return


if __name__ == '__main__':
    print(check_code("""
a = 'o' + 's'
__import__(a)
"""))
