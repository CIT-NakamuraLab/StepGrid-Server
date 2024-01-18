import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import database
from model import ModelManager
from websocket import ConnectionManager

manager = ConnectionManager()
model = ModelManager()
app = FastAPI()

logger = logging.getLogger("Server")


@app.websocket("/")
async def websocket_point_loader(websocket: WebSocket):
    await websocket.accept()
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            points = json.loads(data)
            points.pop("group_id")
            logger.info(points)

            ans = model.predict(points)
            predicted_group_id = ans.iloc[0]
            logger.info(f"group_id is estimated to be {predicted_group_id}")
            await websocket.send_text(f"Group Id: {predicted_group_id}\n")

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/point")
async def websocket_point_logger(websocket: WebSocket):
    await websocket.accept()
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            points = json.loads(data)
            logger.info(points)
            database.update_point(points)

    except WebSocketDisconnect:
        manager.disconnect(websocket)