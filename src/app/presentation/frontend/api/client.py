import requests
import streamlit as st

API_URL = "http://localhost:8000/api/v1"

def _auth_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def get(path: str, **kwargs):
    url = f"{API_URL}{path}"
    headers = kwargs.pop("headers", {})
    headers.update(_auth_headers())
    return requests.get(url, headers=headers, **kwargs)

def post(path: str, data=None, **kwargs):
    url = f"{API_URL}{path}"
    headers = kwargs.pop("headers", {})
    headers.update(_auth_headers())
    return requests.post(url, json=data, headers=headers, **kwargs)


def put(path: str, data=None, **kwargs):
    url = f"{API_URL}{path}"
    headers = kwargs.pop("headers", {})
    headers.update(_auth_headers())
    return requests.put(url, json=data, headers=headers, **kwargs)

def delete(path: str, **kwargs):
    url = f"{API_URL}{path}"
    headers = kwargs.pop("headers", {})
    headers.update(_auth_headers())
    return requests.delete(url, headers=headers, **kwargs)