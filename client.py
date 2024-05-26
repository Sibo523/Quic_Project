"""Client for the UDP-based chat application."""
import socket
import time
from threading import Thread
from tkinter import *
from tkinter import filedialog

import QuicFunc
from QuicFunc import *
"""
    defenition for the Algorithms of resending, intended to corespond with QuicFunc
"""
packages_list = {}
no_acks = []
ack_list = []
seq_threshold = 3
time_threshold = 0.002
Running = True
firstclick = True


"""
    checks if we should resend depends on the mode
"""


def valid_mode(mode):
    global no_acks
    global time_threshold

    match mode:
        case 1:  # time
            return time.time() - no_acks[0].sent_time > time_threshold

        case 2:  #seq
            return list(packages_list.values())[-1].seq - no_acks[0].seq > seq_threshold

        case 3:  #both
            return list(packages_list.values())[-1].seq - no_acks[0].seq > seq_threshold and time.time() - no_acks[0].sent_time > time_threshold


"""
    3 modes to determine if a packet is lost if so it adds to the no_acks list 
    The mode is given by the user
"""

"""
    Algorithm to send by seq number.
"""
def send_by_seq(ack_seq):
    global ack_list,no_acks,packages_list

    if ack_seq > ack_list[-2] + 1:
        for i in range(ack_list[-2] + 1, ack_seq):
            no_acks.append(packages_list[i])
"""
    Algorithm to resend by time.
"""
def send_by_time(ack_seq):
    global ack_list,no_acks,packages_list,time_threshold,send_sleep

    if packages_list[ack_seq].sent_time > packages_list[ack_list[-2]].sent_time:
        index_start = int((send_sleep * 3) / time_threshold) #how many packets from the last should we check
        if (index_start > len(ack_list)):  # if we are just starting we will reach index out of bounds
            pass
        else:
            for i in range(ack_list[-index_start] + 1, ack_seq):
                if i in ack_list:
                    continue
                no_acks.append(packages_list[i])
"""
    uses both algorithm to know better when we should resend a package without acknowledgement
"""
def send_by_both(ack_seq):
    global ack_list, no_acks, packages_list, time_threshold, send_sleep
    if ack_seq > ack_list[-2] + 1 and packages_list[ack_seq].sent_time > packages_list[ack_list[-2]].sent_time:
        if ack_seq > ack_list[-2] + 1: #the send_by_
            for i in range(ack_list[-2] + 1, ack_seq):
                no_acks.append(packages_list[i])

"""
    3 modes to choose the mode in which we are going to use
    The mode is given by the user
    the mode we have will have a different algorithm to determine a packet as lost or not.
"""
def append_noack(mode, ack_seq):
    global no_acks
    global time_threshold
    global send_sleep

    match mode:
        case 1:  # time
            send_by_time(ack_seq)
        case 2:  #seq
            send_by_seq(ack_seq)
        case 3:  #both
            send_by_both(ack_seq)


"""
    resending using the mode we got from the user
    also uses resend_lost_packages (which is in QuicFunc.py)
"""

def resending_algo(package_list, no_acks, client_sockt, ADDR, mode):
    if len(packages_list) > 0 and len(no_acks) > 0:
        if valid_mode(mode):
            print("resend")
            resend_lost_packages(packages_list, no_acks, client_socket, SERVER_ADDR)
            no_acks.remove(no_acks[0])


"""
    check if the packet is ACK
"""


def acked(data):
    return data[:3] == "ACK".encode('utf-8')


def almost_exec(ack_seq):  #almost someone who got acked sent again
    for index, packet in enumerate(no_acks):  # we check if it's in the acks and remove it
        if not compare(packages_list[ack_seq], packet):
            no_acks.remove(packet)


"""
    Functions that manages the sent packets and resends if needed 
    using functions:
        acked - checks if the packet that we got is a ACK packet
        almost_exec - checks if the packet is in the no_ack list if so removes it
        resending_algo - depending on the mode it chooses the algo to use
        append_noAck - depending on the mode, main reason to colerate with the resending_algo
        valid_mode - depending on the mode does it's check 
"""
def receive():
    """Handles receiving of messages."""
    global Running  #needed for hand of connection curretly doesn't work #tchelet
    global packages_list  #dictionary contains all the packets we sent so far
    global no_acks  # is list for the packets we need to resend sometimes we removre elements from it if we got a ack for them :)
    global flag_send  #don't know #tchelet
    global ack_list  #list of all seq's we got so far

    while Running:  #when we need to keep running the thread we switch this off

        try:  #tchelet why do we try

            resending_algo(packages_list, no_acks, client_socket, SERVER_ADDR, mode)  #checks there's packets to resend and resends
            data, n = client_socket.recvfrom(BUFSIZ)

            if acked(data):  #if we got ack for someone we check if we missed someone :(
                print(data.decode("utf-8"))
                ack_seq = int(data[5:])

                try:
                    packages_list[ack_seq].recvack()
                    ack_list.append(ack_seq)
                    almost_exec(ack_seq)
                    append_noack(mode, ack_seq)

                except(KeyError):
                    print("KeyError: " + str(data[5:]))
                    ack_list.append(int(data[5:]))

            else:  #don't know #tchelet
                recv_package = recreate_package(data)
                msg = recv_package.payload[4:]
                msg_list.insert(END, msg)  # Insert the received message into the message list
        except OSError as e:  # Possibly server has left the chat.
            pass

"""
    send basic msg between the client to the server.
"""
def send(event=None):
    """Handles sending of messages."""
    msg = "TEXT" + my_msg.get()
    my_msg.set("")  # Clears input field.
    new_package = QuicPackage(0, str(msg),CONNECTION_ID)
    QuicFunc.send_package(new_package, client_socket, SERVER_ADDR)

    print(SERVER_ADDR)
    if msg == "{quit}":
        client_socket.close()
        root.quit()

"""
    send attachment, it lets you select in the gui the file in the father directory as a default
    after it, it usess the func send_packages_from_file 
    which create small packages and sends to the server 
"""

def sendattach():
    """Handles sending of files (attachments)."""
    global ack_list
    global no_acks

    filename = filedialog.askopenfilename(initialdir="/home/sibo/Desktop/lemuyr/text_send.txt", title="Select A File",
                                          filetypes=(("jpeg files", "*.txt"),
                                                     ("all files", "*.*")))  #short cut for now we need to delete
    if (filename == ""):  #if we got nothing then we can't send natting
        client_socket.close()
        root.quit()
        return
    #parsing the input
    s = filename.split("/")

    with open(filename, "rb") as file1:
        entry = "FILE" + str(s[-1])
        entry_package = QuicPackage(0, entry,CONNECTION_ID)
        ack_list.append(entry_package.seq)
        QuicFunc.send_package(entry_package, client_socket, SERVER_ADDR)
        QuicFunc.send_packages_from_file(file1, client_socket, SERVER_ADDR, packages_list, no_acks,CONNECTION_ID)




def on_entry_click(event):
    """function that gets called whenever entry1 is clicked"""
    global firstclick
    if firstclick:  # if this is the first time they clicked it
        firstclick = False
        entry_field.delete(0, "end")  # delete all the text in the entry

"""
    These functions are for the closing of the gui.
"""
def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    send()
def sendquit():
    global Running
    on_closing()
    root.destroy()
    Running = False

"""
    This represend the handshake between the client and the server, the client sends packet which the payload is hello
    meaning it's the start of the connection. It waits for an Ack from the server, meaning it's got the first ack and 
    we can start sending msgs and files
    if the packet is lost, it will send again to the server.
"""
def send_first_ack():
    print("Send first")
    pack = QuicPackage(0, "hello", CONNECTION_ID)
    QuicFunc.send_package(pack, client_socket, SERVER_ADDR)
    wait_for_ack()


def wait_for_ack():
    print("Enter ack")
    start = time.time()
    timeout = 1  # Timeout for retransmission
    while True:
        try:
            client_socket.settimeout(timeout)
            data, n = client_socket.recvfrom(BUFSIZ)
            new_pack = QuicFunc.recreate_package(data)

            if new_pack.payload == "hello":
                print("Connection is good")
                return

        except socket.timeout:
            if time.time() - start > timeout:
                print("Didn't receive ack in time, resending...")
                send_first_ack()
                return

        except Exception as e:
            print(f"An error occurred: {e}")


"""
    Definitions for the Gui used
"""

root = Tk()
root.title("ChatIO")
root.geometry('500x500')

messages_frame = Frame(root)
my_msg = StringVar()  # For the messages to be sent.
my_msg.set("Type your messages here.")
yscrollbar = Scrollbar(messages_frame)  # To navigate through past messages.
xscrollbar = Scrollbar(messages_frame, orient=HORIZONTAL)  # To navigate through long messages.
# Following will contain the messages.
msg_list = Listbox(messages_frame, height=20, width=50, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
yscrollbar.pack(side=RIGHT, fill=Y)
xscrollbar.pack(side=BOTTOM, fill=X)
msg_list.pack(side=LEFT, fill=BOTH)
messages_frame.pack()
yscrollbar.config(command=msg_list.yview)
xscrollbar.config(command=msg_list.xview)

entry_field = Entry(root, width=42, textvariable=my_msg)
entry_field.bind('<FocusIn>', on_entry_click)
entry_field.bind("<Return>", send)
entry_field.place(x=15, y=344)
send_button = Button(root, text="Send", command=send)
send_button.place(x=280, y=340)
send_attach = Button(root, text="Send Attachment", command=sendattach)
send_attach.place(x=50, y=375)
send_button = Button(root, text="Quit Chat", command=sendquit)
send_button.place(x=175, y=375)

root.protocol("WM_DELETE_WINDOW", on_closing)

"""
    Definitions for the socket in which the client and the server will conmminucate.
"""
#----Socket code----
HOST = "127.0.0.1"
PORT = 33002
BUFSIZ = 1024
SERVER_ADDR = (HOST, PORT)
"""
    Choose the mode in which we are going to resend the packetd 
    there are 3 modes
    1. time based
    2. seq based
    3. time And seq based
"""
CONNECTION_ID=int(input("Enter the connection id\n"))
mode = int(input("Enter the mode of packet loss between 1-3\n"))
while mode not in [1,2,3]:
    mode=int(input("mode between 1-3\n"))


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send_first_ack()

receive_thread = Thread(target=receive)
receive_thread.start()
root.mainloop()
