import socket
import time

print('Creating socket...')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.168.168', 12345)  # Menggunakan alamat IP server yang benar

print('Connecting to {} port {}'.format(*server_address))
try:
    client_socket.connect(server_address)
    print('Connection successful')
    client_socket.sendall(b'CONNECTED')  # Mengirimkan pesan koneksi ke server
except Exception as e:
    print(f'Failed to connect: {e}')
    client_socket.close()
    exit()

try:
    while True:
        command = input("Enter command (LIST, RETR <filename>, STOR <filename>, CWD <directory>, QUIT, ACTIVE): ")
        cmd = command.split(' ', 1)[0].upper()
        if cmd not in ['LIST', 'RETR', 'STOR', 'CWD', 'QUIT', 'ACTIVE']:
            print("Error: command not valid")
            continue

        if cmd == 'QUIT':
            client_socket.sendall(command.encode())
            break

        client_socket.sendall(command.encode())
        time.sleep(0.1)

        if cmd == 'RETR':
            filename = command.split(' ', 1)[1]
            total_data = b""
            while True:
                data = client_socket.recv(1024)
                if b'EOF' in data:
                    total_data += data[:data.index(b'EOF')]
                    confirmation = data[data.index(b'EOF')+3:]
                    break
                else:
                    total_data += data
            with open(filename, 'wb') as f:
                f.write(total_data)
            print(confirmation.decode().strip())  # Tampilkan pesan konfirmasi
            print("File downloaded successfully.")

        elif cmd == 'STOR':
            try:
                with open(command.split(' ', 1)[1], 'rb') as f:
                    data = f.read()
                client_socket.sendall(len(data).to_bytes(4, 'big'))
                client_socket.sendall(data)
                client_socket.sendall(b'EOF')
                confirmation = client_socket.recv(1024)  # Tunggu konfirmasi
                print(confirmation.decode().strip())  # Tampilkan pesan konfirmasi
            except FileNotFoundError:
                print("Error: File not found.")

        elif cmd == 'LIST' or cmd == 'CWD':
            response = client_socket.recv(1024).decode()
            print(response)

        elif cmd == 'ACTIVE':
            active_clients = client_socket.recv(1024).decode()
            print("Active clients: ", active_clients)

finally:
    print('Closing socket')
    try:
        client_socket.sendall(b'DISCONNECTED')  # Mengirimkan pesan koneksi ke server
    except ConnectionResetError:
        pass
    client_socket.close()
