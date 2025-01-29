import socket
import struct
import os
from threading import Thread
import random

# Constants
Server_IP = socket.gethostbyname(socket.gethostname())
#Server_IP = ''  # write your real ip and comment the above line
Server_PORT = 4000
Address = (Server_IP, Server_PORT)
Buffer_Size = 1024
Fragment_Size = 4
Min_File_Size = 1
Max_retry = 5

# Error simulation probability (can be changed to 0.3, 0.5, or 0.8)
ERROR_PROBABILITY = 0

def introduce_error(data):
    """Randomly introduce errors into the data"""
    if random.random() < ERROR_PROBABILITY:
        # Convert to bytearray to make it mutable
        data = bytearray(data)
        # Randomly select a position to corrupt
        pos = random.randint(0, len(data) - 1)
        # Flip a random bit in the selected byte
        data[pos] ^= (1 << random.randint(0, 7))
        return bytes(data)
    return data

def checksum(file):
    if len(file) % 2 != 0:
        file += b'\0'
    checksum = 0
    for i in range(0, len(file), 2):
        word = (file[i] << 8) + file[i + 1]
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)
    return ~checksum & 0xffff

def split_file(file):
    file_data = open(file, "rb").read()
    file_size = os.path.getsize(file)
    inner_fragment_Size = file_size // Fragment_Size
    segments = []

    for i in range(Fragment_Size):
        start = i * inner_fragment_Size
        end = (i + 1) * inner_fragment_Size if i != Fragment_Size - 1 else file_size
        fragment = file_data[start:end]
        checksum_value = checksum(fragment)
        segments.append((i, checksum_value, fragment))
    return segments

def handle_client(client_socket, client_address):
    print(f"Connection from {client_address} has been established!")
    # Send initial welcome message
    welcome_msg = "Welcome to the server!".encode()
    client_socket.send(welcome_msg)
    # Wait for client acknowledgment
    client_socket.recv(Buffer_Size)

    while True:
        try:
            file = client_socket.recv(Buffer_Size).decode().strip()
            if file.lower() == "exit":
                print(f"Client {client_address} requested to exit.")
                break

            print(f"Client requested: {file}")
            
            # Get the absolute path of the current directory
            current_dir = os.path.abspath(os.path.dirname(__file__))
            file_path = os.path.join(current_dir, file)
            
            print(f"Looking for file at: {file_path}")

            if not os.path.exists(file_path):
                error_msg = "File not found".encode()
                client_socket.send(error_msg)
                print(f"File {file_path} not found")
                continue

            file_size = os.path.getsize(file_path)
            if file_size < Min_File_Size:
                error_msg = f"File is too small ({file_size} bytes), it must be at least {Min_File_Size} bytes".encode()
                client_socket.send(error_msg)
                print(f"File is too small ({file_size} bytes), it must be at least {Min_File_Size} bytes")
                continue

            fragments = split_file(file_path)
            for seq_num, checksum_value, fragment in fragments:
                retry = 0
                while retry < Max_retry:
                    # Introduce errors into the fragment data
                    corrupted_fragment = introduce_error(fragment)
                    
                    header = struct.pack("!HH", seq_num, checksum_value)
                    message = header + corrupted_fragment
                    client_socket.send(message)
                    print(f"Sent fragment {seq_num} with checksum {checksum_value}")
                    if fragment != corrupted_fragment:
                        print(f"Error introduced in fragment {seq_num}")

                    ack = client_socket.recv(Buffer_Size).decode().strip()
                    if ack == f"ACK:{seq_num}":
                        print(f"Fragment {seq_num} acknowledged by the client")
                        break
                    else:
                        retry += 1
                        print(f'Fragment {seq_num} not acknowledged by the client, retrying {retry} of {Max_retry}')

                if retry == Max_retry:
                    print(f"Fragment {seq_num} not acknowledged by the client, maximum retries reached")
                    client_socket.send('Transmission failed'.encode())
                    client_socket.close()
                    return

            print(f"File {file} sent successfully")
            client_socket.send("File sent successfully".encode())
            
        except Exception as e:
            print(f"Error handling client request: {e}")
            error_msg = "An error occurred while processing your request".encode()
            try:
                client_socket.send(error_msg)
            except:
                pass
            break

    print(f"Closing connection with {client_address}")
    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(Address)
    server.listen(5)
    print(f"Server is listening on {Server_IP} : {Server_PORT} ...")
    print(f"Current error probability: {ERROR_PROBABILITY}")
    print(f"Server working directory: {os.path.abspath(os.path.dirname(__file__))}")

    while True:
        client_socket, client_address = server.accept()
        print(f"New connection from {client_address}")

        client_thread = Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    main()