import socket
import time

# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server's port
server_address = ('localhost', 12345)
print('Connecting to {} port {}'.format(*server_address))
client_socket.connect(server_address)

try:
    # Send commands
    while True:
        command = input("Enter command (LIST, RETR <filename>, STOR <filename>, CWD <directory>, QUIT): ")

        # Memastikan command yang diinput valid
        cmd = command.split(' ', 1)[0]
        if cmd not in ['LIST', 'RETR', 'STOR', 'CWD', 'QUIT']:
            print("Error: command not valid")
            continue

        # Menghentikan koneksi
        if command == 'QUIT':
            break

        client_socket.send(bytes(command, "utf-8"))
        time.sleep(0.1)

        # Mengunduh file dari server
        if command.split(' ', 1)[0] == 'RETR':
            length = int.from_bytes(client_socket.recv(4), 'big')
            with open(command.split(' ', 1)[1], 'wb') as f:
                while length:
                    chunk = client_socket.recv(1024)
                    if b'EOF' in chunk: 
                        f.write(chunk[:-3]) 
                        break
                    else:
                        f.write(chunk)
                        length -= len(chunk)

        # Mengunggah file ke server
        elif command.split(' ', 1)[0] == 'STOR':
            with open(command.split(' ', 1)[1], 'rb') as f:
                data = f.read()
                client_socket.sendall(len(data).to_bytes(4, 'big'))
                client_socket.sendall(data)
                client_socket.sendall(b'EOF')

        # Menampilkan daftar file dan folder pada direktori saat ini dan mengubah direktori
        else:
            print(client_socket.recv(1024).decode())

finally:
    print('Closing socket')
    client_socket.close()