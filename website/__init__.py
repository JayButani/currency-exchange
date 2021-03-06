from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
def create_app(enviroment = 'Development'):
    app = Flask(__name__)
    app.config.from_object(f'config.{enviroment}Config')

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .wallet import walletView

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(walletView, url_prefix='/')

    from .models import User

    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app