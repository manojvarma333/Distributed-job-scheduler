"""Network check task: verifies the worker can reach the backend over the network."""
import os

import requests


def run():
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    response = requests.get(f"{backend_url}/network-test", timeout=5)
    response.raise_for_status()
    data = response.json()
    return f"Network check reached backend at {data.get('hostname')} ({data.get('ip_address')})"
