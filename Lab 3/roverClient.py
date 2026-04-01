import grpc
import groundControl_pb2
import groundControl_pb2_grpc
import pika
import sys

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3
initial_x = 0
initial_y = 0

initial_dir = SOUTH
addons = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]


def run(roverID: int, mapID: str):
    channel = grpc.insecure_channel("localhost:50051")
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    demine_channel = connection.channel()
    demine_channel.queue_declare(queue='Demine-Queue')
    stub = groundControl_pb2_grpc.ground_controlStub(channel)

    # get map
    map_response = stub.getMap(groundControl_pb2.mapRequest(id=str(mapID)))
    y_bound, x_bound = map_response.bounds.split(" ")
    y_bound = int(y_bound)
    x_bound = int(x_bound)
    map_arr = []
    mines = 0
    for row in map_response.map.split("\n"):
        r = []
        for i in row.split(' '):
            r.append(int(i))
            if int(i) != 0:
                mines += 1
        map_arr.append(r)

    dir: int = initial_dir

    x = initial_x
    y = initial_y

    out_arr = [['0'] * x_bound for r in range(y_bound)]
    cmdIndex = 0
    commands = ["L", "M", "D", "R", "M", "M", "R", "M", "D"]
    while mines > 0:

        #cmd = stub.getCommands(groundControl_pb2.cmdReq(size=1)).commands
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
        # check for mine, check for dig. If dig is false and mine is true, break.
        elif cmd == 'D':
            print("Dig at " + str(x) + ", " + str(y))
            # get mine's serial number
            if map_arr[y][x] != 0:
                serial = stub.getSerial(groundControl_pb2.serialRequest(posX=x, posY=y, id=mapID)).mineSerial
                print(serial)
                # publish serial number, roverID, and mine coordinates to Demine-Queue channel
                demine_channel.basic_publish(exchange="", routing_key='Demine-Queue', body=str(roverID) + "," + serial + "," + str(x) + "," + str(y))
                # mine successfully disarmed
                map_arr[y][x] = 0
                mines -= 1

        

        out_arr[y][x] = '*'
        if mine is True:
            print("Boom")
            break

    with open("path_" + str(1) + ".txt", "w") as out:
        for r in out_arr:
            for pos in r:
                out.write(pos)
            out.write('\n')

    if mines == 0:
        print("All mines defused")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Proper usage: python roverClient.py [mapID] [roverID]")
    elif len(sys.argv) == 3:
        run(sys.argv[1], int(sys.argv[2]))
