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

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()