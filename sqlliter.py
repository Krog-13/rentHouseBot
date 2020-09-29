from inspect import Traceback

import psycopg2 #pip3 install psycopg2-binary
from psycopg2.extras import RealDictCursor, execute_values

class SQLiter:
    def __init__(self, namedb):
        # Подключаемся к ДБ и сохроняем курсор соединения
        self.connection = psycopg2.connect(dbname=namedb, user='postgres', password='postgres', host='localhost')
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status = True):
        # Получаем все подписчиков бота
        with self.connection:
            self.cursor.execute(" SELECT * FROM subscriptions WHERE status = %s", (status, ))
            result = self.cursor.fetchall()
            return result

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        u = str(user_id)
        with self.connection:
            self.cursor.execute('SELECT * FROM subscriptions WHERE user_id = %s', (u,))
            result = self.cursor.fetchall()

            return bool(len(result))

    def add_subscriber(self, user_id, status=True):
        """Добавляем нового подписчика"""
        u = str(user_id)
        with self.connection:
            return self.cursor.execute("INSERT INTO subscriptions (user_id, status) VALUES(%s,%s)",
                                       (u, status))

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        u = str(user_id)
        with self.connection:
            return self.cursor.execute("UPDATE subscriptions SET status = %s WHERE user_id = %s", (status, u))

    def update_url(self, user_id, url):
        """Обновляем url_filters подписки пользователя"""
        u = str(user_id)
        with self.connection:
            return self.cursor.execute("UPDATE subscriptions SET url = %s WHERE user_id = %s", (url, u))

    def add_filters(self, user_id, fPost):
        f = [int(fPost[i]) for i in fPost if i > 0]
        c = fPost[0]
        u = str(user_id)
        with self.connection:
            self.cursor.execute('SELECT country_id FROM country WHERE name_country = %s', (c,))
            id = self.cursor.fetchone()
            self.cursor.execute("UPDATE subscriptions SET country_id = %s, costFrom = %s, costTo = %s WHERE user_id = %s", (id,f[0],f[1], u))

          #  return self.cursor.execute("INSERT INTO filters (costfrom, costto, country_id) VALUES(%s,%s,%s)",
             #                          (f[0], f[1],id))


    def get_country(self):
        with self.connection:
            self.cursor.execute(" SELECT name_country FROM country")
            result = self.cursor.fetchall()
            return result

    def get_keys(self):
        with self.connection:
            self.cursor.execute("SELECT key_post FROM postKey")
            keys = self.cursor.fetchall()
            return keys

    def add_post(self, dt, town):
        with self.connection:
            self.cursor.execute("SELECT country_id FROM country WHERE name_country = %s", (town))
            id = self.cursor.fetchone()
            print(dt)
            for i in dt:
                self.cursor.execute("INSERT INTO postkey (key_post,costs, url, country_id) VALUES(%s,%s,%s,%s)",
                                           (dt[i][0], dt[i][1],dt[i][2], id))
    def get_new_post(self, new_keys='IDiwLDE'):
        with self.connection:
            self.cursor.execute("SELECT distinct (user_id), url FROM subscriptions "
                                "LEFT JOIN country using(country_id)"
                                "LEFT JOIN postkey using(country_id)"
                                "where key_post IN %s and (costs between costfrom and costto) and status=true", (new_keys,))

            parse = self.cursor.fetchall()
            print('sql',parse)
            return parse

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()