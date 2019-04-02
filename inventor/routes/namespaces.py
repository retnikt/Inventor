from flask import session, redirect, url_for, render_template

from inventor import app


@app.route("/n/")
def route_namespace_select():
    if not session.get("logged_in"):
        return redirect(url_for("route_login"))
    return render_template("namespace_select.html",
                           namespaces=session["viewable_namespaces"])


@app.route("/n/<namespace>/")
def route_namespace(namespace):
    # logged in?
    if not session.get("logged_in"):
        return redirect(url_for("route_login"))
    # has permission?
    if namespace not in session["viewable_namespaces"]:
        return render_template("error.html", error="You do not have permission to view this namespace."), 403
    namespace = app.db.get(app.db.key("namespace", namespace))
    if namespace is None:
        return render_template("error.html", error="This namespace does not exist."), 404
    return render_template("namespace.html", n=namespace, zip=zip)
