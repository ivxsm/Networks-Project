import socket
import struct

# Constants
Server_IP = socket.gethostbyname(socket.gethostname())  # Automatically get the local IP address
#Server_IP =  # real ip address uncomment and 
Server_PORT = 4000
Address = (Server_IP, Server_PORT)  # Tuple of the IP and the PORT
Buffer_Size = 1024  # Buffer size for sending/receiving data
Fragment_Size = 4  # Number of fragments

# Function to calculate checksum
def calc_checksum(file):
    if len(file) % 2 != 0:
        file += b'\0'
    checksum = 0
    for i in range(0, len(file), 2):
        word = (file[i] << 8) + file[i + 1]
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)
    return ~checksum & 0xffff

# Function to verify checksum
def verify_checksum(file, received_checksum):
    calculated_checksum = calc_checksum(file)
    return calculated_checksum == received_checksum

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to the server {Server_IP} : {Server_PORT} ...")
    client.connect(Address)

    while True:
        file_name = input("Enter the file name (or 'exit' to quit): ").strip()
        client.send(file_name.encode())

        if file_name.lower() == "exit":
            print("Exiting...")
            break

        fragments = [None] * Fragment_Size

        while True:
            data = client.recv(Buffer_Size)
            if not data:
                break

            if data == b"EOF":
                print("File transfer completed successfully.")
                break

            # Check for server messages
            if data.startswith(b"File not found"):
                print("File not found on the server")
                break
            elif data.startswith(b"File sent successfully"):
                print("File transfer completed successfully.")
                break
            elif data.startswith(b"Transmission failed"):
                print("File transfer failed. The server could not send the file.")
                break

            # Unpack the header and fragment data
            header = data[:4]
            seq_num, checksum = struct.unpack("!HH", header)
            fragment_data = data[4:]

            # Verify the checksum
            if verify_checksum(fragment_data, checksum):
                print(f"Received fragment {seq_num}")
                if fragments[seq_num] is None:  # Avoid duplicate processing
                    fragments[seq_num] = fragment_data
                client.send(f"ACK:{seq_num}".encode())  # Send ACK to the server
            else:
                print(f"Fragment {seq_num} is corrupted.")
                client.send(f"NACK:{seq_num}".encode())  # Send NACK to the server

        # Check if all fragments are received
        if all(fragment is not None for fragment in fragments):
            file_data = b"".join(fragments)  # Combine all fragments
            with open(f"received_{file_name}", "wb") as file:
                file.write(file_data)
            print(f"File '{file_name}' reassembled and saved as 'received_{file_name}'.")
        else:
            print("File transfer incomplete. Some fragments are missing.")

    client.close()

if __name__ == "__main__":
    main()
