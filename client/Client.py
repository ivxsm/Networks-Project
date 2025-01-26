import socket as socket 
import struct 


Server_IP = socket.gethostbyname(socket.gethostname()) # Get the IP address of the server
Server_PORT = 1234 
Address = (Server_IP, Server_PORT) # Tuple of the IP and the PORT
Buffer_Size = 1024 # for sending/receiving data 
Fragment_Size = 4 # the fragment (segment) number.


# in the clinet side we will have three functions:

#first same as sever side to calculate the checksum


def calc_checksum(file):
    if len(file) % 2 != 0:
        file += b'\0'
    checksum = 0
    for i in range(0, len(file), 2):
        word = (file[i] << 8) + file[i + 1]
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16) 
    print("before one's complement: ", checksum)       
    print("after one's complement: ",( ~checksum & 0xffff))
    return ~checksum & 0xffff

# second function to verify cheacksum

def verify_checksum(file, received_checksum):
    calculated_checksum = calc_checksum(file)
    return calculated_checksum == received_checksum

 
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    print(f"Connecting to the server {Server_IP} : {Server_PORT} ...")
    client.connect(Address) 
    
    file_name = input("Enter the file name: ").strip()
    client.send(file_name.encode()) 
    
    fragments = [None] * Fragment_Size
    retry = 0
    
    while True :
        data = client.recv(Buffer_Size)
        if not data:
            break   
        if data.startswith(b"File not found"):
            print("File not found on the server")
            client.close()
            return
        elif data.startswith(b"Transfer failed"):
            print("File transfer failed. The server could not send the file.")
            client.close()
            return
        elif data.startswith(b"Transfer complete"):
            print("File transfer completed successfully.")
            break
        
        header = data[:4]
        seq_num, checksum = struct.unpack("!HH", header)
        fragment_data = data[4:]
        
        if verify_checksum(fragment_data,checksum):
            print(f"Received fragment {seq_num}")
            fragments[seq_num] = fragment_data
            client.send(f"ACK:{seq_num}".encode())
        else:
            print(f"Fragment {seq_num} is corrupted.")
            client.send(f"NACK:{seq_num}".encode())
            retry += 1
            if retry >= 5:
                print("Max retry reached. File transfer failed.")
                client.close()
                return
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