from flask import Flask
from google.cloud import datastore
from . import ids
import secrets
from datetime import datetime

app = Flask("inventor", static_url_path="", static_folder="../static", template_folder="../templates")
USERNAME = "admin"
PASSWORD = "password"
ITEMS_PER_PAGE = 50
ITEMS = {"test": [{"wassap": 1234, "yo": True}]}
DEFAULT_COLUMNS = {"Quantity": "quantity", "Description": "description"}
TYPE_FUNCS = {"string": str, "integer": int, "float": float, "datetime": datetime.fromisoformat}
DB_OPERATORS = {"≤": "<=", "≥": ">=", "≠": "!=", "lt": "<", "lte": "<=", "le": "<=", "gt": ">", "gte": ">=",
                "ge": ">=", "eq": "=", "neq": "!=", "ne": "!="}

# these are CLIENT SIDE (browser) validation only!
# DON'T, DON'T, DON'T, DON'T! RELY! ON! THIS
TYPE_REGEXES = {"string": r".*",  # any string
                # python int syntax
                "integer": r"[+\-]?(0[bB][01]+|0[oO][0-7]+|0[xX][0-9a-fA-F]+|[0-9]+)",
                # python float syntax
                "float": r"[+\-]?(0[bB][01]*\.?[01]*|0[oO][0-7]*\.?[0-7]*|[0-9]*\.?[0-9]*([eE][0-9a-fA-F]+)?|"
                         r"0[xX][0-9a-fA-F]*\.?[0-9a-fA-F]*([eE][0-9a-fA-F]+)?)",
                # iso format
                "datetime": r"[0-9]{4}-([0-9]{2}|1[012])-([012][0-9]|3[012])T"
                            r"([01][0-9]|2[0-4])(:[0-5][0-9]){2}\.[0-9]{,8}"}

FILTERS = {}


class Inventor(Flask):
    def __init__(self):
        super(Inventor, self).__init__("inventor", static_url_path="", static_folder="../static",
                                       template_folder="../templates")
        self.db = datastore.Client()


class InvalidUserSuppliedValue(ValueError):
    def __init__(self, original_exception, key=None, value=None, msg=None):
        self.key = key
        self.value = value
        self.original_exception = original_exception
        self.msg = msg


def init(debug):
    import inventor.routes
    app.debug = debug
    app.secret_key = "123456789" if app.debug else secrets.token_bytes()
