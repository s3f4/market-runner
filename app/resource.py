from flask_restful import Resource, reqparse
from model import *
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

from exchange import Exchange as ExchangeRunner

parser = reqparse.RequestParser()
parser.add_argument('email', help='This field cannot be blank', required=True)
parser.add_argument('password', help='This field cannot be blank', required=True)

baseResponse = {
    'success': True,
    'error': False,
    'result': {
    },
}


class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()

        if User.find_by_email(data['email']):
            return {
                "success": False,
                'error': 'User {} already exists'.format(data['email']),
                "result": None
            }
        try:
            new_user = User()
            new_user.email = data['email'],
            new_user.password = User.generate_hash(data['password'])
            new_user.save()

            access_token = create_access_token(identity=data['email'])
            refresh_token = create_refresh_token(identity=data['email'])
            baseResponse['result'] = {
                'message': 'User {} was created'.format(data['email']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return baseResponse
        except:

            return {
                "success": False,
                'error': 'Something went wrong',
                "result": None
            }


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = User.find_by_email(data['email'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['email'])}

        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(
                identity={'email': current_user.email, 'user_id': current_user.user_id})
            refresh_token = create_refresh_token(identity=data['email'])
            return {
                'result': {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                },
                'error': {},
                'success': True
            }
        else:
            return {
                "success": False,
                'error': 'Wrong credentials',
                "result": None
            }


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel()
            revoked_token.jti = jti
            revoked_token.save()
            baseResponse['result'] = 'Refresh token has been revoked'
            return baseResponse
        except:
            return {
                       'success': False,
                       'error': 'Something went wrong',
                       'result': None
                   }, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class UserExchangeEndPoint(Resource):
    @jwt_required
    def put(self):
        user = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument("api_key", help="api_key is required", required=True)
        parser.add_argument("api_secret", help="api_secred is required", required=True)
        parser.add_argument("exchange_id", help="exchange_id is required", required=True)
        args = parser.parse_args()
        exchange_id, api_key, api_secret = args['exchange_id'], args['api_key'], args['api_secret']
        exchange = Exchange.where("exchange_id", exchange_id).first()
        if exchange is not None:
            userExchange = UserExchange()
            userExchange.user_id = user['user_id']
            userExchange.api_key = api_key
            userExchange.api_secret = api_secret
            userExchange.exchange_id = exchange_id
            userExchange.save()

            return baseResponse
        else:
            return None

    @jwt_required
    def get(self):
        user = get_jwt_identity()
        user_exchanges = UserExchange.where("user_id", user["user_id"]).get()
        baseResponse["result"] = user_exchanges.to_json()
        baseResponse["error"] = False
        return baseResponse

    @jwt_required
    def patch(self):
        user = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument("api_key", help="api_key is required", required=True)
        parser.add_argument("api_secret", help="api_secred is required", required=True)
        parser.add_argument("exchange_id", help="exchange_id is required", required=True)
        args = parser.parse_args()

        exchanges = UserExchange.where_raw("user_id = %s and exchange_id = %s",
                                           [user['user_id'], args['exchange_id']]).update(
            api_key=args['api_key'],
            api_secret=args['api_secret']
        )

        baseResponse['result']['rows'] = exchanges
        return baseResponse

    @jwt_required
    def delete(self):
        user = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument("exchange_id", help="exchange_id is required", required=True)
        args = parser.parse_args()

        UserExchange.where("user_id", user['user_id']).where("exchange_id", args['exchange_id']).delete()
        return baseResponse


class ExchangeEndPoint(Resource):
    def get(self, exchange_id=None):
        """
        get all symbols
        :param exchange_id:
        :return:
        """
        if exchange_id is not None:
            exchangeModel = Exchange.where('exchange_id', exchange_id).first()
            if exchangeModel is not None:
                exchangeRunner = ExchangeRunner(exchangeModel.exchange_class)
                baseResponse['result'] = exchangeRunner.fetch_markets()

        else:
            exchanges = Exchange.all()
            import json
            baseResponse["result"] = json.loads(exchanges.to_json())
        return baseResponse


class OrderBookEndPoint(Resource):

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument("exchange_id", help="exchange_id is required", required=True)
        parser.add_argument("symbol", help="symbol is required", required=True)
        parser.add_argument("side", help="side is required", required=True)
        args = parser.parse_args()

        exchangeModel = Exchange.where("exchange_id", args["exchange_id"]).first()
        if exchangeModel is not None:
            exchangeObject = ExchangeRunner(exchangeModel.exchange_class)
            baseResponse['result'] = exchangeObject.fetch_order_book(args["symbol"], None, {'type': args['side']})
            return baseResponse
        else:
            return None


class OrderEndPoint(Resource):

    @jwt_required
    def get(self, exchange_id, symbol=None):
        user = get_jwt_identity()
        exchangeModel = Lib.get_user_exchange(user['user_id'], exchange_id)
        if exchangeModel is not None:
            exchangeRunner = Lib.get_exchange_runner(exchangeModel)
            if symbol is None:
                baseResponse['result'] = exchangeRunner.fetch_open_orders()
            else:
                baseResponse['result'] = exchangeRunner.fetch_open_orders(symbol)
            return baseResponse

    @jwt_required
    def put(self):
        user = get_jwt_identity()
        parser = reqparse.RequestParser()

        parser.add_argument("exchange_id", help="exchange_id is required", required=True)
        parser.add_argument("symbol", help="symbol is required", required=True)
        parser.add_argument("amount", help="amount is required", required=True)
        parser.add_argument("price", help="price is required", required=True)
        parser.add_argument("side", help="side is required", required=True)
        args = parser.parse_args()

        exchangeModel = Lib.get_user_exchange(user['user_id'], args['exchange_id'])

        if exchangeModel is not None:
            exchangeObject = Lib.get_exchange_runner(exchangeModel)
            baseResponse["result"] = exchangeObject.create_order(args['symbol'], "LIMIT", args["side"],
                                                                 args["amout"], args["price"], {})
            return baseResponse
        else:
            return {
                "success": False,
                'error': 'Something went wrong',
                "result": None
            }

    @jwt_required
    def delete(self):
        user = get_jwt_identity()
        parser = reqparse.RequestParser()

        parser.add_argument("exchange_id", help="exchange_id is required", required=True)
        parser.add_argument("symbol", help="symbol is required", required=True)
        parser.add_argument("exchange_order_id", help="exchange_order_id is required", required=True)
        args = parser.parse_args()

        exchangeModel = Lib.get_user_exchange(user['user_id'], args['exchange_id'])
        exchangeObject = Lib.get_exchange_runner(exchangeModel)
        baseResponse['result'] = exchangeObject.cancel_order(args['exchange_order_id'], args['symbol'])
        return baseResponse


class MarketEndPoint(Resource):
    def get_base_markets(self, exchange_class):
        markets = self.get(exchange_class)
        markets


    def get(self, exchange_class):
        exchangeModel = Exchange()
        exchangeModel.exchange_class = exchange_class
        exchangeModel.api_key = None
        exchangeModel.api_secret = None
        exchangeRunner = Lib.get_exchange_runner(exchangeModel)
        baseResponse['result'] = exchangeRunner.fetch_markets()
        return baseResponse


class Lib(object):
    @staticmethod
    def get_user_exchange(user_id, exchange_id):
        return Exchange.where("exchange_id", exchange_id).where("user_id", user_id).first()

    @staticmethod
    def get_exchange_runner(exchangeModel):
        return ExchangeRunner(exchangeModel.exchange_class, exchangeModel.api_key, exchangeModel.api_secret)


class Ticker(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def post(self):
        pass
