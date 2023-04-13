import sqlite3


def start_base():
    global base, cur
    base = sqlite3.connect('data_base.db')
    cur = base.cursor()
    base.execute('CREATE TABLE IF NOT EXISTS {}(number, date, time,  user_id, user_link, type_service, price, '
                 'date_issue, status, payment)'.
                 format('data_base_clients'))
    base.execute('CREATE TABLE IF NOT EXISTS {}(name, image)'.format('data_base_items'))
    base.commit()
    print('БД подключена')


def add_content(number, data, time, user_id, user_link, type_service, price, date_issue, status, payment):
    cur.execute('INSERT INTO data_base_clients VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (number, data, time, user_id, user_link, type_service, price, date_issue, status, payment,))
    base.commit()


def get_content_for_client(type_content):
    answer = cur.execute('SELECT image FROM data_base_items WHERE name == ?', (type_content, )).fetchone()
    base.commit()
    return answer


def get_content_for_admin(date):
    answer = cur.execute('SELECT * FROM data_base_clients WHERE date == ?', (date, )).fetchall()
    base.commit()
    return answer


def get_number():
    answer = cur.execute('SELECT * FROM data_base_clients').fetchall()
    return len(answer)


def setting_status(status, number):
    cur.execute('UPDATE data_base_clients SET status == ? WHERE number == ?', (status, int(number), ))
    answer = cur.execute('SELECT user_id, type_service FROM data_base_clients WHERE number == ?',
                         (int(number),)).fetchone()
    base.commit()
    return answer


def get_in_job():
    answer = cur.execute('SELECT * FROM data_base_clients WHERE status != ?', ('Выдано', )).fetchall()
    base.commit()
    return answer


def get_number_order(user_id):
    answer = cur.execute('SELECT number FROM data_base_clients WHERE status == ? AND user_id == ?',
                         ('Ожидает клиента', str(user_id), )).fetchall()
    base.commit()
    return answer[-1][0]


def replace_payment_status(number):
    cur.execute('UPDATE data_base_clients SET payment == ? WHERE number == ?', ('Оплачено', number))
    base.commit()


def get_content_for_number(number):
    answer = cur.execute('SELECT * FROM data_base_clients WHERE number == ?', (number,)).fetchone()
    base.commit()
    return answer
