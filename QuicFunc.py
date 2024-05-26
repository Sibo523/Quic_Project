from QuicPackage import *  # import the QuicPackage file for creating packets and using its functions
import socket  # import the socket library for creating a socket and sending packets
from functools import cmp_to_key  #tchelet
import re  #tchelet
import time  # import the time library to get the time of the packet creation, for timeouts and more

send_sleep = 0.002  # if we want faster result but a greater chance to loss packet than we can do 0.0002
                    #depends on the packet loss %


# function for recreating packets, we get encoded packet and we decode it, each variable acording to its kind
def recreate_package(str_package: bytes):
    list_package = str_package.decode("utf-8").split("&", 4)  # the packet encoded using & between each field
    new_package = QuicPackage(int(list_package[1]), list_package[3], list_package[4])  # create the new packet
    new_package.recreate_from_str(float(list_package[2]),
                                  list_package[0])  # setting the time anf sequence number fot the packet
    return new_package  # return the new packet


# function for sending the packet using the "sendto" function from the socket library
def send_package(package: QuicPackage, sock: socket, ADDR):  # event is passed by binders.
    """Handles sending of messages."""
    sock.sendto(package.encode_package(), ADDR)


# function to read information from the file, store it in packet objects and sending the packets
def send_packages_from_file(file1, sock: socket, ADDR, package_list, no_ack, connect):
    """Handles sending of files (attachments)."""
    global send_sleep
    pos = 0
    print("Sending file...")

    while True:  # while we can still read from the file
        slice = file1.read(268)  # read 268 bytes from the file
        # print("hello\n",slice)
        if not slice:  # if we are done reading from the file
            time.sleep(0.5)  # wait for 0.5 seconds
            send_last(sock, ADDR,connect,pos)
            return package_list  # return all the packets we sent from the file

        time.sleep(send_sleep)  # wait
        new_package = QuicPackage(pos, slice, connect)  # create the new packet
        package_list[new_package.seq] = new_package  # add the new packet to the list
        send_package(new_package, sock, ADDR)  # send the packet
        pos += 1  # increase the position of the packets by one

def send_last(sock, ADDR,connect,pos):
    for i in range(1, 100):
        new_package = QuicPackage(pos, "DONE", connect)
        # package_list[new_package.seq] = new_package
        send_package(new_package, sock, ADDR)


# function to receive the packets from the client
def recv_package_list_from_file(sock: socket):
    package_list = []  # initialize a list of packets
    while True:  # while we get packets
        package, addr = sock.recvfrom(1024)  # receive the packets
        if not package:  # if the packet we received is None, there are no longer packets to receive
            print("done recv")
            return package_list  # return the list of packets
        new_package = recreate_package(package)  # decode the received packet
        if new_package.payload == "DONE":  # if its the last one
            print("done recv")
            return package_list
        print("ack for ", new_package.getpos())  # send ack for receiving packets
        new_package.send_ack(sock, addr)  # send ack
        package_list.append(new_package)  # add the new packet to the list


# function to compare packets by position
def compare(x, y):
    return x.getpos() - y.getpos() # return True if the x packet is bigger that the y packet by its position


# function to remove duplicates packets, we know its duplicate by position
def remove_duplicates(list):
    seen_x = set()
    unique_packets = []

    for pac in list:
        if pac.getpos() not in seen_x:
            unique_packets.append(pac)
            seen_x.add(pac.getpos())

    return unique_packets


# function to write the packets received from the file sent by the client into a new file
def write_to_file(package_list: [], file1):
    unique_sorted_package_list = remove_duplicates(package_list) # remove duplicated packets
    package_list = sorted(unique_sorted_package_list, key=cmp_to_key(compare)) # sort the packets by position

    f = open("packetPos.txt", "w") # open the packetPos file to write their the packets position
    for payload in package_list:
        f.write(str(payload.getpos()) + "\n")  #print packet pos
        # f.write("\n")
        file1.write(payload.payload)  #print the packet itself
    f.close()


# function to resend lost packets
def resend_lost_packages(package_list, no_ack, sock, ADDR):
    # time.sleep(send_sleep)
    print("resend lost package")
    pack = no_ack[0] # send the first packet in the no_acks list, its the first packet that need to resend
    print("I lost this :", pack.seq, "and this is the pos somehow", pack.getpos())
    pack.update_for_resend() # update the packet for resend
    send_package(pack, sock, ADDR) # send the packet again
    package_list[pack.seq] = pack # add the packet to the list of sending packets
