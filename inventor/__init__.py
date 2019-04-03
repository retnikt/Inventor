from flask import Flask, session, request, redirect, url_for, render_template
from google.cloud import datastore

from . import ids

from datetime import datetime
from functools import wraps
import secrets

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

    def logged_in(self, func):
        # copy function attributes
        @wraps(func)
        def inner(*args, **kwargs):
            if not session.get("logged_in"):
                return redirect(url_for("login"))
            return func(*args, **kwargs)
        return inner

    def permission(self, *args, **kwargs):
        """
        decorator [factory] to ensure the user is logged in and has permissions
        :param args: individual permissions they gotta have
        e.g. if your route is
        ```
        @app.permission("exist")
        @app.route("/foo")
        def foo():
            ...
        ```
        then the user would have to have "exist" in their permission list
        :param kwargs: keys of the function call that have to be in the users VALUE permission list.
        e.g. if your route is
        ```
        @app.permission(bar="allowed_bars")
        @app.route("/foo/<bar>")
        def foo(bar):
            ...
        ```
        then the user needs to be logged in and have the BAR value (that they provided)
         in their permission list for "allowed_bars".
        :return: decorator that ensures the above
        """
        def decorator(func):
            # obviously they have to be logged in to do this
            @self.logged_in
            # copy function attributes
            @wraps(func)
            def inner(*pass_args, **pass_kwargs):
                if request.method in ("GET", "HEAD"):
                    # GET request so they are trying to view a page
                    msg = "You do not have permission to view this page."
                else:
                    # some other method so they are trying to perform an action
                    msg = "You do not have permission to perform this action."
                for perm in args:
                    if perm not in session["permissions"]:
                        return render_template("error.html", error=msg), 403
                for value, perm in kwargs.items():
                    if pass_kwargs[value] not in session[perm]:
                        return render_template("error.html", error=msg), 403
                return func(*pass_args, **pass_kwargs)
            return inner
        return decorator


class InvalidUserSuppliedValue(ValueError):
    def __init__(self, original_exception, key=None, value=None, msg=None):
        """
        the user done fucked up
        :param original_exception: original exception to reraise if in debug mode
        :param key: which key they done fucked up
        :param value: what they put that was fucked uo
        :param msg: extra info about the fuck-up
        """
        self.key = key
        self.value = value
        self.original_exception = original_exception
        self.msg = msg


app = Inventor()


def init(debug):
    import inventor.routes
    app.debug = debug
    app.secret_key = "123456789" if app.debug else secrets.token_bytes()
