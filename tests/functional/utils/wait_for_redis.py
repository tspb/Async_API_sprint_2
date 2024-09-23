import time
import socket


def is_service_available(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex((host, port))
        return result == 0


def wait_for_services(services):
    for service in services:
        host, port = service
        while not is_service_available(host, port):
            print(f"{host}:{port} is unavailable - sleeping")
            time.sleep(1)
        print(f"{host}:{port} is up")


def wait_for_redis(url):
    protocol, service = url.split('://')
    host, port = service.split(':')
    wait_for_services([(host, int(port)),])


if __name__ == '__main__':
    wait_for_redis('http://localhost:6379')
