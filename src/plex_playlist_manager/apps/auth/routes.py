from . import auth


@auth.route("/login")
def login():
    return "Login Page"


@auth.route("/logout")
def logout():
    return "Logout Page"
