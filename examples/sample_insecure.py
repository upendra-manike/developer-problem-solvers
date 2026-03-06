import pickle
import re
import requests


def bad_query(cursor, user_id):
    sql = "SELECT * FROM users WHERE id=" + user_id
    return cursor.execute(sql)


def insecure_deser(raw):
    return pickle.loads(raw)


API_KEY = "my-secret-token-value"


def slow_loop(items):
    for item in items:
        matcher = re.compile(r"item-\\d+")
        if matcher.match(item):
            print(item)


async def fetch_data(url):
    response = requests.get(url, timeout=3)
    return response.text
