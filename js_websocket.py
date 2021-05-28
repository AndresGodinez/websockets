#!/usr/bin/env python

import os, sys
import asyncio
import json
from json import dumps
import logging
import websockets
import gc
from subprocess import call
import subprocess



logging.basicConfig()
STATE = {"value": 0}
USERS = set()
index = 0;

def state_event():
    return json.dumps({"type": "state", **STATE})
def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})

async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])
async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        gc.collect()
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    USERS.add(websocket)
    gc.collect()
    await notify_users()
async def unregister(websocket):
    USERS.remove(websocket)
    gc.collect()
    await notify_users()

def imprimir():
    print('Va todo la impresión Andres')

async def accionWebSocket(websocket, path):

    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "imprimir":
                raw_data = {'status':1}
                json_data = dumps(raw_data, indent=2)
                STATE["value"] = json_data
                
                imprimir()


                await notify_state()
                gc.collect()
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)

try:
    start_server = websockets.serve(accionWebSocket, '127.0.0.1', 8001)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
except IOError as e:
    print(e)

