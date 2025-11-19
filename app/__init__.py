from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_login import LoginManager
from firebase_admin import auth
import os
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime, date
import types
from app.models.user import User

load_dotenv()

login_manager = LoginManager()


class CustomJSONProvider(DefaultJSONProvider):
    """Provider JSON customizado para serializar Decimal, datetime e métodos."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        # Tratar métodos e funções passados sem serem chamados
        if isinstance(obj, (types.MethodType, types.FunctionType, types.BuiltinMethodType, types.BuiltinFunctionType)):
            try:
                result = obj()
                return result
            except:
                return str(obj)
        return super().default(obj)


@login_manager.user_loader
def load_user(user_id):
    try:
        user_record = auth.get_user(user_id)
        return User(uid=user_id, email=user_record.email, nome=user_record.display_name)
    except:
        return None


def criar_app():
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    app = Flask(__name__, template_folder=template_dir)

    app.config['SECRET_KEY'] = 'chave-secreta-desenvolvimento'
    app.config['FIREBASE_WEB_API_KEY'] = os.environ.get('FIREBASE_WEB_API_KEY', 'REPLACE_WITH_YOUR_KEY')

    # Usar provider JSON customizado para Decimal, datetime e métodos
    app.json_provider_class = CustomJSONProvider
    app.json = CustomJSONProvider(app)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from app import routes
    app.register_blueprint(routes.bp)

    return app
