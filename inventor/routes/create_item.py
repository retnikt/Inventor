from flask import session, redirect, url_for, render_template, request
from google.cloud import datastore

from inventor import ids, app, InvalidUserSuppliedValue
from inventor.misc import get_new_entity_values


def create_item(values, n):
    # create key
    name = ids.gen_key()
    # make sure it doesn't already exist
    while app.db.get(app.db.key("item", name)):
        name = ids.gen_key()
    e = datastore.Entity(app.db.key("item", name))
    e["namespace"] = n.key.name
    e["fields"] = values
    app.db.put(e)
    return name


@app.route("/n/<n>/create", methods=["GET", "POST"])
def route_create_item(n):
    # logged in?
    if not session.get("logged_in"):
        return redirect(url_for("route_login"))
    # has permission?
    if 0 and n not in session["creatable_namespaces"]:
        return render_template("error.html", error="You do not have permission to create items in this namespace."), 403
    # exists?
    n = app.db.get(app.db.key("namespace", n))
    if n is None:
        return render_template("error.html", error="This namespace does not exist."), 404
    if request.method == "GET":
        return render_template("new_item.html", n=n, zip=zip)
    else:
        for field in n["field_names"]:
            print(request.args)
            if "field_" + field not in request.form:
                return f"Missing field \"{field}\"", 400
        try:
            values = get_new_entity_values(n["field_names"], n["field_types"])
        except InvalidUserSuppliedValue as e:
            if app.debug:
                raise e.original_exception
            return "Invalid value \"{v}\" for field \"{k}\"".format(v=e.value, k=e.key), 400
        name = create_item(values, n)
        return redirect(request.url_root + "i/" + name)
