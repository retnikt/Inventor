from flask import request, session, redirect, url_for, render_template

from inventor import DB_OPERATORS, FILTERS, InvalidUserSuppliedValue, app, DEFAULT_COLUMNS


def get_items(namespace):
    custom_filters = []
    # goddammit google fix your type checking
    # noinspection PyTypeChecker
    q = app.db.query(kind="item", filters=(("namespace", "=", namespace),))
    # apply database-level filters
    for filter_name, value in request.args:
        # make sure the filter is a valid thing (format is "key:operator")
        if filter_name.count(":") != 1:
            continue
        key, operator = filter_name.split(":")
        if operator.lower() not in DB_OPERATORS:
            # not a database-level filter
            custom_filters.append((key, operator, value))
            continue
        # datastore operators need to be expanded
        operator = DB_OPERATORS.get(operator.lower(), operator)
        q.add_filter(key, operator, value)
    # get items from database
    i = q.fetch()
    # apply the other filters
    for key, operator, value in custom_filters:
        func = FILTERS.get(key)
        if func is not None:  # make sure this filter actually exists
            filter_func = func()
            try:
                i = filter(filter_func, i)
            except InvalidUserSuppliedValue as e:
                e.key = key
                e.value = value
                raise e
    return list(i)


@app.route("/n/<namespace>/i/<int:start>/<int:end>/")
@app.route("/n/<namespace>/i/<int:start>/", defaults={"end": -1})
@app.route("/n/<namespace>/i/", defaults={"start": 0, "end": -1})
def route_items(namespace, start, end):
    # logged in?
    if not session.get("logged_in"):
        return redirect(url_for("route_login"))
    # has permission?
    if namespace not in session["viewable_namespaces"]:
        return render_template("error.html", error="You do not have permission to view this namespace."), 403
    # get the items, applying any filters
    try:
        i = get_items(namespace)
    except InvalidUserSuppliedValue as e:
        return "Invalid value \"{value}\" for filter {key}: {msg}".format(**vars(e)), 400
    # pagination
    if start >= len(i):
        return render_template("items.html", message="No items could be found.", items=[], n=namespace,
                               columns=session.get("columns", DEFAULT_COLUMNS))
    if end >= len(i):
        end = -1
    return render_template("items.html", items=i[start:end], repr=repr, n=namespace,
                           columns=session.get("columns", DEFAULT_COLUMNS),
                           quick_actions=[("pencil-alt", ""), ("trash-alt", "delete")])
