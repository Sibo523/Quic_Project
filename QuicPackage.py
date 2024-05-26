import socket  #import the socket library, using for sending packets and create a connection
import time  #import the time library to get the time of the packet creation, for timeouts and more


class QuicPackage:  # class for Packet in Quic Protocol
    sequence = 0  # static vaiable just to keep every new packet uniq ever resended pack helps for the resend algo

    def __init__(self, pos, payload, con):  # intialize of Quic packet with multiple fields
        QuicPackage.sequence += 1  # static variable to keep track of every packet sequence number and
        # for different packets to have different sequence number according to their order creation
        self.seq = QuicPackage.sequence  # intialize each packet uniq sequence number
        self.__pos = pos  # each packet has its position according to its order of sending
        self.sent_time = time.time()  # each packet time of creation
        self.payload = payload  # each packet content
        self.connection_id = con  # the connection id between the server and the client
        self.ackrecv = False  # to check if a packet has received in the server

    # function to print the packet with its variables
    def __str__(self):
        return "sequence: " + str(self.seq) + ", pos: " + str(self.__pos) + " sent time: " + str(
            self.sent_time) + "ACK: " + str(self.ackrecv) + "connection id" + str(self.connection_id)

    # function to receive each packet position
    def getpos(self):
        return self.__pos

    # function to receive each packet sequence number
    def getSeq(self):
        return self.seq

    ##################################################SERVER-FUNCTIONS######################################################

    # function for packets that arrived in the server(ack received)
    def recvack(self):
        self.ackrecv = True

    # function to send and print ack from the server side
    def send_ack(self, sock: socket, ADDR):
        sock.sendto(bytes("ACK: " + str(self.seq), 'utf-8'), ADDR)
        print("ACK " + str(self.seq) + " sent!")

    #######################################################CLIENT-FUNCTIONS##################################################

    # function that update the creation time and sequence number for a new packet
    def recreate_from_str(self, sent_time, seq):
        self.sent_time = sent_time
        self.seq = seq

    # funtion that updates a new packet for sending new packet
    # (because of packet loss, we need to send packets again and update their time creation and their sequence number)
    def update_for_resend(self):
        self.sent_time = time.time()
        QuicPackage.sequence += 1
        print("new sequence: " + str(QuicPackage.sequence))
        self.seq = QuicPackage.sequence

    # encode and send the packet
    def encode_package(self):
        if not self.payload:  # if the packet doesn't have payload we don't need to encode it
            return {}
        if type(self.payload) == bytes:  # if the payload is already in bytes we need to decode it first
                                         # (we want to encode every thing together)
            self.payload = self.payload.decode("utf-8")
        encoded = str(self.seq) + "&" + str(self.__pos) + "&" + str(self.sent_time) + "&" + str(
            self.payload) + "&" + str(self.connection_id)
        en = encoded.encode("utf-8") # encode the packet
        return en # send the encoded packet
