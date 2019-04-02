from flask import request, render_template, session, redirect

from inventor import app, USERNAME, PASSWORD


@app.route("/login", methods=["GET", "POST"])
def route_login():
    if request.method == "GET":
        return render_template("login.html")
    if not request.form.get("username"):
        return render_template("login.html", error="Please provide a username"), 400
    if not request.form.get("password"):
        return render_template("login.html", error="Please provide a password"), 400
    # TODO no hardcoded user creds
    if request.form.get("username") == USERNAME and request.form.get("password") == PASSWORD:
        session["logged_in"] = True
        session["viewable_namespaces"] = ["test_ns"]
        session["creatable_namespaces"] = ["test_ns"]
        session["editable_namespaces"] = ["test_ns"]
        return redirect(request.url_root + "n/")

    return render_template("login.html", error="Incorrect username or password"), 403
