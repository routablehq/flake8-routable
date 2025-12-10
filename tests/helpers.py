# Python imports
import ast
import io
import tokenize

# Internal imports
from flake8_routable import Plugin


def results(s):
    return {
        "{}:{}: {}".format(*r)
        for r in Plugin(ast.parse(s), list(tokenize.generate_tokens(io.StringIO(s).readline))).run()
    }
