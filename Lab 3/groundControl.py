import grpc
import groundControl_pb2
import groundControl_pb2_grpc
import requests
import concurrent.futures as futures
import logging
import pika

URL = 'http://127.0.0.1:8000/lab1/rover/'
def cmd(num: int):
    try:
        response = requests.get(URL + str(num))
        response.raise_for_status()
        return response.json()['commands']
    except requests.exceptions.RequestException as e:
        print("Error: " + str(e))

def callback(channel, method, properties, body):
    msg = str(body, "utf-8").split(",")
    print("Mine " + msg[1] + " found by Rover " + msg[0] + " at " + msg[2] + "," + msg[3] + " was disarmed by Deminer " + msg[4] + ".")

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
        if str(request.posX) + "," + str(request.posY) not in positions:
            return groundControl_pb2.serialReply(mineSerial=None)
        for i in positions:
            if i == str(request.posX) + "," + str(request.posY):
                break
            count += 1
        return groundControl_pb2.serialReply(mineSerial=contents[count+1])
        
    
def serve():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='Defused-Mines')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    groundControl_pb2_grpc.add_ground_controlServicer_to_server(groundControl(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    channel.basic_consume(queue='Defused-Mines', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()