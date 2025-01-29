File transfer between client and server Using Socket Programming with a Checksum :
actually dont read me , this is just some notes to take 
things we need ;

The server will operate in passive mode
1 - The client will initiate a connection to the server using a given IP address and port number
2- If the server is unavailable, the client should display the message: “Server is down, please try again later.”

now we connected :
the client must validate the input. For example, the request must
not be empty, and a filename must be provided. An invalid request (e.g., an empty request)
will trigger an error message on the client side, informing the user that there was an issue
with the request.
the client will request a file from the server by providing its filename
The server will search its local directory (where the server code is located) for the requested file
If the file is not found, the server will send
a message to inform the client that the requested file is unavailable (e.g., “The file [file
name] you requested does not exist in this folder”).

else 

the server will send it back to the client

fouces on the server 


1- give it a ip and port 
2- reserve the file name 
3- search in the local directory using os library ,(not found ? send message not found : contuine )
4- apply fragmentation to split the file into smaller parts segments (4).
5- assign each part to a unique sequence number o ensure that the segments can be
properly reordered by the client upon receipt.
6- A 16-bit one's complement checksum will be calculated by the server for each file segment
before transmission , The checksum for each segment is computed separately and then
concatenated with the segment. The server sends the segment along with its checksum to
the client.






