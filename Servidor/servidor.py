# intermediario.py
import socket
import threading
import json
import random
import docker

class IntermediaryServer:
    def __init__(self, host='0.0.0.0', port=6004):
        self.host = host
        self.port = port
        self.docker_client = docker.from_env()  # Create Docker client instance
        

        
    def forward_request(self, host,member_port, request):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as member_socket:
            member_socket.connect((host, member_port))
            member_socket.sendall(json.dumps(request).encode('utf-8'))
            response = member_socket.recv(1024).decode('utf-8')
            return response
            
    def check_container_status(self, container_name):
        try:
            container = self.docker_client.containers.get(container_name)
            if container.status == 'running':
                return True
            else:
                return False
        except docker.errors.NotFound:
            return False
        except docker.errors.APIError as e:
            print(f"Error checking container status: {e}")
            return False

    def select_member_host(self, member_hosts):
        members = len(member_hosts)
        random_host = random.randint(0, members-1) #selecciona un miembro al azar del arreglo
        host = member_hosts[random_host]
        print(f"host : {host}")
        # Check if the selected member host is online
        if self.check_container_status(host):
            return host
        else:
            print("host offline")
            counter = 1
            #el miembro seleccionado anteriormente estaba offline, recorremos el arreglo hasta encontrar uno online
            while not self.check_container_status(host) and counter<=members:
                random_host = (random_host+1) % members
                host = member_hosts[random_host]
                counter = counter + 1

            print(f"new host : {host}")
            return host

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                request = json.loads(data)
                action = request['action']
                print(f'request {request}')
                
                # Forwarding request based on action
                if action in ['subscribe', 'unsubscribe', 'delete_news']:
                    member_port = 6001
                    member_hosts = ['miembro1', 'miembro1.1']
                    host = self.select_member_host(member_hosts)
                elif action in ['login', 'get_news','add_area', 'delete_area']:
                    member_port = 6002
                    member_hosts = ['miembro2', 'miembro2.1']
                    host = self.select_member_host(member_hosts)
                elif action in ['register', 'post_news', 'get_news_last_24_hours']:
                    member_port = 6003
                    member_hosts = ['miembro3', 'miembro3.1']
                    host = self.select_member_host(member_hosts)
                else:
                    response = json.dumps({'error': 'Unknown action'})
                    client_socket.sendall(response.encode('utf-8'))
                    continue

                print(f'member_port {member_port}')

                response = self.forward_request(host, member_port, request)
                
                print(f'response {response}')
                client_socket.sendall(response.encode('utf-8'))
            except ConnectionResetError:
                client_socket.close()  # Asegurar que el socket se cierre correctamente
                break

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print('Intermediary Server started and waiting for connections...')
        while True:
            client_socket, addr = server.accept()
            print(f'Accepted connection from {addr}')
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == '__main__':
    server = IntermediaryServer()
    server.run()
