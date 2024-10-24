import subprocess

from fastapi import FastAPI, Request
from uvicorn import run
import multiprocessing
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse

from backend.numatoRelay import Relay
import time

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:4173",
    "tauri://localhost", # this fixed it! With this line, the Tauri app can now access the FastAPI server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# https://numato.com/docs/8-channel-usb-relay-module/
# OSX: ls /dev/*usb*

# Scan the system for serial ports
def get_serial_ports():
    ports: list[str | None] = []
    commands = ["ls /dev/ttyUSB*", "ls /dev/ttyACM*", "ls /dev/*usb*"]
    
    for cmd in commands:
        try:
            output = subprocess.check_output(cmd, shell=True, text=True)
            ports.extend(output.strip().split('\n'))
        except subprocess.CalledProcessError:
            # Ignore the error if no devices are found for the current pattern
            continue
    
    return ports

# switch = Relay('/dev/tty.usbmodem1301')



# Initialize the switch with one of the detected serial ports
serial_ports = get_serial_ports()
print("serial ports: ", serial_ports)
if serial_ports:
    switch = Relay(serial_ports[0])
else:
    switch = Relay(None) # debug mode


@app.get("/")
def hello():
    return "Hello, World!"


class Channel(BaseModel):
    number: int

class Sw(BaseModel):
    number: int


class Tree(BaseModel):
    R1: bool
    R2: bool
    R3: bool
    R4: bool
    R5: bool
    R6: bool
    R7: bool


tree_state = Tree(R1=False, R2=False, R3=False, R4=False, R5=False, R6=False, R7=False)


class T(BaseModel):
    tree_state: Tree

tree = T(tree_state=tree_state)



class Node:
    def __init__(self, relay_name: str):
        self.left: Node | None = None
        self.right: Node | None = None

        self.relay_name = relay_name
        self.relay_index = int(relay_name[1]) # R1 -> 1
        self.polarity = False # False/0 is right, True/1 is left

    def to_next(self):
        # process to whichever switch is 'pointed to' by this switch
        if self.polarity:
            return self.left
        else:
            return self.right
        

def flatten_tree(root: Node) -> Tree:
    state = {}
    queue = [root]
    
    while queue:
        current_node = queue.pop(0)
        if current_node:
            state[current_node.relay_name] = current_node.polarity
            queue.append(current_node.left)
            queue.append(current_node.right)
    
    return Tree(**state)
        

#           ___  R1 ____
#         /              \
#       R2                R3
#    /      \          /      \
#   R4       R5       R6       R7
#  /  \     /  \     /  \     /  \
# 7    6   5    4   3    2   1    0   # channel according to the relay board
# 8    7   6    5   4    3   2    1   # channel according to the user

nodes = [Node(f"R{i}") for i in range(1, 8)]
R1, R2, R3, R4, R5, R6, R7 = nodes

# set up the tree
R1.left = R2
R1.right = R3
R2.left = R4
R2.right = R5
R3.left = R6
R3.right = R7



def init_tree(): 

    if switch is None:
        print("No switch found, stopping.")
        return
    
    switch.turn_on(0)
    
    for node in nodes:
        time.sleep(0.03)
        node.polarity = False
        idx = int(node.relay_index)
        switch.send_pulse(idx, 12)

    switch.turn_off(0)

    tree.tree_state = flatten_tree(R1)



def channel_to_state(channel: int):
    """
    take in user-numbering channel (1-8)
    """

    if channel < 0 or channel > 7:
        print("Invalid channel number, stopping.")
        return

    # flip the channel numbering
    channel = 7 - channel

    if switch is None:
        print("No switch found, stopping.")
        return

    # switch from user to relay channel numbering
    # channel -= 1
    binary = bin(channel)[2:]
    # binary should be 3 digits long
    binary = binary.zfill(3)
    current_node = R1

    for bit in enumerate(binary):
        print(bit[1])

        if current_node is None:
            print("Reached a None node, stopping.")
            return
        
        time.sleep(0.05)
        if bit[1] == "0":
            # current_node = current_node.left

            # if current_node.polarity != True:
            # flip the relay
            current_node.polarity = True

            idx = int(current_node.relay_index)
            switch.turn_off(0)
            time.sleep(0.05)

            switch.send_pulse(idx,50)

            time.sleep(0.05)


        else:
            # if current_node.polarity != False:
            # flip the relay
            current_node.polarity = False

            idx = int(current_node.relay_index)
            switch.turn_on(0)
            time.sleep(0.05)

            switch.send_pulse(idx, 50)

            time.sleep(0.05)
            switch.turn_off(0)
            time.sleep(0.05)

        current_node = current_node.to_next()

    tree.tree_state = flatten_tree(R1)
    return tree.tree_state








@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("the request: ", request)
    return PlainTextResponse(str(exc), status_code=400)

@app.exception_handler(400)
async def bad_request_handler(request: Request, exc):

    print("detail: ", exc)
    return JSONResponse(
        status_code=400,
        content={"message": "Bad Request", "detail": str(exc)},
    )

@app.get("/reset")
def reset():
    init_tree()
    return tree.tree_state


@app.post("/channel")
def request_channel(channel: Channel):
    print("channel number: ", channel.number)
    return channel_to_state(channel.number)

@app.get("/tree")
def get_tree():
    # print("tree state: ", tree_state)
    return tree.tree_state


@app.post("/switch")
def toggle_switch(swp: Sw):

    if switch is None:
        print("No switch found, stopping.")
        return
    

    sw = nodes[swp.number-1]
    print("the switch to toggle: ", sw.relay_name)

    if sw.polarity == False:
        # flip the relay
        sw.polarity = True

        idx = int(sw.relay_index)
        switch.turn_off(0)
        time.sleep(0.05)
        switch.send_pulse(idx, 50)

    else:
        # flip the relay
        sw.polarity = False

        idx = int(sw.relay_index)
        switch.turn_on(0)
        time.sleep(0.05)
        switch.send_pulse(idx, 50)

    tree.tree_state = flatten_tree(R1)
    return tree.tree_state


init_tree()

if __name__ == "__main__":
    multiprocessing.freeze_support()  # For Windows support

    run(app, host="0.0.0.0", port=9050, reload=False, workers=1)

    # init_tree()
    # time.sleep(1)
    # channel_to_state(2)
