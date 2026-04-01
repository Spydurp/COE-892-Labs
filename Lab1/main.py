import requests
import threading
import hashlib
import random
import time

URL = 'http://127.0.0.1:8000/lab1/rover/'
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3
initial_x = 0
initial_y = 0

initial_dir = SOUTH
addons = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]

def checkRover(num: int):
    try:
        response = requests.get(URL + str(num))
        response.raise_for_status()
        return response.json()['commands']
    except requests.exceptions.RequestException as e:
        print("Error: " + str(e))


def run_hash(index: int, p, x, y, stop_event):
    global positions
    global serials
    global map_arr
    while not stop_event.is_set():
        pin = p
        for count in range(8):
            pin = pin + random.choice(addons)
        if stop_event.is_set():
            break
        temp_key = pin + serials[index]
        hashed = hashlib.sha256(temp_key.encode('utf-8')).hexdigest()
        zeroes = 0
        for ch in hashed:
            if ch == "0":
                zeroes += 1
            else:
                break
            if zeroes >= 6:
                del positions[index]
                del serials[index]
                map_arr[y][x] = 0
                stop_event.set()
                return True
# Takes x and y of current pos
# Reads mines.txt. If there is a mine at the given location, defuses the mine and returns true
# If there is no mine at the given location, returns false
# While one rover is defusing a mine, other rovers may not access that mine
def digMine(x: int, y: int, threads: int):
    i = 0

    for p in positions:
        if x == int(p.split(",")[0]) and y == int(p.split(",")[1]):
            # mine exists. defuse
            results = []
            stop_event = threading.Event()
            for count in range(threads):
                results.append(threading.Thread(target=run_hash, args=(i, p, x, y, stop_event)))
            for t in results:
                t.start()

            for t in results:
                t.join()
                return True

        i += 1
        return False


def draw_path(hash_threads: int):
    start_time = time.perf_counter()
    dir: int = initial_dir

    x = initial_x
    y = initial_y
    global map_arr

    out_arr = [['0'] * x_bound for r in range(y_bound)]
    cmdIndex = 0
    commands = ["L", "M", "D", "R", "M", "M", "R", "M", "D"]
    while len(positions) > 0:

        #cmd = checkRover(1)
        cmd = commands[cmdIndex]
        cmdIndex += 1

        dig = False
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
            if map_arr[y][x] == 1:
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
        elif cmd == 'D':
            print("Dig at " + str(x) + ", " + str(y))
            digMine(x, y, hash_threads)
        # check for mine, check for dig. If dig is false and mine is true, break.

        out_arr[y][x] = '*'
        if mine is True:
            print("Boom")
            break

    with open("path_" + str(1) + ".txt", "w") as out:
        for r in out_arr:
            for pos in r:
                out.write(pos)
            out.write('\n')
    end_time = time.perf_counter()
    return end_time-start_time

def start_rovers():
    global positions
    global serials
    global mutex
    global y_bound, x_bound
    with open("map.txt", "r") as map:
        y_bound, x_bound = map.readline().split(" ")
        y_bound = int(y_bound)
        x_bound = int(x_bound)
        for row in map.read().split("\n"):
            r = []
            for i in row.split(' '):
                r.append(int(i))
            map_arr.append(r)
    with open("mines.txt", "r") as mines:
        data = mines.read()
        positions = data.split("\n")[0].split(" ")
        serials = data.split("\n")[1:]
        for count in range(len(positions)):
            mutex.append(threading.Lock())
    r1 = threading.Thread(target=draw_path, args=(1,))
    r2 = threading.Thread(target=draw_path, args=(10,))
    start_time = time.perf_counter()
    r1.start()
    r1.join()
    end_time = time.perf_counter()
    sequential = end_time-start_time

    with open("map.txt", "r") as map:
        y_bound, x_bound = map.readline().split(" ")
        y_bound = int(y_bound)
        x_bound = int(x_bound)
        for row in map.read().split("\n"):
            r = []
            for i in row.split(' '):
                r.append(int(i))
            map_arr.append(r)
    with open("mines.txt", "r") as mines:
        data = mines.read()
        positions = data.split("\n")[0].split(" ")
        serials = data.split("\n")[1:]
        for count in range(len(positions)):
            mutex.append(threading.Lock())

    start_time = time.perf_counter()
    r2.start()
    r2.join()
    end_time = time.perf_counter()
    parallel = end_time-start_time
    print("Sequential: " + str(sequential))
    print("Parallel: " + str(parallel))


positions = []
serials = []
mines = []
mutex = []
map_arr = []
y_bound = 0
x_bound = 0

start_rovers()


