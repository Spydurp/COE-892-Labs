from fastapi import FastAPI
from pydantic import BaseModel

MAP = []
rovers = []
mines = {"mines": []}
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
async def getMap():
    return {"map" : MAP}

@server.put("/map")
async def putMap(body: mapUpdateReq):
    # add extra rows
    if height <= body.height:
        for i in range(body.height - height):
            row = []
            for j in range(body.width):
                row.append(0)
            MAP.append(row)
    else:
        # remove extra rows from MAP
        for i in range(height - body.height):
            MAP.pop(len(MAP)-(i+1))
    # add cells to existing rows
    if width <= body.width:
        for i in range(height):  
            for j in range(body.width - width):
                MAP[i].append(0)
    else:
        # remove extra cells from rows
        for i in range(body.height):
            for j in range(width - body.width):
                MAP[i].pop(len(MAP[i])-(j+1))
    height = body.height
    width = body.width
    
    return {"height": height, "width": width, "map": MAP}

# Mines
@server.get("\mines")
async def getMines():
    pass

@server.get("/mines/{id}")
async def getMineID(id: int):
    pass

@server.delete("/mines/{id}")
async def delMineID(id: int):
    pass

@server.post("/mines/")
async def createMine(body: createMineReq):
    pass

@server.put("/mines/{id}")
async def updateMine(id: int, body: updateMineReq):
    pass

# Rovers
@server.get("rovers")
async def getRovers():
    pass

@server.get("/rovers/{id}")
async def getRoverID(id: int):
    pass

@server.post("/rovers")
async def createRover(roverReq: createRoverReq):
    pass

@server.delete("/rovers/{id}")
async def delRover(id: int):
    pass

@server.put("/rovers/{id}")
async def sendCmd(id: int, cmds: updateCmdReq):
    pass

@server.post("/rovers/{id}/dispatch")
async def dispatchRover(id: int):
    pass

if __name__ == '__main__':
    with open("map.txt", "r") as map:
        ybound, xbound = map.readline().split(" ")
        height = int(ybound)
        width = int(xbound)
        for row in map.read().split("\n"):
            r = []
            for i in row.split(" "):
                r.append(int(i))
            MAP.append(r)
    filename = "mines.txt"
    contents = ""
    with open(filename, "r") as minesFile:
        contents = minesFile.read()
    contents = contents.split("\n")
    positions = contents[0].split(" ")
    serialNumbers = contents[1:]

    for i in range(serialNumbers):
        x = positions[i].split(",")[0]
        y = positions[i].split(",")[1]
        mines["mines"].append({"Serial Number": serialNumbers[i], "x": x, "y": y})

