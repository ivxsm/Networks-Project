import socket as socket 
IP = socket.gethostbyname(socket.gethostname()) 
PORT = 1234
ADDRESS = (IP, PORT) 

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(ADDRESS) 
    print(f"Connected to the server at {IP}")
    print('Good now we are closing thanks !')
    print(client.recv(1024).decode("utf-8")) 
    client.close()
    
if __name__ == "__main__":
    main()