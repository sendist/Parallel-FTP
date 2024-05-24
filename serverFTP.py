import os
import socket
import threading
import time

class ClientThread(threading.Thread):
    def __init__(self, client_address, client_socket):
        threading.Thread.__init__(self)
        self.cwd = os.getcwd() 
        self.client_socket = client_socket
        print("New connection added: ", client_address)

    def run(self):
        print("Connection from : ", client_address)
        self.client_socket.send(bytes("Welcome to the FTP server.", "utf-8"))
        while True:
            data = self.client_socket.recv(1024)
            if not data: break
            command = data.decode().split(' ', 1)
            cmd = command[0].strip().upper()
            arg = ''
            if len(command) > 1:
                arg = command[1].strip()
            if cmd == 'LIST':
                self.list_files()
            elif cmd == 'RETR':
                self.retrieve_file(arg)
            elif cmd == 'STOR':
                self.store_file(arg)
            elif cmd == 'CWD':
                self.change_dir(arg)
            elif cmd == 'QUIT':
                break
        print("Client disconnected...")

    # LIST untuk melihat daftar file dan folder pada direktori saat ini
    def list_files(self):
        files = os.listdir(self.cwd)
        self.client_socket.send(bytes('\n'.join(files), "utf-8"))

    # RETR untuk mengunduh file dari server
    def retrieve_file(self, filename):
        with open(os.path.join(self.cwd, filename), 'rb') as f:
            data = f.read()
            self.client_socket.sendall(len(data).to_bytes(4, 'big'))
            self.client_socket.sendall(data)
            self.client_socket.sendall(b'EOF') 

    # STOR untuk mengunggah file ke server
    def store_file(self, filename):
        length = int.from_bytes(self.client_socket.recv(4), 'big')
        with open(os.path.join(self.cwd, filename), 'wb') as f:
            while length:
                chunk = self.client_socket.recv(1024)
                if b'EOF' in chunk: 
                    f.write(chunk[:-3]) 
                    break
                else:
                    f.write(chunk)
                    length -= len(chunk)

    # CWD untuk mengubah direktori
    def change_dir(self, new_dir):
        try:
            os.chdir(new_dir)
            self.cwd = os.getcwd()
            self.client_socket.send(bytes("Changed working directory to " + self.cwd, "utf-8"))
        except Exception as e:
            self.client_socket.send(bytes("Failed to change directory: " + str(e), "utf-8"))

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 12345)
print('Starting up on {} port {}'.format(*server_address))
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(5)
print("FTP Server started...")

while True:
    # Wait for a connection
    print('Waiting for a connection...')
    (client_socket, client_address) = server_socket.accept()

    # Start a new thread for each connection
    new_thread = ClientThread(client_address, client_socket)
    new_thread.start()
    time.sleep(0.1)
