import time
import requests
from requests.exceptions import RequestException

from elasticsearch import Elasticsearch


def wait_for_es(hosts):
    es_client = Elasticsearch(hosts=hosts, verify_certs=False)
    while True:
        if es_client.ping():
            break
        print("Elasticsearch is unavailable")
        time.sleep(1)


def wait_for_up(host, timeout=60, interval=5):

    wait_for_es(host)

    start_time = time.time()

    while True:
        try:
            response = requests.get(host)
            # Проверяем статус код
            if response.status_code == 200:
                print("Elasticsearch is up and running!")
                return
            elif response.status_code == 503:
                print("Elasticsearch is unavailable (503). Waiting...")
        except RequestException as e:
            print(f"Error connecting to Elasticsearch: {e}. Waiting...")

        # Проверка на таймаут
        if time.time() - start_time > timeout:
            print("Timeout reached while waiting for Elasticsearch.")
            raise Exception(
                "Elasticsearch is not available within the timeout period.")

        time.sleep(interval)


if __name__ == '__main__':
    wait_for_es('http://localhost:9200')
