import requests
import threading
import time

URL = 'http://127.0.0.1:8000/lab1/rover/'
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3
initial_x = 0
initial_y = 0

initial_dir = SOUTH


def checkRover(num: int):
    try:
        response = requests.get(URL + str(num))
        response.raise_for_status()
        return response.json()['commands']
    except requests.exceptions.RequestException as e:
        print("Error: " + str(e))


def draw_path(rover: int, mutex):
    start_time = time.perf_counter()

    map_arr = []
    with mutex:
        with open("map.txt", "r") as map:
            y_bound, x_bound = map.readline().split(" ")
            y_bound = int(y_bound)
            x_bound = int(x_bound)
            for row in map.read().split("\n"):
                r = []
                for i in row.split(' '):
                    r.append(int(i))
                map_arr.append(r)

    dir: int = initial_dir

    x = initial_x
    y = initial_y

    num_mines = 2

    out_arr = [['0'] * x_bound for r in range(y_bound)]
    #cmdIndex = 0
    #commands = ["L", "M", "D", "R", "M", "M", "R", "M", "D"]
    while num_mines > 0:

        cmd = checkRover(1)
        #cmd = commands[cmdIndex]
        #cmdIndex += 1

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
            if map_arr[y][x] == 1:
                num_mines -= 1
                map_arr[y][x] = 0

        # check for mine, check for dig. If dig is false and mine is true, break.

        out_arr[y][x] = '*'
        if mine is True:
            print("Rover " + str(rover) + ": Boom")
            break
    if num_mines == 0:
        print("Rover " + str(rover) + ": Complete")
    with open("path_" + str(rover) + ".txt", "w") as out:
        for r in out_arr:
            for pos in r:
                out.write(pos)
            out.write('\n')
    end_time = time.perf_counter()
    return end_time-start_time

def start_rovers(num: int):
    mutex = threading.Lock()
    rovers = []
    for i in range(num):
        rovers.append(threading.Thread(target=draw_path, args=(i, mutex)))

    start_time = time.perf_counter()
    for r in rovers:
        r.start()
    for r in rovers:
        r.join()
    end_time = time.perf_counter()
    print("Total time: " + str(end_time-start_time))
    return end_time-start_time




parallel = start_rovers(10)
start = time.perf_counter()
for counter in range(10):
    draw_path(counter, mutex=threading.Lock())
end = time.perf_counter()

sequential = end-start
print("Sequential: " + str(sequential))
print("Parallel: " + str(parallel))