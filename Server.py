import socket  as scoket


IP = scoket.gethostbyname(scoket.gethostname()) # Get the IP address of the server
PORT = 1234 
ADDRESS = (IP, PORT) 
list

def main():
    server = scoket.socket(scoket.AF_INET, scoket.SOCK_STREAM) 
    server.bind(ADDRESS)
    server.listen(5) 
    print(f"Server is listening on {IP}")

    while True:
        client, address = server.accept() 
        print(f"Connection from {address} has been established!")
        client.send(bytes("Welcome to the server! Enter the name of the file", "utf-8")) 
        #filename = client.recv(1024).decode("utf-8")
        client.close() 
        
if __name__ == "__main__":
    main()