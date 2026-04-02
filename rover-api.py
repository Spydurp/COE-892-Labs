from fastapi import FastAPI
import random
import uvicorn

app = FastAPI()
@app.get("/lab1/rover/{number}")

def get_rover_commands(number: int):
    commands = ["L", "R", "M"]
    sequence = "".join(random.choice(commands) for _ in range(number))
    return {
    "commands": sequence
    }

if __name__ == '__main__':
    uvicorn.run("rover-api:app", host="0.0.0.0", port=8000, reload=True)