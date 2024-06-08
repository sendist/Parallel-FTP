import os
import socket
import threading
import time
import threading
import os
import socket
import time

class ClientThread(threading.Thread):
    def __init__(self, client_address, client_socket):
        threading.Thread.__init__(self)
        self.cwd = os.getcwd()  # Menyimpan direktori kerja saat ini
        self.client_socket = client_socket  # Socket klien
        self.client_address = client_address  # Alamat klien
        self.is_connected = True  # Status koneksi
        self.stor_count = 0  # Penghitung operasi STOR
        self.retr_count = 0  # Penghitung operasi RETR
        print(f"Connection established from: {client_address}")

    def run(self):
        self.add_client()  # Menambahkan klien ke daftar aktif
        self.client_socket.send(bytes("Welcome to the FTP server.", "utf-8"))
        try:
            while self.is_connected:
                data = self.client_socket.recv(1024)  # Menerima data dari klien
                if not data:
                    break
                command = data.decode().split(' ', 1)  # Memisahkan perintah dan argumen
                cmd = command[0].strip().upper()  # Perintah utama
                arg = ''
                if len(command) > 1:
                    arg = command[1].strip()  # Argumen perintah

                print(f"Client {self.client_address} executed command: {cmd} {arg}")

                if cmd == 'LIST':
                    self.list_files()  # Menampilkan daftar file
                elif cmd == 'RETR':
                    self.retrieve_file(arg)  # Mengambil file
                    self.retr_count += 1
                    self.update_client_operations('RETR')  # Memperbarui operasi RETR
                elif cmd == 'STOR':
                    self.store_file(arg)  # Menyimpan file
                    self.stor_count += 1
                    self.update_client_operations('STOR')  # Memperbarui operasi STOR
                elif cmd == 'CWD':
                    self.change_dir(arg)  # Mengubah direktori kerja
                elif cmd == 'QUIT':
                    self.is_connected = False  # Menghentikan koneksi
                elif cmd == 'ACTIVE':
                    self.active_clients()  # Menampilkan klien aktif
        except ConnectionResetError:
            print(f"Connection reset by client {self.client_address}")
        finally:
            self.remove_client()  # Menghapus klien dari daftar aktif
            self.client_socket.close()  # Menutup socket klien
            print(f"Client {self.client_address} disconnected. STOR count: {self.stor_count}, RETR count: {self.retr_count}")

    def add_client(self):
        active_clients.append(self.client_address)  # Menambahkan klien ke daftar aktif
        if self.client_address not in client_operations:
            client_operations[self.client_address] = {'RETR': 0, 'STOR': 0}  # Inisialisasi operasi klien
        print(f"Client {self.client_address} connected. Current active clients: {len(active_clients)}")

    def remove_client(self):
        if self.client_address in active_clients:
            active_clients.remove(self.client_address)  # Menghapus klien dari daftar aktif
        print(f"Client {self.client_address} disconnected. Current active clients: {len(active_clients)}")
        
        # Memeriksa apakah tidak ada klien aktif
        if not active_clients:
            self.display_most_active_client()  # Menampilkan klien paling aktif
            self.reset_client_operations()  # Mengatur ulang operasi klien

    def list_files(self):
        files = os.listdir(self.cwd)  # Mendapatkan daftar file di direktori saat ini
        self.client_socket.send(bytes('\n'.join(files), "utf-8"))  # Mengirim daftar file ke klien

    def retrieve_file(self, filename):
        file_path = os.path.join(self.cwd, filename)  # Mendapatkan path file
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            self.client_socket.sendall(data)  # Mengirim data file ke klien
            self.client_socket.send(b'EOF')  # Mengirim EOF
            self.client_socket.send(b"File transfer completed.")  # Mengirim pesan selesai
        else:
            self.client_socket.send(bytes("Error: File not found.", "utf-8"))  # File tidak ditemukan

    def store_file(self, filename):
        length = int.from_bytes(self.client_socket.recv(4), 'big')  # Menerima panjang file
        received = 0
        with open(os.path.join(self.cwd, filename), 'wb') as f:
            while received < length:
                self.client_socket.settimeout(5)
                try:
                    chunk = self.client_socket.recv(1024)  # Menerima data file
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
        self.client_socket.send(b"File upload completed.")  # Mengirim pesan selesai

    def change_dir(self, new_dir):
        try:
            new_path = os.path.join(self.cwd, new_dir)  # Mendapatkan path direktori baru
            if os.path.isdir(new_path):
                self.cwd = new_path  # Mengubah direktori kerja
                self.client_socket.send(bytes("Changed working directory to " + self.cwd, "utf-8"))
            else:
                self.client_socket.send(bytes("Failed to change directory: Directory not found.", "utf-8"))
        except Exception as e:
            self.client_socket.send(bytes("Failed to change directory: " + str(e), "utf-8"))

    def active_clients(self):
        self.client_socket.send(bytes(str(active_clients), "utf-8"))  # Mengirim daftar klien aktif

    def update_client_operations(self, operation):
        if self.client_address in client_operations:
            client_operations[self.client_address][operation] += 1  # Memperbarui operasi klien
            print(f"Client {self.client_address} - {operation} count: {client_operations[self.client_address][operation]}")

    def display_most_active_client(self):
        if client_operations:
            max_retr_client = max(client_operations.items(), key=lambda x: x[1]['RETR'])  # Klien dengan unduhan terbanyak
            max_stor_client = max(client_operations.items(), key=lambda x: x[1]['STOR'])  # Klien dengan unggahan terbanyak

            max_retr_clients = [client for client, ops in client_operations.items() if ops['RETR'] == max_retr_client[1]['RETR']]
            max_stor_clients = [client for client, ops in client_operations.items() if ops['STOR'] == max_stor_client[1]['STOR']]

            if max_retr_client[1]['RETR'] > 0:
                if len(max_retr_clients) > 1:
                    print(f"Clients with the same number of downloads (RETR): {', '.join(map(str, max_retr_clients))} with {max_retr_client[1]['RETR']} downloads each")
                else:
                    print(f"Client with the most downloads (RETR): {max_retr_client[0]} with {max_retr_client[1]['RETR']} downloads")

            if max_stor_client[1]['STOR'] > 0:
                if len(max_stor_clients) > 1:
                    print(f"Clients with the same number of uploads (STOR): {', '.join(map(str, max_stor_clients))} with {max_stor_client[1]['STOR']} uploads each")
                else:
                    print(f"Client with the most uploads (STOR): {max_stor_client[0]} with {max_stor_client[1]['STOR']} uploads")

    def reset_client_operations(self):
        global client_operations
        client_operations = {}  # Mengatur ulang operasi klien

# Membuat socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('192.168.0.114', 12345)  # Alamat server
print('Starting up on {} port {}'.format(*server_address))
server_socket.bind(server_address)  # Mengikat socket ke alamat
print('Binding successful, now listening...')
server_socket.listen(5)  # Mendengarkan koneksi
print("FTP Server started...")

active_clients = []  # Daftar klien aktif
client_operations = {}  # Operasi klien

while True:
    print('Waiting for a connection...')
    client_socket, client_address = server_socket.accept()  # Menerima koneksi klien
    new_thread = ClientThread(client_address, client_socket)  # Membuat thread baru untuk klien
    new_thread.start()  # Memulai thread baru
    time.sleep(0.1)  # Menunggu sejenak sebelum menerima koneksi berikutnya
