from json import load, JSONDecodeError


def get_data_from_json(path):
    """
    Возвращает все данные из файла json
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:     # открытие файла
            data = load(file)                               # загрузка данных
    except FileNotFoundError:
        print(f'ERROR: Not file {path} found.')
        return None
    except JSONDecodeError:
        print(f'ERROR: File {path} not JSON format.')
        return None
    else:
        return data


def load_all_data(path):
    """
    Возврат всех считанных данных json
    """
    return get_data_from_json(path)


def put_user_data(data, model):
    """
     Перекладка данных пользователя из json в модель SQLAlchemy
    """
    model.first_name = data['first_name']
    model.last_name = data['last_name']
    model.age = data['age']
    model.email = data['email']
    model.role = data['role']
    model.phone = data['phone']

    return model


def put_order_data(data, model):
    """
     Перекладка данных заказа из json в модель SQLAlchemy
    """
    model.name = data['name']
    model.description = data['description']
    model.start_date = data['start_date']
    model.end_date = data['end_date']
    model.address = data['address']
    model.price = data['price']
    model.customer_id = data['customer_id']
    model.executor_id = data['executor_id']

    return model
