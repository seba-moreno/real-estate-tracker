import requests

API_URL = "http://localhost:8000/api/v1"


def get(path):
    return requests.get(f"{API_URL}{path}")


def post(path, data):
    return requests.post(f"{API_URL}{path}", json=data)


def put(path, data):
    return requests.put(f"{API_URL}{path}", json=data)


def delete(path):
    return requests.delete(f"{API_URL}{path}")
