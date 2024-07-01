import socket
import threading
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from datetime import datetime

class CommonServer:
    def __init__(self, host='0.0.0.0', port1=6000, timeout=5):
        self.host = host
        self.port1 = port1
        self.timeout = timeout
        self.lock = threading.Lock()  # For thread-safe access
        self.db_connection = sqlite3.connect('common_server.db', check_same_thread=False)
        self.create_tables()

    # Creación de las tablas de base de datos
    def create_tables(self):
        with self.db_connection:
            self.db_connection.execute('''CREATE TABLE IF NOT EXISTS news (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            service TEXT,
                                            content TEXT,
                                            client TEXT,
                                            timestamp TEXT)''')
            self.db_connection.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
                                            service TEXT,
                                            client_address TEXT)''')
            self.db_connection.execute('''CREATE TABLE IF NOT EXISTS users (
                                            username TEXT PRIMARY KEY,
                                            password TEXT,
                                            last_news_request TEXT)''')
            self.db_connection.execute('''CREATE TABLE IF NOT EXISTS services (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            name TEXT UNIQUE)''')
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Register a new user
    def register_user(self, username, password):
        hashed_password = self.hash_password(password)
        current_timestamp = datetime.now().isoformat()  # Get the current datetime
        with self.lock, self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                return {'status': 'user_exists'}
            self.db_connection.execute('INSERT INTO users (username, password, last_news_request) VALUES (?, ?, ?)', 
                                       (username, hashed_password, current_timestamp))
        return {'status': 'success'}
    
    #login de usuario
    def login_user(self, username, password):
        hashed_password = self.hash_password(password)
        with self.lock, self.db_connection:
            cursor = self.db_connection.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
            if cursor.fetchone():
                return {'status': 'success'}
            else:
                return {'status': 'login_failed'}
                
    # Método para recibir noticias nuevas
    def post_news(self, service, content, client):
        news_item = {'service': service, 'content': content, 'client': client, 'timestamp': datetime.now().isoformat()}
        with self.lock, self.db_connection:
            cursor = self.db_connection.cursor()
            
            # Verificar si el cliente está suscrito al servicio
            cursor.execute('SELECT COUNT(*) FROM subscriptions WHERE service = ? AND client_address = ?', (service, client))
            is_subscribed = cursor.fetchone()[0] > 0
            
            if not is_subscribed:
                return {'status': 'Not subscribed to this service'}
            
            # Check if the service exists in the services table
            cursor.execute('SELECT id FROM services WHERE name = ?', (service,))
            service_id = cursor.fetchone()

            # If the service does not exist, insert it
            if not service_id:
                cursor.execute('INSERT INTO services (name) VALUES (?)', (service,))
                service_id = cursor.lastrowid
            else:
                service_id = service_id[0]

            self.db_connection.execute('INSERT INTO news (service, content, client, timestamp) VALUES (?, ?, ?, ?)',
                                       (service, content, client, news_item['timestamp']))
        return {'status': 'News posted successfully!'}


    # Método para eliminar noticias
    def delete_news(self, client, title):
        with self.lock, self.db_connection:
            # Check if the news exists for the given client and title
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT * FROM news WHERE client=? AND content=?', (client, title))
            removed = cursor.fetchone()
            print(f"news to delete: {removed}")
            if removed:
                # Verify if the client matches the stored client name
                stored_client = removed[3]  # Assuming 'client' is the fourth column in your news table
                if client == stored_client:
                    cursor.execute('DELETE FROM news WHERE client=? AND content=?', (client, title))
                    self.db_connection.commit()
                    print(f"Deleted news: {removed}")
                    return removed  # Return the deleted news item tuple
                else:
                    print(f"Client '{client}' does not match stored client '{stored_client}'. News not deleted.")
                    return None
            else:
                print(f"News with content '{title}' not found for client '{client}'.")
                return None

    # Método para obtener noticias nuevas desde un timestamp dado
    def get_new_news(self, client):
        since_timestamp = 0
        with self.lock, self.db_connection:
            try:
                # Update since_timestamp with the value of last_news_request for the client
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT last_news_request FROM users WHERE username = ?', (client,))
                last_news_request = cursor.fetchone()
                if last_news_request:
                    since_timestamp = last_news_request[0]
                    
                # Get the list of services the client is subscribed to
                cursor.execute('SELECT service FROM subscriptions WHERE client_address = ?', (client,))
                subscribed_services = [row[0] for row in cursor.fetchall()]
                

                # If the client is not subscribed to any services, return an empty list
                if not subscribed_services:
                    return []

                # Execute query to fetch news items since the given timestamp for subscribed services
                cursor.execute('''
                    SELECT * FROM news 
                    WHERE timestamp >= ? 
                    AND service IN ({seq}) 
                    ORDER BY timestamp DESC
                '''.format(seq=','.join(['?']*len(subscribed_services))),
                [since_timestamp] + subscribed_services)

                latest_news = cursor.fetchall()
                
                # Update last_news_request for the client with the current datetime
                current_time = datetime.now().isoformat()
                cursor.execute('UPDATE users SET last_news_request = ? WHERE username = ?', (current_time, client))
                self.db_connection.commit()
                
                return latest_news
            except sqlite3.Error as e:
                print(f"Error fetching new news: {e}")
                return []



    # Método para obtener la lista de suscriptores
    def get_subscribers(self):
        with self.lock, self.db_connection:
            cursor = self.db_connection.execute('SELECT service, client_address FROM subscriptions')
            subscribers = [{'service': row[0], 'address': row[1]} for row in cursor.fetchall()]
        return subscribers

    # Método para obtener noticias de las últimas 24 horas
    def get_news_last_24_hours(self, client):
        cutoff_time = (datetime.now() - timedelta(days=1)).isoformat()
        with self.lock, self.db_connection:
            cursor = self.db_connection.cursor()
            
            # Get the list of services the client is subscribed to
            cursor.execute('SELECT service FROM subscriptions WHERE client_address = ?', (client,))
            subscribed_services = [row[0] for row in cursor.fetchall()]
            
            # If the client is not subscribed to any services, return an empty list
            if not subscribed_services:
                return []

            # Fetch news from the last 24 hours for subscribed services
            query = '''
                SELECT * FROM news 
                WHERE timestamp > ? 
                AND service IN ({seq}) 
                ORDER BY timestamp DESC
            '''.format(seq=','.join(['?']*len(subscribed_services)))
            
            cursor.execute(query, [cutoff_time] + subscribed_services)
            recent_news = cursor.fetchall()
            
        return recent_news


    # Manejo de la solicitud de suscripción del cliente
    def handle_subscription_request(self, request):
        client = request['client']
        service = request['service']
        response = {'status': 'Successful subscription!'}

        with self.lock, self.db_connection:
            # Check if the service exists
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT id FROM services WHERE name = ?', (service,))
            service_id = cursor.fetchone()

            if service_id:
                # Service exists, proceed with subscription
                cursor.execute('SELECT COUNT(*) FROM subscriptions WHERE service = ? AND client_address = ?', (service, client))
                count = cursor.fetchone()[0]

                if count > 0:
                    response = {'status': 'Already subscribed'}
                else:
                    self.db_connection.execute('INSERT INTO subscriptions (service, client_address) VALUES (?, ?)', (service, client))
            else:
                # Service does not exist, update response accordingly
                response = {'status': 'Area not found'}

        return response



    # Método para manejar la solicitud de cancelación de suscripción del cliente
    def handle_unsubscription_request(self, request):
        client = request['client']
        service = request['service']
        response = {'status': 'Successful unsubscription!'}

        with self.lock, self.db_connection:
            # Check if the IP address is subscribed to the given service
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT COUNT(*) FROM subscriptions WHERE service = ? AND client_address = ?', (service, client))
            count = cursor.fetchone()[0]

            if count == 0:
                response = {'status': 'Not subscribed to this service'}
            else:
                self.db_connection.execute('DELETE FROM subscriptions WHERE service = ? AND client_address = ?', (service, client))

        return response

    
    # Método para añadir un nuevo servicio
    def add_service(self, service_name):
        with self.lock, self.db_connection:
            try:
                self.db_connection.execute('INSERT INTO services (name) VALUES (?)', (service_name,))
                return {'status': 'service_added'}
            except sqlite3.IntegrityError:
                return {'status': 'service_exists'}

    # Método para eliminar un servicio
    def delete_service(self, service_name):
        with self.lock, self.db_connection:
            cursor = self.db_connection.cursor()
            
            cursor.execute('SELECT id FROM services WHERE name = ?', (service_name,))
            service_id = cursor.fetchone()
            if service_id:
                self.db_connection.execute('DELETE FROM services WHERE name = ?', (service_name,))
                self.db_connection.execute('DELETE FROM subscriptions WHERE service = ?', (service_name,))
                self.db_connection.execute('DELETE FROM news WHERE service = ?', (service_name,))
                return {'status': 'service_deleted'}
            else:
                return {'status': 'service_not_found'}
    
    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                request = json.loads(data)
                action = request['action']
                print(f'request {request}')
                if action == 'post_news':
                    response = self.post_news(request['news_item']['service'], request['news_item']['content'], request['news_item']['client'])
                    client_socket.sendall(json.dumps(response).encode('utf-8'))
                elif action == 'get_news_last_24_hours':
                    response = self.get_news_last_24_hours(request['client'])
                    client_socket.sendall(json.dumps(response).encode('utf-8'))
                elif action == 'subscribe':
                    response = self.handle_subscription_request(request)
                    client_socket.sendall(json.dumps(response).encode('utf-8'))
                elif action == 'unsubscribe':
                    response = self.handle_unsubscription_request(request)
                    client_socket.sendall(json.dumps(response).encode('utf-8'))
                elif action == 'get_subscribers':
                    subscribers = self.get_subscribers()
                    client_socket.sendall(json.dumps({'subscribers': subscribers}).encode('utf-8'))
                elif action == 'get_news':
                    new_news = self.get_new_news(request['client'])
                    client_socket.sendall(json.dumps({'new_news': new_news}).encode('utf-8'))
                elif action == 'add_service':
                    response = self.add_service(request['service_name'])
                    client_socket.sendall(json.dumps({'service': response}).encode('utf-8'))
                elif action == 'delete_service':
                    response = self.delete_service(request['service_name'])
                    client_socket.sendall(json.dumps({'service': response}).encode('utf-8'))
                elif action == 'delete_news':
                    removed = self.delete_news(request['news_item']['client'], request['news_item']['content'])
                    if removed:
                        client_socket.sendall(json.dumps({'removed': removed}).encode('utf-8'))
                    elif not removed:
                        client_socket.sendall(json.dumps({'none_removed': removed}).encode('utf-8'))
                elif action == 'register':
                    response = self.register_user(request['username'], request['password'])
                    client_socket.sendall(json.dumps(response).encode('utf-8'))
                elif action == 'login':
                    response = self.login_user(request['username'], request['password'])
                    client_socket.sendall(json.dumps(response).encode('utf-8'))

        except ConnectionResetError:
            client_socket.close()  # Close the socket properly

    def run(self):
        # Inicia dos instancias de socket para escuchar en los dos puertos
        server1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server1.bind((self.host, self.port1))
        server1.listen(5)
        server1.settimeout(self.timeout)
        print('Common Server started and waiting for connections...')
        while True:
            try:
                # Acepta conexiones
                client_socket1, addr1 = server1.accept()
                print(f'Accepted connection from {addr1}')
                client_handler1 = threading.Thread(target=self.handle_client, args=(client_socket1,))
                client_handler1.start()
            except socket.timeout:
                pass

if __name__ == '__main__':
    server = CommonServer()
    server.run()
