import socket
import struct
import os
from threading import Thread

# Constants
Server_IP = '127.0.0.1'  # Server's IP
Server_PORT = 4000
Address = (Server_IP, Server_PORT)  # Tuple of the IP and the PORT
Buffer_Size = 1024  # for sending/receiving data
Fragment_Size = 4  # Number of fragments
Min_File_Size = 1  # Minimum file size
Max_retry = 5  # Maximum number of retries
Timeout = 5  # Timeout duration for waiting for acknowledgment

# Function to calculate checksum
def checksum(file):
    if len(file) % 2 != 0:
        file += b'\0'
    checksum = 0
    for i in range(0, len(file), 2):
        word = (file[i] << 8) + file[i + 1]
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)
    return ~checksum & 0xffff

# Function to split the file into segments
def split_file(file):
    file_data = open(file, "rb").read()  # Read the file in binary mode
    file_size = os.path.getsize(file)  # Get the size of the file
    inner_fragment_size = file_size // Fragment_Size  # The size of each fragment
    segments = []  # List to store the segments

    for i in range(Fragment_Size):
        start = i * inner_fragment_size
        end = (i + 1) * inner_fragment_size if i != Fragment_Size - 1 else file_size
        fragment = file_data[start:end]
        checksum_value = checksum(fragment)
        segments.append((i, checksum_value, fragment))
    return segments

# Function to handle each client connection
def handle_client(client_socket, client_address):
    print(f"Connection from {client_address} established!")
    client_socket.send("Welcome to the server!".encode())

    try:
        while True:
            try:
                file = client_socket.recv(Buffer_Size).decode().strip()  # Receive the file name
                if not file:  # Client disconnected
                    print(f"Client {client_address} disconnected.")
                    break

                if file.lower() == "exit":
                    print(f"Client {client_address} requested to exit.")
                    break

                print(f"Client requested: {file}")

                if not os.path.exists(file):
                    client_socket.send("File not found".encode())
                    print(f"File {file} not found")
                    continue

                file_size = os.path.getsize(file)
                if file_size < Min_File_Size:
                    client_socket.send(f"File is too small ({file_size} bytes), it must be at least {Min_File_Size} bytes".encode())
                    print(f"File is too small ({file_size} bytes), it must be at least {Min_File_Size} bytes")
                    continue

                fragments = split_file(file)
                for seq_num, checksum_value, fragment in fragments:
                    retry = 0
                    while retry < Max_retry:
                        header = struct.pack("!HH", seq_num, checksum_value)  # Pack sequence number and checksum
                        message = header + fragment
                        client_socket.send(message)
                        print(f"Sent fragment {seq_num} with checksum {checksum_value}")

                        try:
                            client_socket.settimeout(Timeout)  # Set timeout for acknowledgment
                            ack = client_socket.recv(Buffer_Size).decode().strip()
                            print(f"Received ACK: {ack}")

                            if ack == f"ACK:{seq_num}":
                                print(f"Fragment {seq_num} acknowledged by the client")
                                break
                        except socket.timeout:
                            retry += 1
                            print(f"Fragment {seq_num} not acknowledged by the client, retrying {retry} of {Max_retry}")

                    if retry == Max_retry:
                        print(f"Fragment {seq_num} not acknowledged by the client, maximum retries reached")
                        client_socket.send('Transmission failed'.encode())
                        client_socket.close()
                        return

                print(f"File {file} sent successfully")
                client_socket.send("File sent successfully".encode())

            except Exception as e:
                print(f"Error occurred: {e}")
                break

    except TimeoutError:
        print(f"Timeout while communicating with {client_address}, closing connection.")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        print(f"Closing connection with {client_address}")
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(Address)
    server.listen(5)  # Allow up to 5 clients to queue
    print(f"Server is listening on {Server_IP} : {Server_PORT} ...")

    while True:
        client_socket, client_address = server.accept()
        print(f"New connection from {client_address}")
        # Create a new thread to handle the client
        client_thread = Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    main()
