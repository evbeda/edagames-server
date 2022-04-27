from asyncio.log import logger
import starlette
from fastapi import FastAPI, WebSocket, Request
from server.connection_manager import ConnectionManager, AuthenticationError
from .router import router
from server.apigw_connection_manager import APIGatewayConnectionManager
from server.factory_event_server import FactoryServerEvent
import json

app = FastAPI()
app.include_router(router)

@app.websocket("/ws/")
async def session(websocket: WebSocket, token):
    if ConnectionManager.connection_type != 'websocket':
        return

    client = await ConnectionManager.instance.connect(websocket, token)
    if client is None:
        return
    try:
        while True:
            msg = await websocket.receive_text()
            try:
                data = json.loads(msg)
            except json.decoder.JSONDecodeError:
                data = {}
            await FactoryServerEvent.get_event(data, client).run()
    except starlette.websockets.WebSocketDisconnect:
        await ConnectionManager.instance.remove_user(client)
        return

@app.post("/apigw-ws/connect")
async def apigw_connect(request: Request):
    if ConnectionManager.connection_type != 'api_gateway':
        return

    connection_manager = APIGatewayConnectionManager.instance

    try:
        req_body = await request.json()
        client_id = req_body["client_id"]
    except (json.JSONDecodeError, KeyError):
        logger.error("Connect to this server using API Gateway")

    try:
        # Verify client using request.json()['query']['token']
        token = json.loads(req_body['query'])['token']
    except (KeyError, AuthenticationError):
        # Explicitly disconnect if auth fails using DELETE @connections api
        await connection_manager.disconnect(client_id)
        return {}

    await connection_manager.connect(client_id, token)

@app.post("/apigw-ws/disconnect")
async def apigw_disconnect(request: Request):
    if ConnectionManager.connection_type != 'api_gateway':
        return

    connection_manager = APIGatewayConnectionManager.instance

    try:
        req_body = await request.json()
        client_id = req_body["client_id"]
    except (json.JSONDecodeError, KeyError):
        logger.error("Connect to this server using API Gateway")

    # Remove client from list on $disconnect
    await connection_manager.disconnect(client_id)

@app.post("/apigw-ws/message")
async def apigw_message(request: Request):
    if ConnectionManager.connection_type != 'api_gateway':
        return

    try:
        req_body = await request.json()
        client_id = req_body["client_id"]
    except (json.JSONDecodeError, KeyError):
        logger.error("Connect to this server using API Gateway")

    try:
        message = json.loads(req_body['message'])
    except json.decoder.JSONDecodeError:
        message = {}

    await FactoryServerEvent.get_event(message, client_id).run()
