# 0.0.0.0_service.py
import socket
import threading
import json
import time
from tabulate import tabulate

class Member2Service:
    def __init__(self):
        self.areas = []
        self.subscriptions = {}
        self.news = []

    def get_news(self, request):
        common_server_address = ('datos', 6000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as common_server_socket:
            common_server_socket.connect(common_server_address)
            request = {
                'action': 'get_news',
                'client': request['client']
            }
            common_server_socket.sendall(json.dumps(request).encode('utf-8'))
            response = common_server_socket.recv(4096).decode('utf-8')
            news_items = json.loads(response)['new_news']
            return news_items
        return {'status': 'connection_problem'}


    def add_area(self, area):
        common_server_address = ('datos', 6000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as common_server_socket:
            common_server_socket.connect(common_server_address)
            request = {'action': 'add_service', 'service_name': area}
            common_server_socket.sendall(json.dumps(request).encode('utf-8'))
            response = common_server_socket.recv(4096).decode('utf-8')
            result = json.loads(response)
            if result['service']['status'] == 'service_added':
                self.areas.append(area)
                return {'status': 'Area added successfully!'}
            elif result['service']['status'] == 'service_exists':
                return {'status': 'Area already exists'}
        return {'status': 'Area already exists'}

    def delete_area(self, area):
        common_server_address = ('datos', 6000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as common_server_socket:
            common_server_socket.connect(common_server_address)
            request = {'action': 'delete_service', 'service_name': area}
            common_server_socket.sendall(json.dumps(request).encode('utf-8'))
            response = common_server_socket.recv(4096).decode('utf-8')
            result = json.loads(response)
            if result['service']['status'] == 'service_deleted':
                return {'status': 'Area deleted successfully!'}
            elif result['service']['status'] == 'service_not_found':
                return {'status': 'Area not found'}
        return {'status': 'Area not found'}
    
    def authenticate_user(self, username, password):
        common_server_address = ('datos', 6000)
        login_request = {'action': 'login', 'username': username, 'password': password}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as common_server_socket:
            common_server_socket.connect(common_server_address)
            common_server_socket.sendall(json.dumps(login_request).encode('utf-8'))
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
                print(f'request: {request}')
                
                if action == 'add_area':
                    aux = self.add_area(request['area'])
                    response = aux['status']
                elif action == 'delete_area':
                    aux = self.delete_area(request['area'])
                    response = aux['status']
                elif action == 'login':
                    username = request['username']
                    password = request['password']
                    response = self.authenticate_user(username, password)
                elif action == 'get_news':
                    recent_news = self.get_news(request)
                    headers = ["Area", "Content", "Timestamp"]
                    if recent_news:
                        # Extraer los campos específicos de cada noticia en recent_news
                        table_data = [[news[1], news[2], news[4]] for news in recent_news]
                    else:
                        table_data = []
                    response = tabulate(table_data, headers, tablefmt="pretty")
                    
                client_socket.sendall(response.encode('utf-8'))
            except ConnectionResetError:
                client_socket.close()
                break


    def run(self, host='0.0.0.0', port=6002):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
        print('Member 2 Service started and waiting for connections...')

        while True:
            client_socket, addr = server.accept()
            print(f'Accepted connection from {addr}')
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == '__main__':
    service = Member2Service()
    service.run()
