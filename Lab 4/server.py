from fastapi import FastAPI
from pydantic import BaseModel
import json
import uvicorn
import roverClient
from threading import Lock, Thread

Map = []
rovers = {"rovers": []}
mines = {"mines": []}
mapLock = Lock()
roverLock = Lock()
maxMineID = 0
maxRoverID = 0
height = 0
width = 0


class createMineReq(BaseModel):
    x : int
    y : int
    serial : str

class updateMineReq(BaseModel):
    x : int | None
    y : int | None
    serial : str | None
    armed : bool | None
    pin : str | None

class createRoverReq(BaseModel):
    cmds : str

class updateCmdReq(BaseModel):
    cmds : str

class mapUpdateReq(BaseModel):
    height: int | None
    width: int | None


server = FastAPI()

# Map
@server.get("/map")
def getMap():
    return {"map" : Map}

@server.put("/map/")
def putMap(body: mapUpdateReq):
    global Map, height, width, mapLock
    # add extra rows
    with mapLock:
        if height <= body.height:
            for i in range(body.height - height):
                row = []
                for j in range(body.width):
                    row.append(0)
                Map.append(row)
        else:
            # remove extra rows from Map
            for i in range(height - body.height):
                Map.pop(len(Map)-(i+1))
        # add cells to existing rows
        if width <= body.width:
            for i in range(height):  
                for j in range(body.width - width):
                    Map[i].append(0)
        else:
            # remove extra cells from rows
            for i in range(body.height):
                for j in range(width - body.width):
                    Map[i].pop(len(Map[i])-(j+1))
        height = body.height
        width = body.width
        for mine in mines["mines"]:
            Map[mine["y"]][mine["x"]] = mine["id"]
        return {"height": height, "width": width, "map": Map}

# Mines
@server.get("/mines")
def getMines():
    return mines

@server.get("/mines/{id}")
def getMineID(id: int):
    for mine in mines["mines"]:
        if mine["id"] == id:
            return {"Success": True, "mine": mine, "error": None}
    return {"Success": False, "mine": None, "error": f"Error: mine with ID {id} not found"}

@server.delete("/mines/{id}")
def delMineID(id: int):
    global mines, mapLock
    for mine in mines["mines"]:
        if mine["id"] == id:
            with mapLock:
                Map[mine["y"]][mine["x"]] = 0
            mines["mines"].remove(mine)
            return {"Success": True, "error": None}
    return {"Success": False, "error": f"Error: mine with ID {id} not found"}

@server.post("/mines/")
def createMine(body: createMineReq):
    global maxMineID, mines, mapLock
    maxMineID += 1
    if Map[body.y][body.x] == 0:
        mines["mines"].append({"id": maxMineID, "Serial Number": body.serial, "x": body.x, "y": body.y, "armed": True, "pin": ""})
        with mapLock:
            Map[body.y][body.x] = maxMineID
        return {"Success": True, "id": maxMineID, "error": None}
    return {"Success": False, "id": None, "error": f"Error: mine already exists at {body.x}, {body.y}"}

@server.put("/mines/{id}/")
def updateMine(id: int, body: updateMineReq):
    global mines, Map
    for mine in mines["mines"]:
        if mine["id"] == id:
            if body.serial != None:
                mine["Serial Number"] = body.serial
            if body.x != None:
                with mapLock:
                    Map[mine["y"]][mine["x"]] = 0
                    mine["x"] = body.x
                    Map[body.y][body.x] = mine["id"]
            if body.y != None:
                with mapLock:
                    Map[mine["y"]][mine["x"]] = 0
                    mine["y"] = body.y
                    Map[body.y][body.x] = mine["id"]
            if body.armed != None:
                mine["armed"] = body.armed
            if body.pin != None:
                mine["pin"] = body.pin
            
            return {"Success": True, "mine": mine, "error": None}
    return {"Success": False, "mine": None, "error": f"Error: mine with ID {id} not found"}

# Rovers
@server.get("/rovers")
def getRovers():
    return rovers

@server.get("/rovers/{id}")
def getRoverID(id: int):
    for rover in rovers["rovers"]:
        if rover["id"] == id:
            return {"Success": True, "rover": rover, "error": None}
    return {"Success": False, "rover": None, "error": f"Error: rover with ID {id} not found"}

@server.post("/rovers/")
def createRover(roverReq: createRoverReq):
    global rovers, maxRoverID
    print(roverReq.cmds)
    with roverLock:
        maxRoverID += 1
        rovers["rovers"].append({"id": maxRoverID, "status": "Not Started", "commands": roverReq.cmds, "x": 0, "y": 0})
        return {"Success": True, "id": maxRoverID}

@server.delete("/rovers/{id}")
def delRover(id: int):
    global roverLock, rovers
    with roverLock:
        for rover in rovers["rovers"]:
            if rover["id"] == id:
                rovers["rovers"].remove(rover)
                return {"Success": True, "error": None}
        return {"Success": False, "error": f"Error: rover with ID {id} not found"}


@server.put("/rovers/{id}/")
def sendCmd(id: int, cmds: updateCmdReq):
    global rovers
    for rover in rovers["rovers"]:
        if rover["id"] == id:
            with roverLock:
                if rover["status"] == "Not started" or "Finished":
                    rover["commands"] = cmds.cmds
                    return {"Success": True, "error": None}
                else:
                    return {"Success": False, "error": f"Error: rover status is {rover["status"]}"}
    return {"Success": False, "error": f"Error: rover with ID {id} not found"}


@server.post("/rovers/{id}/dispatch/")
async def dispatchRover(id: int):
    global rovers, Map, height, width, mapLock, roverLock
    for rover in rovers["rovers"]:
        if rover["id"] == id:
            if rover["status"] == "Not Started":
                rover["status"] = "Moving"
                # insert rover code here
                roverThread = Thread(target=roverClient.run, args=(Map, height, width, rover, mapLock, roverLock))
                roverThread.start()

                return {"Success": True, "rover": rover, "error": None}
            else:
                return {"Success": False, "error": f"Error: rover in {rover["status"]} state"}
    return {"Success": False, "error": f"Error: rover with ID {id} not found"}

@server.on_event("startup")
def startup():
    global height, width, Map, mines, maxMineID
    Map = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
    height = 4
    width = 3

if __name__ == '__main__':
    uvicorn.run("server:server", host="0.0.0.0", port=8000, reload=True)

