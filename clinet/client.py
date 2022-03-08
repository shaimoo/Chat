import socket
import threading
import time


class client():

    def __init__(self, port, host, name):
        self.server_connect_port = port
        self.name = name
        self.host = host
        self.client_port = None
        self.connect = False
        self.file_name = None
        self.client_socket_file = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def Start(self, name):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.server_connect_port))
        self.connect = True
        self.client_socket.send(name.encode('ascii'))

    def write(self):
        print("for connect to the server  enter 1 \n"
              "for disconnect to the server enter 2 \n"
              "for privet messenger to user enter 3 ,user name,your message \n"
              "for message to all users enter 4 ,your message\n"
              "for list of all users enter 5 \n"
              "fot list of file your can download enter 6 \n"
              "for send request to download file enter 7 , the name of file\n"
              "for download the file enter 8\n")
        receive_thread=None
        while True:
            action = input("enter command \n")
            x = action.split(",")
            while not x[0].isdigit():
                action = input("enter command \n")
                # Endless loop - missing assignment to x
                x = action.split(",")
            if int(x[0]) == 1 and self.connect is True:
                print("you already connect")

            if int(x[0]) == 1 and self.connect is False:
                name = self.name
                self.Start(name)
                receive_thread = threading.Thread(target=self.receive)
                receive_thread.start()
            else:
                if int(x[0]) == 7:
                    self.file_name = x[1]
                    message = action
                    self.client_socket.send(message.encode('ascii'))
                    continue

                if int(x[0]) == 8:
                    if self.file_name != None and self.file_name != "":
                        # print(f"client_socket: {self.client_socket.getsockname()}")
                        # print(f"peer socket: {self.client_socket.getpeername()}")
                        # self.client_socket_file.connect(self.client_socket.getsockname())
                        self.client_socket_file.bind(self.client_socket.getsockname())

                        download = threading.Thread(target=self.get_file, args=(self.file_name,))
                        download.start()
                        self.client_socket.send(x[0].encode('ascii'))
                        continue
                    else:
                        print("you didn't choose file to download")
                if int(x[0]) > 8 or int(x[0]) < 1:
                    print("err no such action , pls try again")
                if self.connect is False:
                    print("you need to connect ")
                if int(x[0]) == 2:
                    self.connect = False
                    message = action
                    self.client_socket.send(message.encode('ascii'))
                    self.client_socket.close()
                    # self.client_socket_file.close()
                else:
                    message = action
                    self.client_socket.send(message.encode('ascii'))


    def privat(self,message,user_name):
        message = "3," + user_name + message
        self.client_socket.send(message.encode('ascii'))

    def disconnect(self):
        self.client_socket.send("2".encode('ascii'))

    def client_list(self):
        self.client_socket.send("5".encode('ascii'))

    def files_list(self):
        self.client_socket.send("6".encode('ascii'))

    def broadcast(self,message):
        message = "4,"+message
        self.client_socket.send(message.encode('ascii'))

    def receive_broadcast_chat(self):
        message = self.client_socket.recv(4096).decode('ascii')
        total_message = message
        return total_message

    def get_file(self, filename):
        # self.send_filename(filename)
        self.client_socket_file.setblocking(0)
        start_time = time.time()
        timeout = 2
        expected = 0
        packets = []

        while True:
            # wait if you have no data
            if time.time() - start_time > timeout:
                print("got timeout. exiting download file loop")
                break
            # recieve something
            try:
                #print(f"about to receive packet {self.client_socket_file.getsockname()}")
                packet, address = self.client_socket_file.recvfrom(1024)
                #print("recieved packet")
                if packet:
                    num, data = self.extract(packet)

                    # Send acknlowedgement to the sender
                    if num == expected:
                        #print(f"sending ack on packet# {num}")
                        self.client_socket_file.sendto(str(expected).encode(), address)
                        #print(f"ack sent on packet# {num}")

                        expected += 1
                        packets.append((num, data))
                    else:
                        print(f"packet is not expected: {num}: {expected}")
                        print(f"sending to server: {expected-1}")
                        self.client_socket_file.sendto(str(expected - 1).encode(), address)

                    start_time = time.time()
                else:
                    time.sleep(0.01)

            except socket.error as err:
                pass

        if len(packets) == 0:
            print('Got no packets')
            return

        # sort packets, handle reordering
        sorted(packets, key=lambda x: x[0])

        packets = self.handle_duplicate(packets)
        last_pack = packets[len(packets) - 1]
        with open(filename, 'wb') as f:
            packet_data = last_pack[1]
            last_byte = packet_data[len(packet_data)-1]
            for p in packets:
                data = p[1]
                f.write(data)
        f.close()
        print(f"file downloaded: {filename} \n"
              f" the last byte is : {last_byte}")


    def handle_duplicate(self, packets):
        i = 0
        while i < len(packets) - 1:
            if packets[i][0] == packets[i + 1][0]:
                del packets[i + 1]
            else:
                i += 1
        return packets

    def make_packet(self, acknum, data=b''):
        ackbytes = acknum.to_bytes(4, byteorder='little', signed=True)
        return ackbytes + data

    def extract(self, packet):
        num = int.from_bytes(packet[0:4], byteorder='little', signed=True)
        return num, packet[4:]

    def receive(self):
        while True:
            try:
                message = self.client_socket.recv(1024)
                if len(message):
                    print(message.decode('ascii'))
                else:
                    # self.client_socket.close()
                    print("connection with server closed, exiting")
                    break
            except:
                print("Closed connection")
                break

if __name__ == '__main__':
    name = input("enter name")
    while name == "":
        name = input("enter name")
    c = client(host='127.0.0.1', port=50000, name=name)
    c.write()
