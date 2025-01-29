import socket as socket
import struct
import time

# Constants
Server_IP = socket.gethostbyname(socket.gethostname())
#Server_IP = ''  # write your real ip and comment the above line
Server_PORT = 4000
Address = (Server_IP, Server_PORT)
Buffer_Size = 1024
Fragment_Size = 4

# Statistics tracking
class TransferStats:
    def __init__(self):
        self.total_fragments = 0
        self.corrupted_fragments = 0
        self.retransmissions = 0
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def print_stats(self):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            print("\nTransfer Statistics:")
            print(f"Total fragments: {self.total_fragments}")
            print(f"Corrupted fragments: {self.corrupted_fragments}")
            print(f"Retransmissions: {self.retransmissions}")
            print(f"Error rate: {(self.corrupted_fragments/self.total_fragments)*100:.2f}%")
            print(f"Transfer duration: {duration:.2f} seconds")

def calc_checksum(file):
    if len(file) % 2 != 0:
        file += b'\0'
    checksum = 0
    for i in range(0, len(file), 2):
        word = (file[i] << 8) + file[i + 1]
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)
    return ~checksum & 0xffff

def verify_checksum(file, received_checksum):
    calculated_checksum = calc_checksum(file)
    return calculated_checksum == received_checksum

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to the server {Server_IP} : {Server_PORT} ...")
    client.connect(Address)

    # Receive welcome message and send acknowledgment
    welcome = client.recv(Buffer_Size)
    print(welcome.decode())
    client.send(b"ACK")

    while True:
        file_name = input("Enter the file name (or 'exit' to quit): ").strip()
        client.send(file_name.encode())
        
        if file_name.lower() == "exit":
            print("Exiting...")
            break

        fragments = [None] * Fragment_Size
        stats = TransferStats()
        stats.start()
        retry = 0

        while True:
            data = client.recv(Buffer_Size)
            if not data:
                print("Connection closed by server")
                break

            if data.startswith(b"File not found"):
                print("File not found on the server")
                break
            elif data.startswith(b"File sent successfully"):
                stats.stop()
                stats.print_stats()
                print("File transfer completed successfully.")
                break
            elif data.startswith(b"Transmission failed"):
                stats.stop()
                stats.print_stats()
                print("File transfer failed. The server could not send the file.")
                break
            elif data.startswith(b"An error occurred"):
                print("Server encountered an error processing the request")
                break

            stats.total_fragments += 1
            header = data[:4]
            seq_num, checksum = struct.unpack("!HH", header)
            fragment_data = data[4:]

            if verify_checksum(fragment_data, checksum):
                print(f"Received fragment {seq_num}")
                fragments[seq_num] = fragment_data
                client.send(f"ACK:{seq_num}".encode())
            else:
                print(f"Fragment {seq_num} is corrupted.")
                stats.corrupted_fragments += 1
                stats.retransmissions += 1
                client.send(f"NACK:{seq_num}".encode())
                retry += 1
                if retry >= 5:
                    print("Max retry reached. File transfer failed.")
                    stats.stop()
                    stats.print_stats()
                    client.close()
                    return

        if all(fragment is not None for fragment in fragments):
            file_data = b"".join(fragments)
            with open(f"received_{file_name}", "wb") as file:
                file.write(file_data)
            print(f"File '{file_name}' reassembled and saved as 'received_{file_name}'.")
        else:
            print("File transfer incomplete. Some fragments are missing.")

    client.close()

if __name__ == "__main__":
    main()