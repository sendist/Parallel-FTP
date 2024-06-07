import socket
import time

# Membuat socket TCP
print('Creating socket...')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.0.114', 12345)  # Menggunakan alamat IP server yang benar

# Menghubungkan ke server
print('Connecting to {} port {}'.format(*server_address))
try:
    client_socket.connect(server_address)  # Mencoba menghubungkan ke server
    print('Connection successful')
    client_socket.sendall(b'CONNECTED')  # Mengirimkan pesan koneksi ke server
except Exception as e:  # Menangkap pengecualian jika koneksi gagal
    print(f'Failed to connect: {e}')
    client_socket.close()  # Menutup socket jika koneksi gagal
    exit()

try:
    while True:
        command = input("Enter command (LIST, RETR <filename>, STOR <filename>, CWD <directory>, QUIT): ")
        cmd = command.split(' ', 1)[0].upper()
        if cmd not in ['LIST', 'RETR', 'STOR', 'CWD', 'QUIT']:
            print("Error: command not valid")
            continue

        if cmd == 'QUIT':
            client_socket.sendall(command.encode())  # Mengirimkan perintah QUIT ke server
            break  # Keluar dari loop jika perintah adalah QUIT

        client_socket.sendall(command.encode())  # Mengirimkan perintah ke server
        time.sleep(0.1)  # Menunggu sebentar untuk menghindari masalah sinkronisasi

        if cmd == 'RETR':  # Jika perintah adalah RETR
            filename = command.split(' ', 1)[1]  # Mendapatkan nama file
            total_data = b""  # Buffer untuk menyimpan data yang diterima
            while True:
                data = client_socket.recv(1024)  # Menerima data dari server
                if b'EOF' in data:  # Jika tanda EOF ditemukan
                    total_data += data[:data.index(b'EOF')]  # Tambahkan data hingga EOF
                    confirmation = data[data.index(b'EOF')+3:]  # Simpan konfirmasi
                    break
                else:
                    total_data += data  # Tambahkan data ke buffer
            with open(filename, 'wb') as f:  # Membuka file untuk menulis
                f.write(total_data)  # Menulis data ke file
            print(confirmation.decode().strip())  # Tampilkan pesan konfirmasi
            print("File downloaded successfully.")

        elif cmd == 'STOR':  # Jika perintah adalah STOR
            try:
                with open(command.split(' ', 1)[1], 'rb') as f:  # Membuka file untuk membaca
                    data = f.read()  # Membaca seluruh isi file
                client_socket.sendall(len(data).to_bytes(4, 'big'))  # Mengirimkan ukuran data
                client_socket.sendall(data)  # Mengirimkan data
                client_socket.sendall(b'EOF')  # Mengirimkan tanda EOF
                confirmation = client_socket.recv(1024)  # Menerima konfirmasi dari server
                print(confirmation.decode().strip())  # Tampilkan pesan konfirmasi
            except FileNotFoundError:
                print("Error: File not found.")  # Tampilkan pesan error jika file tidak ditemukan

        elif cmd == 'LIST' or cmd == 'CWD':  # Jika perintah adalah LIST atau CWD
            response = client_socket.recv(1024).decode()  # Menerima dan decode respons dari server
            print(response)  # Tampilkan respons

finally:
    print('Closing socket')
    try:
        client_socket.sendall(b'DISCONNECTED')  # Mengirimkan pesan koneksi ke server
    except ConnectionResetError:
        pass
    client_socket.close()  # Menutup socket
