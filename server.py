#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
import os
import socket
import threading
import time
from threading import Thread
from pathlib import Path
import QuicFunc
from QuicFunc import *

global flag_file
global file1
global client_addresses
client_addresses = set()

total_time=0
total_send=0
total_speed=0


def stat(start_time,end_time,filename):
    global total_time,total_send,total_speed
    elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
    file_size = os.path.getsize(filename)
    speed = file_size / (elapsed_time / 1000)  # Convert elapsed time back to seconds for speed calculation
    total_time += elapsed_time
    total_send += 1
    total_speed += speed
    print("______________________STATISTICS______________________")
    print("______________________FOR THE CURRENT FILE______________________")
    print(f"Time taken to receive file: {elapsed_time:.2f} ms")
    print(f"Speed of file transfer: {speed:.2f} bytes/second")
    print("______________________AVERAGE______________________")
    print(f"average time :{total_time / total_send} ms")
    print(f"average speed :{total_speed / total_send} bytes/second")


"""
    handles two options for the client, 
    first option is to receiver a text message, usually a small one(about couple of kbs)
    Second option is to send a text file, bigger than the text, up to 10 mb's as required in the assigment;
    we parse the input to get the name of the file, and then we get the rest of the file in recv_file

"""
def handle_client(client_address, name):  # Takes client data and address as argument.
    """Handles a single client connection."""
    global total_time,total_send,total_speed
    try:
        while True:
            data, _ = server_socket.recvfrom(BUFSIZ)
            new_package = QuicFunc.recreate_package(data)
            msg = new_package.payload
            # print(msg)
            if msg[:4] == "TEXT":
                print("enterd text")
                broadcast_text(new_package, name + ": ")
                print("sending done")
            elif msg[:4] == "FILE":
                flag_file = True
                print("enterd file: " + msg[4:])
                receivedname = msg[4:]
                filename = str(Path.cwd()) + r'//(2)' + receivedname
                with open(filename,"w") as file:
                    recv_file(file,filename)
                    print("done file")
    except OSError:
        pass  # Client disconnected or encountered an error

"""
    Called by handle_client function
    this func uses QuicFunc.recv_pacakge_list_from file 
    and then redirect the list to write to file, which recreated the file that had been sent from the user (client)
"""
def recv_file(file1,filename):
    start_time=time.time()
    package_list = QuicFunc.recv_package_list_from_file(server_socket)
    write_to_file(package_list, file1)
    end_time=time.time()
    stat(start_time,end_time,filename)
    print("exit file")

"""
    broadcast the text msgs to the client (using our gui)
"""
def broadcast_text(text_package: QuicPackage, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    print(text_package.payload)
    text_package.payload = text_package.payload[:4] + prefix + text_package.payload[4:]
    for addr in client_addresses:
        print(client_address)
        QuicFunc.send_package(text_package, server_socket, addr)
    print("done broadcast")
"""
    broadcast file to all users.
"""

def broadcast_file(msg, prefix=""):
    path, s = os.path.split(msg)
    s = s[3:]
    for addr in client_addresses:
        server_socket.sendto(s, addr)
        file1 = open(msg, 'rb')
        slice = file1.read(128)
        while slice:
            server_socket.sendto(slice, addr)
            slice = file1.read(128)

"""
    handles a new connection a broadcasts his name,
    it's like a new user to the system the client assigns his name
    and after this, he can send texts and everyone will know it's him
"""
def new_connection(data, client_address):
    print("thread")
    client_addresses.add(client_address)
    new_package = QuicFunc.recreate_package(data)
    name = new_package.payload[4:]
    welcome = f'&TEXTWelcome %s! If you ever want to quit, you can just stop typing. The Connection ID is {CONNECTION_ID}' % name
    welcome_package = QuicPackage(0, welcome,CONNECTION_ID)
    QuicFunc.send_package(welcome_package, server_socket, client_address)
    msg = "TEXT%s has joined the chat!" % name
    new_package = QuicPackage(0, msg,CONNECTION_ID) #start the connection
    print(welcome)
    broadcast_text(new_package)
    client_thread = Thread(target=handle_client, args=(client_address, name))
    client_thread.start()


"""
    checks for conenction, and sends back the connection id in which they will use. 
"""
def handshake(new_pack,address):
    if new_pack.payload == "hello":
        CONNECTION_ID = new_pack.connection_id
        print("The connection ID is: " + CONNECTION_ID)
        QuicFunc.send_package(new_pack, server_socket, address)
        return True
    return False

def wait_for_connection():
    global CONNECTION_ID
    start = time.time()
    timeout = 1  # Timeout for retransmission
    while True:
        try:
            server_socket.settimeout(timeout)
            pack, address = server_socket.recvfrom(BUFSIZ)
            new_pack = QuicFunc.recreate_package(pack)

            if handshake(new_pack, address):  # if we found the user we can stop waiting for him
                break

        except socket.timeout:
            if time.time() - start > timeout:
                print("Didn't receive pack in time, waiting again...")
                start = time.time()  # Reset the start time for the next timeout

        except Exception as e:
            print(f"An error occurred: {e}")

"""
    definitions for the soecket and the connetion
"""
HOST = '127.0.0.1'
PORT = 33002
BUFSIZ = 1024
ADDR = (HOST, PORT)
CONNECTION_ID=0


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(ADDR)

if __name__ == "__main__":
    print("Waiting for connection...")
    flag_file = False
    # while True: #don't know if it's good or not
    time.sleep(5)
    wait_for_connection()
    server_socket.settimeout(None)
    data, client_address = server_socket.recvfrom(BUFSIZ)
    if client_address not in client_addresses:
        print("new connection, list: " + str(client_addresses))
        new_connection(data, client_address)
    else:
        if not flag_file:
            print("why?")
            print(threading.current_thread())
            # handle_client(client_address, "name")
        else:
            print("main")
            print(file1)
            # get_file(data, file1)
