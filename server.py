import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import database
from model import ModelManager
from websocket import ConnectionManager
from predictData import PredictData

manager = ConnectionManager()
model = ModelManager()
app = FastAPI()

logger = logging.getLogger("Server")
predictData = PredictData()


@app.websocket("/")
async def websocket_point_loader(websocket: WebSocket):
    await websocket.accept()
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast_mocopi("calc")
            points = json.loads(data)
            points.pop("group_id")
            logger.info(points)

            ans = model.predict(points)
            predicted_group_id = ans.iloc[0]
            predictData.knn = predicted_group_id
            print("knn:", predicted_group_id)

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


def x_round(value: float) -> int:
    return int(value / 0.8)


def y_round(value: float) -> int:
    return int(value / 0.8)


@app.websocket("/mocopi")
async def websocket_point_loader(websocket: WebSocket):
    await websocket.accept()
    await manager.connect(websocket, False)
    try:
        while True:
            data = await websocket.receive_text()
            print("mocopi raw:", data)
            acc = data.split(' ')

            # 移動距離を求める!! X Y 別々に 100 => y=1 x=0  310 => y=3 x=10
            latest_x: int = predictData.latestKnn % 100
            latest_y: int = int(predictData.latestKnn / 100)
            pre_x: int = predictData.knn % 100
            pre_y: int = int((predictData.knn / 100))

            del_x = pre_x - latest_x
            del_y = pre_y - latest_y

            fix_pre_x = x_round(float(acc[0])) - del_x
            fix_pre_y = (y_round(-float(acc[2])) - del_y) * 100

            fix_pre = predictData.knn + fix_pre_x + fix_pre_y
            fix_pre = fix_pre if fix_pre < 1000 else 0

            print(latest_x, latest_y, pre_x, pre_y, del_x, del_y)
            logger.info(f"group_id is estimated to be {predictData.knn} {fix_pre_x} {fix_pre_y} {fix_pre}")
            await manager.broadcast_rtt(json.dumps({"group_id": int(predictData.knn), "group_id_mocopi": int(fix_pre)}))
            predictData.latestKnn = fix_pre

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(WebSocketDisconnect)
