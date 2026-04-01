import pika
import random
import hashlib
import sys

addons = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]

def run_hash(serial):
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

def run(deminerID):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    defused_channel = connection.channel()
    defused_channel.queue_declare(queue='Defused-Mines')

    demine_channel = connection.channel()
    demine_channel.queue_declare(queue='Demine-Queue')
    
    while True:
        method, properties, body = demine_channel.basic_get(queue='Demine-Queue', auto_ack=True)
        if body is not None:
            serial = str(body, "utf-8").split(",")[1]
            print("Received Mine from Rover " + str(body, "utf-8").split(",")[0])
            pin = run_hash(serial)
            defused_message = str(body, "utf-8") + "," + deminerID + "," + pin
            print(defused_message)
            defused_channel.basic_publish(exchange="", routing_key='Defused-Mines', body=defused_message)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Proper usage: python deminer.py [deminerID]")
    elif len(sys.argv) == 2:
        run(sys.argv[1])
