import mimetypes
import socket
import logging
import json
from datetime import datetime
import threading
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = Path()
SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 5000


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        print(route.query)
        match route.path:
            case '/':
                self.send_html('index.html')
            case '/message':
                self.send_html('message.html')
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('error.html', 404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(post_data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-Type', mime_type)
        else:
            self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

def save_data_from_form(data):
    parse_data = urllib.parse.unquote_plus(data.decode())
    try:
        parse_dict = {key: value for key, value in [el.split('=') for el in parse_data.split('&')]}
        if (fp:=Path('storage/data.json')).exists():
            with open(fp, 'r', encoding='utf-8') as file:
                try:
                    jsondata = json.load(file)
                except json.JSONDecodeError:
                    jsondata = {}
            with open(fp, 'w', encoding='utf-8') as file:
                key = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                jsondata[key] = parse_dict
                json.dump(jsondata, file, ensure_ascii=False, indent=4)
        else:
            with open(fp, 'w', encoding='utf-8') as file:
                key = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                json.dump({key: parse_dict}, file, ensure_ascii=False, indent=4)
    except ValueError as err:
        logging.error(err)
    except OSError as err:
        logging.error(err)

def run_socket_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"Socket server is running on {host}:{port}")
    
    try:
        while True:
            msg, address = server_socket.recvfrom(2048)
            save_data_from_form(msg)
    except KeyboardInterrupt:
        pass
    finally:
        server_socket.close()

def run_http_server():
    address = ('localhost', 8080)
    http_server = HTTPServer(address, Handler)
    print(f"HTTP server is running on {address[0]}:{address[1]}")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        http_server.server_close()


if __name__ == '__main__':
    webserver = threading.Thread(target=run_http_server)
    webserver.start()
    socket_server = threading.Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    socket_server.start()