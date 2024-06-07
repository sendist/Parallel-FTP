import os
import socket
import threading
import time

class ClientThread(threading.Thread):
    def __init__(self, client_address, client_socket):
        threading.Thread.__init__(self)
        self.cwd = os.getcwd()
        self.client_socket = client_socket
        self.client_address = client_address
        self.is_connected = True
        self.stor_count = 0
        self.retr_count = 0
        print(f"Connection established from: {client_address}")

    def run(self):
        self.add_client()
        self.client_socket.send(bytes("Welcome to the FTP server.", "utf-8"))
        try:
            while self.is_connected:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                command = data.decode().split(' ', 1)
                cmd = command[0].strip().upper()
                arg = ''
                if len(command) > 1:
                    arg = command[1].strip()

                print(f"Client {self.client_address} executed command: {cmd} {arg}")

                if cmd == 'LIST':
                    self.list_files()
                elif cmd == 'RETR':
                    self.retrieve_file(arg)
                    self.retr_count += 1
                elif cmd == 'STOR':
                    self.store_file(arg)
                    self.stor_count += 1
                elif cmd == 'CWD':
                    self.change_dir(arg)
                elif cmd == 'QUIT':
                    self.is_connected = False
                elif cmd == 'ACTIVE':
                    self.active_clients()
        except ConnectionResetError:
            print(f"Connection reset by client {self.client_address}")
        finally:
            self.remove_client()
            self.client_socket.close()
            print(f"Client {self.client_address} disconnected. STOR count: {self.stor_count}, RETR count: {self.retr_count}")

    def add_client(self):
        active_clients.append(self.client_address)
        print(f"Client {self.client_address} connected.")

    def remove_client(self):
        if self.client_address in active_clients:
            active_clients.remove(self.client_address)
        print(f"Client {self.client_address} disconnected.")

    def list_files(self):
        files = os.listdir(self.cwd)
        self.client_socket.send(bytes('\n'.join(files), "utf-8"))

    def retrieve_file(self, filename):
        file_path = os.path.join(self.cwd, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            self.client_socket.sendall(data)
            self.client_socket.send(b'EOF')
            self.client_socket.send(b"File transfer completed.")
        else:
            self.client_socket.send(bytes("Error: File not found.", "utf-8"))

    def store_file(self, filename):
        length = int.from_bytes(self.client_socket.recv(4), 'big')
        received = 0
        with open(os.path.join(self.cwd, filename), 'wb') as f:
            while received < length:
                self.client_socket.settimeout(5)
                try:
                    chunk = self.client_socket.recv(1024)
                    if not chunk:
                        break
                    if b'EOF' in chunk:
                        f.write(chunk[:-3])
                        break
                    else:
                        f.write(chunk)
                    received += len(chunk)
                except socket.timeout:
                    break
            self.client_socket.settimeout(None)
        self.client_socket.send(b"File upload completed.")

    def change_dir(self, new_dir):
        try:
            new_path = os.path.join(self.cwd, new_dir)
            if os.path.isdir(new_path):
                self.cwd = new_path
                self.client_socket.send(bytes("Changed working directory to " + self.cwd, "utf-8"))
            else:
                self.client_socket.send(bytes("Failed to change directory: Directory not found.", "utf-8"))
        except Exception as e:
            self.client_socket.send(bytes("Failed to change directory: " + str(e), "utf-8"))

    def active_clients(self):
        self.client_socket.send(bytes(str(active_clients), "utf-8"))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('192.168.0.114', 12345)
print('Starting up on {} port {}'.format(*server_address))
server_socket.bind(server_address)
print('Binding successful, now listening...')
server_socket.listen(5)
print("FTP Server started...")

active_clients = []

while True:
    print('Waiting for a connection...')
    client_socket, client_address = server_socket.accept()
    new_thread = ClientThread(client_address, client_socket)
    new_thread.start()
    time.sleep(0.1)
