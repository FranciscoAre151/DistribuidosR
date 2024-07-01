import socket
import threading
import json
from tabulate import tabulate

class Member1Service:
    def __init__(self):
        self.news = []

    def subscribe(self, client, service):
        subscription_request = {'action': 'subscribe', 'service': service, 'client': client}
        return self.send_subscription_request_to_common_server(subscription_request)

    def unsubscribe(self, client, service):
        unsubscription_request = {'action': 'unsubscribe', 'service': service, 'client': client}
        response = self.send_subscription_request_to_common_server(unsubscription_request)
        return response

    def delete_news_from_common_server(self, news_item):
        common_server_address = ('datos', 6000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as common_server_socket:
            common_server_socket.connect(common_server_address)
            request = {'action': 'delete_news', 'news_item': news_item}
            common_server_socket.sendall(json.dumps(request).encode('utf-8'))
            response = common_server_socket.recv(1024).decode('utf-8')
            return response

    def send_news_to_common_server(self, news_item):
        common_server_address = ('datos', 6000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as common_server_socket:
            common_server_socket.connect(common_server_address)
            request = {'action': 'send_news', 'news_item': news_item}
            common_server_socket.sendall(json.dumps(request).encode('utf-8'))
            response = common_server_socket.recv(1024).decode('utf-8')
            
            return response

    def send_subscription_request_to_common_server(self, subscription_request):
        common_server_address = ('datos', 6000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as common_server_socket:
            common_server_socket.connect(common_server_address)
            common_server_socket.sendall(json.dumps(subscription_request).encode('utf-8'))
            data = common_server_socket.recv(1024).decode('utf-8')
            response = json.loads(data)
            return response['status']

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                request = json.loads(data)
                action = request['action']
                print(f'request {request}')
                if action == 'subscribe':
                    response = self.subscribe(request['client'], request['service'])
                    client_socket.sendall(response.encode('utf-8'))
                elif action == 'unsubscribe':
                    response = self.unsubscribe(request['client'], request['service'])
                    client_socket.sendall(response.encode('utf-8'))
                elif action == 'delete_news':
                    response_json = self.delete_news_from_common_server(request)
                    response_dict = json.loads(response_json)
                    
                    if 'removed' in response_dict:
                        removed_data = response_dict['removed']
                    else:
                        removed_data = []
                    
                    if removed_data:
                        # Extraer los campos específicos del elemento de noticia eliminado
                        table_data = [[removed_data[1], removed_data[2], removed_data[4]]]
                        headers = ["Area", "Content", "Timestamp"]
                        tabla = tabulate(table_data, headers, tablefmt="pretty")
                        response = f"News removed\n{tabla}"
                    else:
                        response = "News was not found and/or was not created by you"
                    
                    client_socket.sendall(response.encode('utf-8'))
                elif action == 'send_news':
                    response = self.send_news_to_common_server(request['news_item'])
                    client_socket.sendall(response.encode('utf-8'))
            except ConnectionResetError:
                client_socket.close()  # Ensure that the socket is closed properly
                break

    def run(self, host='0.0.0.0', port=6001):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
        print('Member 1 Service started and waiting for connections...')
        while True:
            client_socket, addr = server.accept()
            print(f'Accepted connection from {addr}')
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == '__main__':
    service = Member1Service()
    service.run()
