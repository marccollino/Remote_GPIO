import os

from flask import Flask

def create_app(test_config=None):   # create_app is the application factory function. You’ll use it to tell Flask how to create your application
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)    # __name__ is the name of the current Python module. The app needs to know where it’s located to set up some paths, and __name__ is a convenient way to tell it that
    app.config.from_mapping(    # app.config is a dictionary that contains the configuration variables for your application
        SECRET_KEY='dev',       # SECRET_KEY is used by Flask and extensions to keep data safe          
    )

    if test_config is None:         # test_config can also be passed to the factory, and will be used instead of the instance configuration
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import auth  # import the auth module
    app.register_blueprint(auth.bp) # register the auth blueprint

    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='home.dashBoardViewer') #The home webpage is the main feature of tutorial_blogger, so it makes sense that the blog index will be the main index.
    # -->  url_for('index') or url_for('blog.index') will both work, generating the same / URL

    return app