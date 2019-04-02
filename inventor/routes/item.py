from flask import session, redirect, url_for, render_template, request

from inventor import app, TYPE_REGEXES, InvalidUserSuppliedValue
from inventor.misc import get_new_entity_values


@app.route("/i/<name>", methods=["GET", "POST"])
def route_item(name):
    # logged in?
    if not session.get("logged_in"):
        return redirect(url_for("route_login"))
    item = app.db.get(app.db.key("item", name))
    if item is None:
        return render_template("error.html", error="This item does not exist"), 404
    namespace = app.db.get(app.db.key("namespace", item["namespace"]))
    if request.method == "GET":
        if item["namespace"] not in session["viewable_namespaces"]:
            return render_template("error.html", error="You do not have permission to view this item."), 403
        return render_template("item.html", item=item, namespace=namespace, zip=zip, TYPE_REGEXES=TYPE_REGEXES,
                               editable=item["namespace"] in session["editable_namespaces"])
    else:
        if item["namespace"] not in session["editable_namespaces"]:
            return render_template("error.html", error="You do not have permission to edit this item."), 403
        for field in namespace["field_names"]:
            if "field_" + field not in request.form:
                return f"Missing field \"{field}\"", 400
        try:
            values = get_new_entity_values(namespace["field_names"], namespace["field_types"])
        except InvalidUserSuppliedValue as e:
            return "Invalid value \"{v}\" for field \"{k}\"".format(v=e.value, k=e.key), 400
        # save the item
        item["fields"] = values
        app.db.put(item)
        return redirect(request.base_url, 303)
