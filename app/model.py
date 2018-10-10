import datetime

from init import db
from passlib.hash import pbkdf2_sha256 as sha256


class User(db.Model):
    __table__ = "user"
    __timestamps__ = False

    def get_dates(self):
        return ['created']

    def get_date_format(self):
        return '%Y-%m-%d %H:%M:%S'

    @classmethod
    def find_by_user_name(cls, user_name):
        return User.where("user_name", user_name).first()

    @classmethod
    def find_by_email(cls, email):
        return User.where("email", email).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class UserExchange(db.Model):
    __table__ = "user_exchange"
    __timestamps__ = False

    def get_dates(self):
        return ['created']

    def get_date_format(self):
        return '%Y-%m-%d %H:%M:%S'

    def __repr__(self):
        return '<UserExchange %r>' % self.exchange_id


class RevokedTokenModel(db.Model):
    __table__ = 'revoked_token'

    def add(self):
        pass

    @classmethod
    def is_jti_blacklisted(cls, jti):
        return None


class Exchange(db.Model):
    __table__ = 'exchange'

    def __repr__(self):
        return '<Exchange %r>' % self.exchange_name


class Order(db.Model):
    __table__ = 'order'
    __timestamps__ = False

    def get_dates(self):
        return ['created']

    def get_date_format(self):
        return '%Y-%m-%d %H:%M:%S'

    def __repr__(self):
        return '<Order %r>' % self.order_id


class Transaction(db.Model):
    __table__ = 'transaction'


class UserTransaction(db.Model):
    __table__ = 'user_transaction'
    __timestamps__ = False

    def get_dates(self):
        return ['created']

    def get_date_format(self):
        return '%Y-%m-%d %H:%M:%S'

    def __repr__(self):
        return '<UserTransaction %r>' % self.transaction_id


class OrderBook(db.Model):
    __table__ = 'order_book'
