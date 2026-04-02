import requests
import json
import os
import server
import time

URL = 'http://127.0.0.1:8000/'
DELAY = 1

def displayMap():
    m = requests.get(URL + "map").json()
    for row in m["map"]:
        print(row)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == '__main__':
    while True:
        clear()
        displayMap()
        print("Spawn Rover: 1")
        print("See Rovers: 2")
        print("Edit Rover Commands: 3")
        print("Delete Rover: 4")
        print("Dispatch Rover: 5")
        print("Edit Map: 6")
        print("Create Mine: 7")
        print("Edit Mine: 8")
        print("See Mine Details: 9")
        print("Delete Mine: 10")
        print("Exit: -1")
        opIn = input(">> ")
        match opIn:
            case "-1":
                break
            case "1":
                clear()
                print("Spawn Rover")
                print("Commands: (L, R, M, D)")
                commands = input(">> ")
                body = server.createRoverReq(cmds=commands)
                r = requests.post(URL + "/rovers", json=body.model_dump()).json()
                if r["Success"]:
                    print(f"Rover successfully spawned with ID {r["id"]}")
                print("Press enter to return to main menu")
                input()
            case "2":
                clear()
                print("See Rovers")
                print("Rover ID: (Enter -1 to see all rovers)")
                rID = input(">> ")
                if rID == "-1":
                    rovers = requests.get(URL + "rovers").json()
                    for r in rovers["rovers"]:
                        print(r)
                else:
                    rovers = requests.get(URL + f"rovers/{int(rID)}").json()
                    if rovers["Success"]:
                        print(rovers["rover"])
                    else:
                        print(rovers["error"])
                print("Press enter to return to main menu")
                input()
            case "3":
                clear()
                print("Update Rover Commands")
                print("Rover ID: ")
                rID = input(">> ")
                print("Commands: (L, R, M, D)")
                commands = input(">> ")
                body = server.updateCmdReq(cmds=commands)
                ret = requests.put(URL + f"rovers/{rID}", json=body.model_dump()).json()
                if ret["Success"]:
                    print("Commands updated")
                else:
                    print(ret["error"])
                print("Press enter to return to main menu")
                input()
            case "4":
                clear()
                print("Delete Rover")
                print("Rover ID: ")
                rID = input(">> ")
                ret = requests.delete(URL + f"rovers/{rID}").json()
                if ret["Success"]:
                    print(f"Rover {rID} successfully deleted")
                else:
                    print(ret["error"])
                print("Press enter to return to main menu")
                input()
            case "5":
                clear()
                print("Dispatch Rover")
                print("Rover ID: ")
                rID = input(">> ")
                ret = requests.post(URL + f"rovers/{rID}/dispatch").json()
                if ret["Success"]:
                    print(f"Successfully dispatched Rover {rID}")
                    print(ret["rover"])
                else:
                    print(ret["error"])
                print("Press enter to return to main menu")
                input()
            case "6":
                clear()
                print("Edit Map")
                print("New Height: ")
                h = input(">> ")
                print("New Width: ")
                w = input(">> ")
                if w == "":
                    w = None
                if h == "":
                    h = None
                body = server.mapUpdateReq(height=h, width=w)
                ret = requests.put(URL + "map", json=body.model_dump()).json()
                print("Press enter to return to main menu")
                input()
            case "7":
                clear()
                print("Create Mine")
                print("x position: ")
                x = input(">> ")
                print("y position: ")
                y = input(">> ")
                print("Serial Number: ")
                ser = input(">> ")
                body = server.createMineReq(x=int(x), y=int(y), serial=ser)
                ret = requests.post(URL + "mines", json=body.model_dump()).json()
                if ret["Success"]:
                    print(f"Mine successfully created at {x}, {y} with ID {ret["id"]}")
                else:
                    print(ret["error"])
                print("Press enter to return to main menu")
                input()
            case "8":
                clear()
                print("Edit Mine")
                print("Mine ID: ")
                mID = input(">> ")
                print("x position: ")
                x = input(">> ")
                print("y position: ")
                y = input(">> ")
                print("Serial Number: ")
                ser = input(">> ")
                body = server.updateMineReq(x=None, y=None, serial=None, armed=None, pin=None)
                if x == "":
                    body.x = None
                else:
                    body.x = int(x)
                if y == "":
                    body.y = None
                else:
                    body.y = int(y)
                if ser == "":
                    body.serial = None
                else:
                    body.serial = ser
                
                ret = requests.put(URL + f"mines/{mID}", json=body.model_dump()).json()
                if ret["Success"]:
                    print("Mine successfully edited:")
                    print(ret["mine"])
                else:
                    print(ret["error"])
                print("Press enter to return to main menu")
                input()
            case "9":
                clear()
                print("See Mine Details")
                print("Mine ID: (Enter -1 to see all mines)")
                mID = input(">> ")
                if mID == "-1":
                    ret = requests.get(URL + "mines").json()
                    for mine in ret["mines"]:
                        print(mine)
                else:
                    ret = requests.get(URL + f"mines/{mID}").json()
                    if ret["Success"]:
                        print(ret["mine"])
                    else:
                        print(ret["error"])
                print("Press enter to return to main menu")
                input()
            case "10":
                clear()
                print("Delete Mine")
                print("Mine ID: ")
                mID = input(">> ")
                ret = requests.delete(URL + f"mines/{mID}").json()
                if ret["Success"]:
                    print(f"Successfully deleted Mine {mID}")
                else:
                    print(ret["error"])
                print("Press enter to return to main menu")
                input()
            