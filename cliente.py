import socket 
import json
import time
import getpass
import argparse
from datetime import datetime, timedelta

class NewsClient:
    def __init__(self, host='0.0.0.0', port=6004, timeout=600):
        self.host = host
        self.port = port
        self.timeout = timeout  # Tiempo de espera en segundos
        self.authenticated = False
        self.username = None

    def send_request(self, request):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(self.timeout)  # Establecer el tiempo de espera
            try:
                client_socket.connect((self.host, self.port))
                client_socket.sendall(json.dumps(request).encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                return response
            except socket.timeout:  # Capturar el tiempo de espera
                return json.dumps({'error': 'Timeout occurred'})
    
    def register(self, username, password):
        request = {'action': 'register', 'username': username, 'password': password}
        response = self.send_request(request)
        dict_data = json.loads(response)
        if dict_data['status'] == 'success':
            print('Registration successful.')
        else:
            print('Registration failed')

    def login(self, username, password):
        request = {'action': 'login', 'username': username, 'password': password}
        response = self.send_request(request)
        dict_data = json.loads(response)
        if dict_data['status']  == 'success':
            self.authenticated = True
            self.username = username
            print('Login successful.')
        else:
            print('Login failed')

    def ensure_authenticated(self):
        if not self.authenticated:
            print('You need to be logged in to perform this action.')
            return False
        return True
        
    def subscribe(self, service, client):
        request = {'action': 'subscribe', 'service': service, 'client':client}
        print(self.send_request(request))

    def unsubscribe(self, service, client):
        request = {'action': 'unsubscribe', 'service': service, 'client':client}
        print(self.send_request(request))

    def delete_news(self, content, client_name):
        request = {'action': 'delete_news', 'content': content, 'client': client_name}
        print(self.send_request(request))

    def get_news(self, client_name):
        
        request = {
            'action': 'get_news',
            'client': client_name
        }
        
        print(self.send_request(request))

    def add_area(self, area):
        request = {'action': 'add_area', 'area': area}
        print(self.send_request(request))

    def delete_area(self, area):
        request = {'action': 'delete_area', 'area': area}
        print(self.send_request(request))

    def post_news(self, service, content, client_name):
        request = {'action': 'post_news', 'news_item': {'service': service, 'content': content, 'client': client_name}}
        print(self.send_request(request))


    def get_news_last_24_hours(self, client):
        request = {'action': 'get_news_last_24_hours', 'client': client}
        print(self.send_request(request))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='News Client')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Server IP address')
    parser.add_argument('--port', type=int, default=6004, help='Server port')
    args = parser.parse_args()

    client = NewsClient(host=args.host, port=args.port)
    while True:
        action = input('Do you want to [login] or [register]? ')
        if action == 'login':
            username = input('Username: ')
            password = getpass.getpass('Password: ')
            client.login(username, password)
            if client.authenticated:
                break
        elif action == 'register':
            username = input('Username: ')
            password = getpass.getpass('Password: ')
            client.register(username, password)
        else:
            print('Invalid action. Please choose either [login] or [register].')

    while True:
        print("\nOptions:")
        print("1. Subscribe to an area")
        print("2. Unsubscribe from an area")
        print("3. Get news")
        print("4. Delete news")
        print("5. Add an area")
        print("6. Delete an area")
        print("7. Post news")
        print("8. Get news from the last 24 hours")
        print("9. Logout")
        choice = input("Select an option (1-9): ")

        if choice == '1':
            service = input('Area to subscribe: ')
            client_name = client.username
            client.subscribe(service, client_name)
        elif choice == '2':
            service = input('Area to unsubscribe: ')
            client_name = client.username
            client.unsubscribe(service, client_name)
        elif choice == '3':
            client_name = client.username
            client.get_news(client.username)
        elif choice == '4':
            content = input('News content to delete: ')
            client_name = client.username
            client.delete_news(content, client_name)
        elif choice == '5':
            area = input('Area to add: ')
            client.add_area(area)
        elif choice == '6':
            area = input('Area to delete: ')
            client.delete_area(area)
        elif choice == '7':
            service = input('Area to post news to: ')
            content = input('News content: ')
            client_name = client.username
            client.post_news(service, content, client_name)
        elif choice == '8':
            client_name = client.username
            client.get_news_last_24_hours(client_name)
        elif choice == '9':
            print("Logging out...")
            client.authenticated = False
            client.username = None
            break
        else:
            print("Invalid choice. Please select a valid option.")
