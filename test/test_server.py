from unittest import TestCase

from clinet.client import client
from server.server import Server


class TestServer(TestCase):

    def setUp(self) -> None:
        self.My_server = Server(port=50000, ip='127.0.0.1')
        self.c1 = client(host='127.0.0.1', port=50000, name="shay")
        self.c2 = client(host='127.0.0.1', port=50000, name="noam")
        self.c3 = client(host='127.0.0.1', port=50000, name="dani")

    def test_run__server(self):
        # Run a server connect 2 client and check the broadcast of online/offline new users
        self.c1.Start(self.c1.name)
        self.assertEqual(self.c1.receive_broadcast_chat(), "shay is now online ! \n ")
        self.assertEqual(self.c1.receive_broadcast_chat(), "connected to the server ")
        self.c2.Start(self.c2.name)
        self.assertEqual(self.c1.receive_broadcast_chat(), "noam is now online ! \n ")
        self.assertEqual(self.c2.receive_broadcast_chat(), "noam is now online ! \n ")
        self.assertEqual(self.c2.receive_broadcast_chat(), "connected to the server ")
        self.c1.disconnect()
        self.assertEqual(self.c2.receive_broadcast_chat(), "shay left")
        self.c1.Start(self.c1.name)
        self.assertEqual(self.c1.receive_broadcast_chat(), "shay is now online ! \n ")
        self.assertEqual(self.c2.receive_broadcast_chat(), "shay is now online ! \n ")


    def test_broadcast(self):
        self.c1.Start(self.c1.name)
        self.assertEqual(self.c1.receive_broadcast_chat(), "shay is now online ! \n ")
        self.assertEqual(self.c1.receive_broadcast_chat(), "connected to the server ")
        self.c2.Start(self.c2.name)
        self.assertEqual(self.c1.receive_broadcast_chat(), "noam is now online ! \n ")
        self.assertEqual(self.c2.receive_broadcast_chat(), "noam is now online ! \n ")
        self.assertEqual(self.c2.receive_broadcast_chat(), "connected to the server ")
        self.c1.broadcast("hey")
        self.assertEqual(self.c1.receive_broadcast_chat(), "shay:hey")
        self.assertEqual(self.c2.receive_broadcast_chat(), "shay:hey")

    def test_list_users(self):
        self.c1.Start(self.c1.name)
        self.assertEqual(self.c1.receive_broadcast_chat(), "shay is now online ! \n ")
        self.assertEqual(self.c1.receive_broadcast_chat(), "connected to the server ")
        self.c2.Start(self.c2.name)
        self.assertEqual(self.c1.receive_broadcast_chat(), "noam is now online ! \n ")
        self.assertEqual(self.c2.receive_broadcast_chat(), "noam is now online ! \n ")
        self.assertEqual(self.c2.receive_broadcast_chat(), "connected to the server ")
        self.c1.client_list()
        self.assertEqual(self.c1.receive_broadcast_chat() ,"-----The online users are------\nshay , noam , ")
        self.c2.client_list()
        self.assertEqual(self.c2.receive_broadcast_chat(), "-----The online users are------\nshay , noam , ")


    def test_list_files(self):
        self.c1.Start(self.c1.name)
        self.assertEqual(self.c1.receive_broadcast_chat(), "shay is now online ! \n ")
        self.assertEqual(self.c1.receive_broadcast_chat(), "connected to the server ")
        self.c1.files_list()
        self.assertEqual(self.c1.receive_broadcast_chat(), "-----The files are------\ncat.jpg , dog.jpg , list.txt")
        self.c2.Start(self.c2.name)
        self.assertEqual(self.c2.receive_broadcast_chat(), "noam is now online ! \n ")
        self.assertEqual(self.c2.receive_broadcast_chat(), "connected to the server ")
        self.c2.files_list()
        self.assertEqual(self.c2.receive_broadcast_chat(), "-----The files are------\ncat.jpg , dog.jpg , list.txt")



    def test_privat_message(self):
        self.c1.Start(self.c1.name)
        self.assertEqual(self.c1.receive_broadcast_chat(), "shay is now online ! \n ")
        self.assertEqual(self.c1.receive_broadcast_chat(), "connected to the server ")
        self.c2.Start(self.c2.name)
        self.assertEqual(self.c1.receive_broadcast_chat(), "noam is now online ! \n ")
        self.assertEqual(self.c2.receive_broadcast_chat(), "noam is now online ! \n ")
        self.assertEqual(self.c2.receive_broadcast_chat(), "connected to the server ")
        self.c1.privat(",hey noam","shay")
        self.assertEqual(self.c2.receive_broadcast_chat(), "privat message from:shay:hey noam")



