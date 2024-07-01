# miembro3_service.py
import socket
import threading
import json
from datetime import datetime, timedelta
from tabulate import tabulate

class Member3Service:
    def __init__(self):
        pass

    def get_news_last_24_hours_from_common_server(self, request):
        common_server_address = ('datos', 6000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as common_server_socket:
            common_server_socket.connect(common_server_address)
            request = {'action': 'get_news_last_24_hours', 'client': request['client']}
            common_server_socket.sendall(json.dumps(request).encode('utf-8'))
            response = common_server_socket.recv(1024).decode('utf-8')
            return json.loads(response)

    def send_news_to_common_server(self, news_item):
        common_server_address = ('datos', 6000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as common_server_socket:
            common_server_socket.connect(common_server_address)
            request = {'action': 'post_news', 'news_item': news_item}
            common_server_socket.sendall(json.dumps(request).encode('utf-8'))
            data = common_server_socket.recv(1024).decode('utf-8')
            response = json.loads(data)
            return response['status']
            
    def register_user(self, username, password):
        common_server_address = ('datos', 6000)
        register_request = {'action': 'register', 'username': username, 'password': password}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as common_server_socket:
            common_server_socket.connect(common_server_address)
            common_server_socket.sendall(json.dumps(register_request).encode('utf-8'))
            response = common_server_socket.recv(1024).decode('utf-8')
            return response

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                request = json.loads(data)
                action = request['action']
                print(f'request {request}')
                if action == 'post_news':
                    news_item = request['news_item']
                    response = self.send_news_to_common_server(news_item)
                    client_socket.sendall(json.dumps(response).encode('utf-8'))
                elif action == 'register':
                    username = request['username']
                    password = request['password']
                    response = self.register_user(username, password)
                    client_socket.sendall(response.encode('utf-8'))
                elif action == 'get_news_last_24_hours':
                    recent_news = self.get_news_last_24_hours_from_common_server(request)
                    if recent_news:
                        # Extraer los campos específicos de cada noticia en recent_news
                        table_data = [[news[1], news[2], news[4]] for news in recent_news]
                    else:
                        table_data = []
                    headers = ["Area", "Content", "Timestamp"]
                    tabla = tabulate(table_data, headers, tablefmt="pretty")
                    client_socket.sendall(tabla.encode('utf-8'))
            except ConnectionResetError:
                client_socket.close()  # Asegurar que el socket se cierre correctamente
                break

    def run(self, host='0.0.0.0', port=6003):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
        print('Member 3 Service started and waiting for connections...')
        while True:
            client_socket, addr = server.accept()
            print(f'Accepted connection from {addr}')
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == '__main__':
    service = Member3Service()
    service.run()
