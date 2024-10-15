
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash   # Werkzeug is a comprehensive WSGI web application library. 
#--> WSGI = Web Server Gateway Interface used to connect web servers to web applications or frameworks from Python

### Create a Blueprint named 'auth'. ###
# Like the application object, the blueprint needs to know where it’s defined, so __name__ is passed as the second argument. 
# The url_prefix will be prepended to all the URLs associated with the blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')    

users = [{'id':1,'name':'administrator', 'password':'Cheeserius777', 'admin':1}]
# Convert all passwords to hash
for user in users:
    user['password'] = generate_password_hash(user['password'])

### LOGIN View (View = URL/Request Handler) ###
@bp.route('/login', methods=('GET', 'POST'))   # When the user visits /auth/login, the login view will return the HTML with a form for them to fill out
def login():
    if request.method == 'POST':    # If the user submitted the form, request.method will be 'POST'. In this case, start validating the input
        username = request.form['username'] # Input from the form
        password = request.form['password']
        error = None
        if username not in [user['name'] for user in users]:   # If the username is not in the list of users, the error is set
            error = 'Incorrect username.'
        else:
            # Get the index of the user in the list of users
            user = [user for user in users if user['name'] == username][0]

            # Validation of the password
            if not check_password_hash(user['password'], password):
                error = 'Incorrect password.'   # If the username exists, but the password is incorrect, the error is set

        if error is None:   # If the username and password both exist and are correct, the user’s id is stored in a new session. 
            session.clear()
            session['user_id'] = user['id']     # The data is stored in a cookie that is sent to the browser, and the browser then sends it back with subsequent requests. Flask securely signs the data so that it can’t be tampered with
            g.user = {}
            g.user['id'] = user['id']
            g.user['name'] = user['name']
            if user['admin'] == 1:
                g.admin = True
                session['admin'] = True
            else:
                if 'admin' in session:
                    del session['admin']
                if 'admin' in g:
                    del g.admin

            return redirect(url_for('home.dashBoardViewer'))   # If the validation succeeds, the user is redirected to the index page

        flash(error, 'error')
    # When the user initially navigates to /auth/login, or there was a validation error,
    return render_template('login.html') # --> Return the Login HTML

### user_id Handshake View (View = URL/Request Handler) ###
# Before the user navigates to a page, the user’s information needs to be loaded. 
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    # g.user lasts for the length of the request. It is a way to store information that might be accessed by multiple functions during the request
    if user_id is None:
        g.user = None   
    else:
        try:
            if user_id not in [user['id'] for user in users]:
                g.user = None
            else:
                user = [user for user in users if user['id'] == user_id][0]
                g.user = {}
                g.user['id'] = user['id']
                g.user['name'] = user['name']

                if user['admin'] == 1:
                    g.admin = True
                else:
                    if 'admin' in g:
                        del g.admin
        except Exception as e:
            flash(f"Error fetching user from database: {e}", 'error')

### LOGOUT View (View = URL/Request Handler) ###
@bp.route('/logout')
def logout():
    session.clear()
    g.user = {}
    return redirect(url_for('home.dashBoardViewer'))

### LOGIN REQUIRED DECORATOR ###
# Creating, editing, and deleting blog posts will require a user to be logged in. A decorator can be used to check this for each view it’s applied to.
# This decorator returns a new view function that wraps the original view it’s applied to.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # if 'tableName' in kwargs and kwargs['tableName'] == 'user':# One Exception for Registration: It uses the editor/prepEdit function without login
            #     print("Start Registration")
            # else:
            return redirect(url_for('auth.login'))  # If a user is not loaded, the user is redirected to the login page

        return view(**kwargs)   # If a user is loaded, the original view is called and continues normally

    return wrapped_view