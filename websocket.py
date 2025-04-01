from typing import List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.isRTTs: List[bool] = []

    async def connect(self, websocket: WebSocket, isRtt: bool = True):
        self.connections.append(websocket)
        self.isRTTs.append(isRtt)
        print(self.connections, self.isRTTs)

    def disconnect(self, websocket: WebSocket):
        index = self.connections.index(websocket)
        self.connections.remove(websocket)
        self.isRTTs.pop(index)

    async def broadcast(self, message: str):
        for connection in self.connections:
            await connection.send_text(message)

    async def broadcast_mocopi(self, message: str):
        for index, connection in enumerate(self.connections):
            if self.isRTTs[index]:
                continue
            await connection.send_text(message)

    async def broadcast_rtt(self, message: str):
        for index, connection in enumerate(self.connections):
            if not self.isRTTs[index]:
                continue
            await connection.send_text(message)