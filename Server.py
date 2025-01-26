import socket as scoket
import struct  # to convert the size of the file to bytes
import os  # to search in the inside system.

# Constants
Server_IP = scoket.gethostbyname(scoket.gethostname())  # Get the IP address of the server
Server_PORT = 1234
Address = (Server_IP, Server_PORT)  # Tuple of the IP and the PORT
Buffer_Size = 1024  # for sending/receiving data
Fragment_Size = 4  # the fragment (segment) number.
Min_File_Size = 1  # the minimum size of the file
Max_retry = 5  # the maximum number of retries

# we will have two functions in the server side:

# first one to calculate the checksum
def checksum(file):
    if len(file) % 2 != 0:
        file += b'\0'
    checksum = 0
    for i in range(0, len(file), 2):
        word = (file[i] << 8) + file[i + 1]
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)
    print("before one's complement: ", checksum)
    print("after one's complement: ", (~checksum & 0xffff))
    return ~checksum & 0xffff

# second one to split the file into segments then calculate the checksum for each segment
def split_file(file):
    file_data = open(file, "rb").read()  # read the file in binary mode
    file_size = os.path.getsize(file)  # get the size of the file
    inner_fragment_Size = file_size // Fragment_Size  # the size of each segment -used another variable to avoid confusion with-
    segments = []  # list to store the segments

    for i in range(Fragment_Size):
        start = i * inner_fragment_Size
        end = (i + 1) * inner_fragment_Size if i != Fragment_Size - 1 else file_size
        fragment = file_data[start:end]
        checksum_value = checksum(fragment)  # Renamed to avoid conflict with the function name
        segments.append((i, checksum_value, fragment))
    return segments

def main():
    server = scoket.socket(scoket.AF_INET, scoket.SOCK_STREAM)
    server.bind(Address)
    server.listen(1)
    print(f"Server is listening on {Server_IP} : {Server_PORT} ...")

    while True:
        client_socket, client_address = server.accept()
        print(f"Connection from {client_address} has been established!")
        client_socket.send("Welcome to the server!".encode())
        file = client_socket.recv(Buffer_Size).decode().strip()  # receive the file name
        print(f"Client requested: {file}")

        if not os.path.exists(file):
            client_socket.send("File not found".encode())
            print(f"File {file} not found")
            client_socket.close()
            continue

        file_size = os.path.getsize(file)
        if file_size < Min_File_Size:
            client_socket.send(f"File is too small ({file_size} bytes), it must be at least {Min_File_Size} bytes".encode())
            print(f"File is too small ({file_size} bytes), it must be at least {Min_File_Size} bytes")
            client_socket.close()
            continue

        fragments = split_file(file)
        for seq_num, checksum_value, fragment in fragments:
            retry = 0
            while retry < Max_retry:
                header = struct.pack("!HH", seq_num, checksum_value)  # Pack sequence number and checksum
                message = header + fragment
                client_socket.send(message)
                print(f"Sent fragment {seq_num} with checksum {checksum_value}")

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
        client_socket.close()

if __name__ == "__main__":
    main()