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
        self.is_connected = True  # Menambahkan status koneksi
        self.stor_count = 0  # Menambahkan penghitung untuk STOR
        self.retr_count = 0  # Menambahkan penghitung untuk RETR
        print("New connection added: ", client_address)

    def run(self):
        print("Connection from : ", self.client_address)
        self.add_client()
        self.client_socket.send(bytes("Welcome to the FTP server.", "utf-8"))
        while self.is_connected:
            data = self.client_socket.recv(1024)
            if not data:
                break
            command = data.decode().split(' ', 1)
            cmd = command[0].strip().upper()
            arg = ''
            if len(command) > 1:
                arg = command[1].strip()

             # Mencetak log perintah yang diterima dari klien
            print(f"Client {self.client_address} executed command: {cmd} {arg}")

            if cmd == 'LIST':
                self.list_files()
            elif cmd == 'RETR':
                self.retrieve_file(arg)
                self.retr_count += 1  # Menginkrementasi penghitung RETR
            elif cmd == 'STOR':
                self.store_file(arg)
                self.stor_count += 1  # Menginkrementasi penghitung STOR
            elif cmd == 'CWD':
                self.change_dir(arg)
            elif cmd == 'QUIT':
                self.is_connected = False  # Memperbarui status koneksi
            elif cmd == 'ACTIVE':
                self.active_clients()
        self.remove_client()
        print("Client disconnected...")

    def add_client(self):
        active_clients.append(self.client_address)
        print(f"Client {self.client_address} connected.")  # Mencetak log status koneksi

    def remove_client(self):
        active_clients.remove(self.client_address)
        print(f"Client {self.client_address} disconnected. STOR count: {self.stor_count}, RETR count: {self.retr_count}")

    # LIST untuk melihat daftar file dan folder pada direktori saat ini
    def list_files(self):
        files = os.listdir(self.cwd)
        self.client_socket.send(bytes('\n'.join(files), "utf-8"))

    # RETR untuk mengunduh file dari server
    def retrieve_file(self, filename):
        file_path = os.path.join(self.cwd, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            self.client_socket.sendall(data)
            self.client_socket.sendall(b'EOF')
        else:
            self.client_socket.send(bytes("Error: File not found.", "utf-8"))

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

    def active_clients(self):
        self.client_socket.send(bytes(str(active_clients), "utf-8"))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.0.113', 12345)
print('Starting up on {} port {}'.format(*server_address))
server_socket.bind(server_address)
print('Binding successful, now listening...')
server_socket.listen(5)
print("FTP Server started...")

active_clients = []

while True:
    print('Waiting for a connection...')
    client_socket, client_address = server_socket.accept()
    print('Connection received from: ', client_address)
    new_thread = ClientThread(client_address, client_socket)
    new_thread.start()
    time.sleep(0.1)