# Parallel-FTP

This repository contains a simple implementation of a parallel FTP server and client using Python sockets. The server can handle multiple client connections concurrently, allowing for parallel file transfers.

## Getting Started

### Prerequisites

- Python 3.x

### Running the Server

1. Open a terminal or command prompt.
2. Navigate to the repository directory.
3. Run the following command to start the server:

    ```bash
    python serverFTP.py
    ```

   The server will start listening for incoming connections on the specified IP address and port.

### Running the Client

1. Open another terminal or command prompt.
2. Navigate to the repository directory.
3. Run the following command to start the client:

    ```bash
    python clientFTP.py
    ```

   The client will attempt to connect to the server. Once connected, you can use the following commands:

   - `LIST`: List files and directories in the current working directory on the server.
   - `RETR <filename>`: Retrieve a file from the server.
   - `STOR <filename>`: Upload a file to the server.
   - `CWD <directory>`: Change the working directory on the server.
   - `QUIT`: Disconnect from the server.
   - `ACTIVE`: Display a list of active clients connected to the server.

## Project Contributors

- Egi Satria (211524040)
- Regi Purnama (211524057)
- Rivaldo Fauzan Robani (211524060)
- Sendi Setiawan (211524062)
