import requests
import random
import hashlib
import server
from threading import Lock

addons = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3
initial_x = 0
initial_y = 0
URL = 'http://127.0.0.1:8000/'

initial_dir = SOUTH

def run(map: list[int], y_bound: int, x_bound: int, rover: dict, mapLock: Lock, roverLock: Lock):
    print("Rover Started")
    dir: int = initial_dir

    x = rover["x"]
    y = rover["y"]

    out_arr = [['0'] * x_bound for r in range(y_bound)]
    out_arr[0][0] = '*'
    cmdIndex = 0
    commands = rover["commands"]
    while cmdIndex < len(commands):
        cmd = commands[cmdIndex]
        cmdIndex += 1

        mine = False

        if cmd == 'R':
            if dir+1 == 4:
                dir = 0
            else:
                dir += 1
        elif cmd == 'L':
            if dir-1 == -1:
                dir = 3
            else:
                dir -= 1
        elif cmd == 'M':
            if map[y][x] != 0:
                mine = True
            if dir == NORTH:
                if y-1 >= 0:
                    y -= 1
            if dir == EAST:
                if x+1 < x_bound:
                    x += 1
            if dir == SOUTH:
                if y+1 < y_bound:
                    y += 1
            if dir == WEST:
                if x-1 >= 0:
                    x -= 1
        # check for mine, check for dig. If dig is false and mine is true, break.
        elif cmd == 'D':
            print("Dig at " + str(x) + ", " + str(y))
            # get mine's serial number
            if map[y][x] != 0:
                try:
                    mineReq = requests.get(URL+f"mines/{map[y][x]}").json()
                except requests.exceptions.RequestException as e:
                    print("Error: " + str(e))
                if mineReq["Success"]:
                    if mineReq["mine"]["armed"]:
                        serial: str = mineReq["mine"]["Serial Number"]
                        pin = run_hash(serial)
                        body = server.updateMineReq(x=None, y=None, serial=None, armed=False, pin=pin)
                        # update mines at the server with pin
                        requests.put(URL + f"mines/{map[y][x]}", json=body.model_dump())
                
                # mine successfully disarmed
                with mapLock:
                    map[y][x] = 0

        

        out_arr[y][x] = '*'
        if mine is True:
            print("Boom")
            with roverLock:
                rover["status"] = "Eliminated"
                rover["x"] = x
                rover["y"] = y
            break
        with roverLock:
            rover["x"] = x
            rover["y"] = y

    with open("path_" + str(rover["id"]) + ".txt", "w") as out:
        for r in out_arr:
            for pos in r:
                out.write(pos)
            out.write('\n')
    
    if rover["status"] != "Eliminated":
        with roverLock:
            rover["status"] = "Finished"
            rover["x"] = x
            rover["y"] = y

    

def run_hash(serial: str):
    while True:
        pin = "XYZ"
        for count in range(8):
            pin = pin + random.choice(addons)
        temp_key = pin + serial
        hashed = hashlib.sha256(temp_key.encode('utf-8')).hexdigest()
        zeroes = 0
        for ch in hashed:
            if ch == "0":
                zeroes += 1
            else:
                break
            if zeroes >= 6:
                return pin