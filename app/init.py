import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from dotenv import load_dotenv
from flask_orator import Orator
from config import development, production

APP_ROOT = os.path.join(os.path.dirname(__file__), '.')  # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

env = os.getenv("ENV")
if env == "DEVELOPMENT":
    dbConf = development.mysqlConf
elif env == "PRODUCTION":
    dbConf = production.mysqlConf

app = Flask(__name__)
app.config['ORATOR_DATABASES'] = dbConf
db = Orator(app)
api = Api(app)

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return model.RevokedTokenModel.is_jti_blacklisted(jti)


import model, resource

api.add_resource(resource.UserRegistration, '/register')
api.add_resource(resource.UserLogin, '/login')
api.add_resource(resource.UserLogoutAccess, '/logout/access')
api.add_resource(resource.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resource.TokenRefresh, '/token/refresh')
api.add_resource(resource.UserExchangeEndPoint,
                 '/user_exchange/<int:user_id>',
                 '/user_exchange', methods=['POST', 'GET', 'PUT', 'DELETE', 'PATCH'])
api.add_resource(resource.ExchangeEndPoint, "/exchanges")
api.add_resource(resource.OrderEndPoint,
                 "/order"
                 "/order/<int:exchange_id>",
                 "/order/<int:exchange_id>/<string:symbol>"
                 , methods=['GET', 'POST', 'PUT', 'DELETE'])

api.add_resource(resource.OrderBookEndPoint, "/order_book", methods=['POST'])
api.add_resource(resource.MarketEndPoint, '/markets/<string:exchange_class>', methods=['GET'])
