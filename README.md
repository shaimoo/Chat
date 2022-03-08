# Chat&file-transfer
  develop a meassenger chat multithreading 
  the project problem the file tranfer with UDP protocol that implemrnting GO-N-BACK realaibel 
  
 ## server <br />
  this class is server class and it has folowing functions
  | Name of function | Description |
  |------------------|-------------|
  | def __init__(self, port, ip, ) | building new server.|
  | def broadcast(self, message)  | send message to all clients that online. |
  | def list_users(self, user_socket)  | send list of all users online to spesific client.  |
  | def list_files(self, user_socket)  | send list of all files that client can download. |
  | def private_message(self, message, name) | send a message to spesific client.|
  | def handle(self, client: ChatClient)| hendel with client orders.|
  | def sender(self, client) | send the file to client with UDP protocole implementing GO-N-BACK with timer.|
  | def file_exists(self, filename) | return True if the file is exists False o.w.|
  | def receive(self) |  add new client to the chat and send message to all the users when new client log in and send message to all when we log out that he laft.|

  
  ## client
    this class represent the client of the chat ,
  
  
 ## how to download 
  To download the task from GitHub, you should navigate to the top level of the project , and then a green "Code" download button will be visible on the right. Choose the Download ZIP option from the Code pull-down menu. That ZIP file will contain the entire repository content.

## how to use
After you download the task at zip you need to extract the zip file , then you need to open cmd going to to your file location aka cd "file location" when you be on the file location first you need to run the server , then run the client give the name of the clinet

## test
tets the server and clinet, chack every function with exmples to see the correctness of the function
