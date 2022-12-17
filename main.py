# ДЗ 16 Шумихин А.В. 17.12.2022
import json

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from utils import load_all_data, put_user_data, put_order_data

# Пути к файлам с данными json
JSON_USERS = 'data/users.json'
JSON_ORDERS = 'data/orders.json'
JSON_OFFERS = 'data/offers.json'

if __name__ == '__main__':

    # Init and config application ######################################################################################
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_hw16.db'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.url_map.strict_slashes = False

    db = SQLAlchemy(app)

    # Classes defines - (User, Order, Offer) ###########################################################################
    class User(db.Model):
        __tablename__ = 'user'
        id = db.Column(db.Integer, primary_key=True)
        first_name = db.Column(db.String)
        last_name = db.Column(db.String)
        age = db.Column(db.Integer)
        email = db.Column(db.String)
        role = db.Column(db.String)
        phone = db.Column(db.String)

        def conv_dict(self):
            return {
                'id': self.id,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'age': self.age,
                'email': self.email,
                'role': self.role,
                'phone': self.phone
            }


    class Offer(db.Model):
        __tablename__ = 'offer'
        id = db.Column(db.Integer, primary_key=True)
        order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
        executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

        def conv_dict(self):
            return {
                'id': self.id,
                'order_id': self.order_id,
                'executor_id': self.executor_id
            }


    class Order(db.Model):
        __tablename__ = 'order'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)
        description = db.Column(db.String)
        start_date = db.Column(db.String)
        end_date = db.Column(db.String)
        address = db.Column(db.String)
        price = db.Column(db.Integer)
        customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

        def conv_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'address': self.address,
                'price': self.price,
                'customer_id': self.customer_id,
                'executor_id': self.executor_id
            }
    # End of classes defines - (User, Order, Offer) ####################################################################

    # Генерация базы данных в файл base_hw16.db текущей директории с таблицами users, orders, offers ###################
    # из данных в файле data_for_db.py
    db.drop_all()  # deletes all tables
    db.create_all()  # creates all tables

    # Чтение данных из файлов ##########################################################################################
    # Данные пользователей
    users_json = load_all_data(JSON_USERS)

    users = []
    for user in users_json:
        user_tmp = User()

        user_tmp.id = user['id']
        user_tmp.first_name = user['first_name']
        user_tmp.last_name = user['last_name']
        user_tmp.age = user['age']
        user_tmp.email = user['email']
        user_tmp.role = user['role']
        user_tmp.phone = user['phone']

        users.append(user_tmp)

    db.session.add_all(users)

    # Данные заказов
    orders_json = load_all_data(JSON_ORDERS)

    orders = []
    for order in orders_json:
        order_tmp = Order()

        order_tmp.id = order['id']
        order_tmp.description = order['description']
        order_tmp.name = order['name']
        order_tmp.start_date = order['start_date']
        order_tmp.end_date = order['end_date']
        order_tmp.address = order['address']
        order_tmp.price = order['price']
        order_tmp.customer_id = order['customer_id']
        order_tmp.executor_id = order['executor_id']

        orders.append(order_tmp)

    db.session.add_all(orders)

    # Данные предложений
    offers_json = load_all_data(JSON_OFFERS)

    offers = []
    for offer in offers_json:
        offer_tmp = Offer()

        offer_tmp.id = offer['id']
        offer_tmp.order_id = offer['order_id']
        offer_tmp.executor_id = offer['executor_id']
        offers.append(offer_tmp)

    db.session.add_all(offers)
    db.session.commit()  # Конец формирования БД MySQL
    # Конец чтения данных из файлов ####################################################################################

    # Flask Views ######################################################################################################
    @app.route("/")
    def start_page():
        """
        Начальная страница
        """
        return "Home work 16"


    @app.route("/users", methods=['GET'])
    def get_all_users():
        """
        Запрос и вывод всех данных всех пользователей из БД
        """
        users_q_a = User.query.all()  # запрос из БД
        users_ret = []
        for user_q_a in users_q_a:
            users_ret.append(user_q_a.conv_dict())

        return jsonify(users_ret)


    @app.route("/users", methods=['POST'])
    def add_user():
        """
        Получение и запись данных нового пользователя
        """
        data = json.loads(request.data)

        ad_user = put_user_data(data, User())

        db.session.add(ad_user)
        db.session.commit()

        return f'New user (id={ad_user.id}) added.'


    @app.route("/users/<int:us_id>", methods=['GET', 'PUT', 'DELETE'])
    def op_one_user(us_id):
        """
        Вывод, либо изменение, либо удаление всех данных пользователя id в БД
        """
        meth = request.method
        # Вывод
        if meth == 'GET':
            return User.query.get(us_id).conv_dict()
        # Изменение
        elif meth == 'PUT':
            data = json.loads(request.data)  # данные от сервера

            pu_user = put_user_data(data,  User.query.get(us_id))

            db.session.add(pu_user)
            db.session.commit()

            return f'User (id={pu_user.id}) edited.'
        # Удаление
        elif meth == 'DELETE':
            del_user = User.query.get(us_id)
            db.session.delete(del_user)
            db.session.commit()

            return f'User (id={us_id}) is deleted.'


    @app.route("/orders", methods=['GET'])
    def get_all_orders():
        """
        Запрос и вывод всех данных всех заказов из БД
        """
        orders_q_a = Order.query.all()  # запрос из БД
        orders_ret = []
        for order_q_a in orders_q_a:
            orders_ret.append(order_q_a.conv_dict())

        return jsonify(orders_ret)


    @app.route("/orders", methods=['POST'])
    def add_order():
        """
        Получение и запись данных нового заказа
        """
        data = json.loads(request.data)

        ad_order = put_order_data(data, Order())

        db.session.add(ad_order)
        db.session.commit()

        return f'New order (id={ad_order.id}) added.'


    @app.route("/orders/<int:or_id>", methods=['GET', 'PUT', 'DELETE'])
    def op_one_order(or_id):
        """
        Вывод, либо изменение, либо удаление всех данных заказа id из БД
        """
        meth = request.method
        # Вывод
        if meth == 'GET':
            return Order.query.get(or_id).conv_dict()
        # Изменение
        elif meth == 'PUT':
            data = json.loads(request.data)  # данные от сервера

            pu_order = put_order_data(data, Order.query.get(or_id))

            db.session.add(pu_order)
            db.session.commit()

            return f'Order (id={pu_order.id}) edited.'
        # Удаление
        elif meth == 'DELETE':
            del_order = Order.query.get(or_id)
            db.session.delete(del_order)
            db.session.commit()

            return f'Order (id={or_id}) is deleted.'


    @app.route("/offers", methods=['GET'])
    def get_all_offers():
        """
        Запрос и вывод всех данных всех предложений из БД
        """
        offers_q_a = Offer.query.all()  # запрос из БД
        offers_ret = []
        for offer_q_a in offers_q_a:
            offers_ret.append(offer_q_a.conv_dict())

        return jsonify(offers_ret)
    
    
    @app.route("/offers", methods=['POST'])
    def add_offer():
        """
        Получение и запись данных нового заказа
        """
        data = json.loads(request.data)

        ad_offer = Offer()

        ad_offer.order_id = data['order_id']
        ad_offer.executor_id = data['executor_id']

        db.session.add(ad_offer)
        db.session.commit()

        return f'New offer (id={ad_offer.id}) added.'


    @app.route("/offers/<int:of_id>", methods=['GET', 'PUT', 'DELETE'])
    def op_one_offer(of_id):
        """
        Вывод, либо изменение, либо удаление всех данных предложения id из БД
        """
        meth = request.method
        # Вывод
        if meth == 'GET':
            return Offer.query.get(of_id).conv_dict()
        # Изменение
        elif meth == 'PUT':
            data = json.loads(request.data)  # данные от сервера
            pu_offer = Offer.query.get(of_id)  # из БД

            pu_offer.order_id = data['order_id']
            pu_offer.executor_id = data['executor_id']

            db.session.add(pu_offer)
            db.session.commit()

            return f'Offer (id={pu_offer.id}) edited.'
        # Удаление
        elif meth == 'DELETE':
            del_offer = Offer.query.get(of_id)
            db.session.delete(del_offer)
            db.session.commit()

            return f'Offer (id={of_id}) is deleted.'


    app.run()
