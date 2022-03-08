import socket
import threading
import time


class ChatClient():

    def __init__(self, chat_socket, name, file_socket, address):
        self.chat_socket = chat_socket
        self.name = name
        self.files_socket = file_socket
        self.address = address
        self.name_file = None


class Server():
    def __init__(self, port, ip, ):
        self.port = port
        self.host = ip
        self.clients = {}
        self.start_time = -1
        self.max_time = 1
        self.window_size = 5
        self.files = ["cat.jpg", "dog.jpg", "list.txt"]
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket_file = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.handle_new_client_thread = threading.Thread(target=self.receive)
        self.handle_new_client_thread.start()

    def broadcast(self, message):
        if len(self.clients) > 0:
            for user in self.clients.values():
                print(f"About to send to: {user.name}. msg: {message}")
                sock = user.chat_socket
                sock.send(message)

    def list_users(self, user_socket):
        online = "-----The online users are------\n"
        for name in self.clients.values():
            online += str(name.name)
            online += " , "
        user_socket.send(online.encode('ascii'))

    def list_files(self, user_socket):
        files_names = "-----The files are------\n"
        for file in self.files:
            files_names += str(file)
            if file != self.files[len(self.files) - 1]:
                files_names += " , "
        user_socket.send(files_names.encode('ascii'))

    def private_message(self, message, name):
        for client in self.clients.values():
            if str(client.name) == name:
                user = client.chat_socket
                user.send(message)

    def handle(self, client: ChatClient):
        while True:
            numbers = []
            message = client.chat_socket.recv(1024).decode('ascii')
            x = str(message).split(",")
            if x[0].isdigit():
                action = int(x[0])
            else:
                message = client.chat_socket.recv(1024).decode('ascii')
                x = str(message).split(",")
                action = int(x[0])

            while len(numbers) == 0:
                if 0 < action < 9:
                    numbers.append(action)
                    break
                message = client.chat_socket.recv(1024).decode('ascii')

            if numbers[0] == 2:
                name = client.name
                socket_chat = client.chat_socket
                files_socket = client.files_socket
                self.clients.pop(name)
                print(f"Deleted client {name} from clients list")

                socket_chat.close()
                # files_socket.close()
                self.broadcast('{} left'.format(name).encode('ascii'))
                break

            if numbers[0] == 3:
                x = str(message).split(",")
                name_sender = x[1]
                message_n = "privat message from:" + str(name_sender) + ":" + str(x[2])
                for i in range(3, len(x)):
                    message_n += x[i]
                self.private_message(message_n.encode('ascii'), str(x[1]))

            if numbers[0] == 4:
                x = str(message).split(",")
                message = client.name + ":" + x[1]
                for i in range(3, len(x)):
                    message += "," + x[i]
                self.broadcast(message.encode('ascii'))

            if numbers[0] == 5:
                self.list_users(client.chat_socket)

            if numbers[0] == 6:
                self.list_files(client.chat_socket)

            if numbers[0] == 7:
                x = str(message).split(",")
                if (len(x) < 2):
                    client.chat_socket.send("Please specify filename".encode('ascii'))
                    continue
                filename = x[1]
                if self.file_exists(filename):
                    # send ok you can download
                    client.chat_socket.send("ok you can download".encode('ascii'))
                    client.name_file = filename
                else:
                    # err file not found
                    client.chat_socket.send("eror file not found".encode('ascii'))

            if numbers[0] == 8:
                print(f"got 8 from {client.name}")
                tread_download = threading.Thread(target=self.sender, args=(client,))
                tread_download.start()

    def sender(self, client):

        packets = []
        num_of_packet = 0

        with open(client.name_file, 'rb') as f:
            # Add all packets and number them
            file_contents = f.read(1020)
            while file_contents:
                packets.append(self.make_packet(num_of_packet, file_contents))
                num_of_packet += 1
                file_contents = f.read(1020)

        num_packets = len(packets)
        print('Num packets: ', num_packets)
        next_frame = 0
        sent_packet = 0
        window = self.set_window(num_packets, sent_packet)

        # Send the packet
        while sent_packet < num_packets:
            # Send all packets within the window
            while next_frame < sent_packet + window and next_frame < num_packets:
                #print(f'Send packet {next_frame} to {client.address}')
                self.server_socket_file.sendto(packets[next_frame], (client.chat_socket.getpeername()))
                next_frame += 1
            # Wait till time is up or acknowledgement
            self.Start_Timer()
            while self.Is_Timer_run() and not self.TimeOut_Timer():
                #print(f'waiting to get ack on: {sent_packet}')
                data = self.server_socket_file.recvfrom(1024)
                if data:
                    ack = data[0]
                   # print('get ack ', ack)
                    if int(ack) >= sent_packet:
                        sent_packet = int(ack) + 1
                        self.Stop_timer()
                    else:
                        sent_packet = int(ack)
                        next_frame = sent_packet
                        self.Stop_timer()
            if self.TimeOut_Timer():
                self.Stop_timer()
                next_frame = sent_packet
            else:
                #print('Shifting window.')
                window_size = self.set_window(num_packets, sent_packet)

    def file_exists(self, filename) -> bool:
        for file in self.files:
            if file == filename:
                return True

        return False

    def receive(self):
        while True:
            user_socket, address = self.server_socket.accept()
            print("connected with {}".format(str(address)))
            name = user_socket.recv(1024).decode('ascii')
            # self.server_socket_file.bind((address[0], address[1]))

            client = ChatClient(chat_socket=user_socket, name=name, file_socket=self.server_socket_file, address=address)
            if name in self.clients:
                user_socket.send("Name already in use {}. please choose different name".format(name).encode('ascii'))
                break
            self.clients[name] = client
            print("name of client is :{}".format(name))
            self.broadcast("{} is now online ! \n ".format(name).encode('ascii'))
            user_socket.send("connected to the server ".encode('ascii'))
            tread = threading.Thread(target=self.handle, args=(client,))
            tread.start()

    def set_window(self, num_packets, packet_resive):
        return min(self.window_size, num_packets - packet_resive)

    # def send_data(self, packet,client):


    def make_packet(self, acknum, data=b''):
        ackbytes = acknum.to_bytes(4, byteorder='little', signed=True)
        return ackbytes + data

    def Start_Timer(self):
        if self.start_time == -1:
            self.start_time = time.time()

    def Stop_timer(self):
        if self.start_time != -1:
            self.start_time = -1

    def Is_Timer_run(self):
        return self.start_time != -1

    def TimeOut_Timer(self):
        if not self.Is_Timer_run():
            return False
        else:
            return time.time() - self.start_time >= self.max_time


if __name__ == '__main__':
    print("server run...")
    server = Server(port=50000, ip='127.0.0.1')
    server.receive()
