import grpc
import groundControl_pb2
import groundControl_pb2_grpc
import requests
import concurrent.futures as futures
import logging
import hashlib

URL = 'http://127.0.0.1:8000/lab1/rover/'
def cmd(num: int):
    try:
        response = requests.get(URL + str(num))
        response.raise_for_status()
        return response.json()['commands']
    except requests.exceptions.RequestException as e:
        print("Error: " + str(e))

def valid_pin(serial, pin):
    key = serial + pin
    hashed = hashlib.sha256(key.encode()).hexdigest()

    return hashed.startswith("000000")

class groundControl(groundControl_pb2_grpc.ground_controlServicer):
    def getMap(self, request, context):
        mapID = request.id
        filename = "map" + str(mapID) + ".txt"
        output = ""
        bounds = ""
        with open(filename, "r") as mapFile:
            bounds = mapFile.readline()
            output = mapFile.read()
        
        return groundControl_pb2.mapReply(map=output, bounds=bounds)

    def getCommands(self, request, context):
        return groundControl_pb2.cmdReply(commands=cmd(request.size))

    def getSerial(self, request, context):
        filename = "mines" + str(request.id) + ".txt"
        contents = ""
        with open(filename, "r") as minesFile:
            contents = minesFile.read()
        contents = contents.split("\n")
        positions = contents[0].split(" ")
        count = 0
        for i in positions:
            if i == str(request.posX) + "," + str(request.posY):
                break
            count += 1
        return groundControl_pb2.serialReply(mineSerial=contents[count+1])
        
    def reportStatus(self, request, context):
        if request.success == True:
            print("Rover " + str(request.id) + " finished defusing all mines")
        else:
            print("Rover " + str(request.id) + " exploded")
        return groundControl_pb2.statusAck(ack=True)
    
    def sharePin(self, request, context):
        roverID = request.id
        pin = request.pinVal
        serial = request.serial
        print("Rover" + str(roverID) + " submitted PIN " + str(pin) + " for serial " + str(serial))
        if valid_pin(serial, pin):
            print("Mine " + serial + " disarmed by rover " + roverID)
            return groundControl_pb2.pinAck(success=True)
        return groundControl_pb2.pinAck(success=False)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    groundControl_pb2_grpc.add_ground_controlServicer_to_server(groundControl(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()