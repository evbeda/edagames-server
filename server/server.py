import os
from typing import Dict
from uvicorn.config import logger
import starlette
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
from server.connection_manager import ConnectionManager, AuthenticationError
from .router import router
from server.apigw_connection_manager import APIGatewayConnectionManager
from server.factory_event_server import FactoryServerEvent
import json

app = FastAPI()
app.include_router(router)

AWS_APIGW_SECRET = os.getenv('AWS_APIGW_SECRET')


@app.websocket("/ws")
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
    logger.error(f'\n\nthe request ({request})')
    logger.error(f'the request ({await request.json()})\n\n')
    try:
        if (
            ConnectionManager.connection_type != 'api_gateway'
            or (req_body := await request.json())['aws_apigw_secret'] != AWS_APIGW_SECRET
        ):
            logger.warning(f'User requested direct connection: {request.client.host}')
            apigw_url = req_body["apigw_ws_endpoint"]
            await APIGatewayConnectionManager.instance.disconnect(apigw_url, req_body["client_id"])
            raise AuthenticationError('API Gateway key mismatch')
    except (KeyError, json.JSONDecodeError, AuthenticationError):
        return JSONResponse({
            'error': 'Forbidden',
            'source_ip': request.client.host,
        }, status_code=403)

    connection_manager = APIGatewayConnectionManager.instance
    client_id = req_body["client_id"]
    apigw_url = req_body["apigw_ws_endpoint"]

    try:
        # Verify client using request.json()['query']['token']
        parsed_query = req_body['query'].strip('{}').split(', ')
        token = [v for (k, v) in [x.split('=') for x in parsed_query] if k == 'token'][0]
        await connection_manager.connect(apigw_url, client_id, token)
    except (json.JSONDecodeError, IndexError, AuthenticationError) as e:
        logger.warning(f'Error authenticating client ({client_id}): {e}')
        # Explicitly disconnect if auth fails using DELETE @connections api
        await connection_manager.disconnect(apigw_url, client_id)
        return


@app.post("/apigw-ws/disconnect")
async def apigw_disconnect(request: Request):
    try:
        if (
            ConnectionManager.connection_type != 'api_gateway'
            or (req_body := await request.json())['aws_apigw_secret'] != AWS_APIGW_SECRET
        ):
            logger.warning(f'User requested direct connection: {request.client.host}')
            apigw_url = req_body["apigw_ws_endpoint"]
            await APIGatewayConnectionManager.instance.disconnect(apigw_url, req_body["client_id"])
            raise AuthenticationError('API Gateway key mismatch')
    except (KeyError, json.JSONDecodeError, AuthenticationError):
        return JSONResponse({
            'error': 'Forbidden',
            'source_ip': request.client.host,
        }, status_code=403)

    connection_manager = APIGatewayConnectionManager.instance
    client_id = req_body["client_id"]
    apigw_url = req_body["apigw_ws_endpoint"]

    # Remove client from list on $disconnect
    await connection_manager.disconnect(apigw_url, client_id)


@app.post("/apigw-ws/message")
async def apigw_message(request: Request):
    logger.error(f'\n\nthe request ({request})')
    logger.error(f'the request ({await request.json()})\n\n')
    try:
        if (
            ConnectionManager.connection_type != 'api_gateway'
            or (req_body := await request.json())['aws_apigw_secret'] != AWS_APIGW_SECRET
        ):
            logger.warning(f'User requested direct connection: {request.client.host}')
            apigw_url = req_body["apigw_ws_endpoint"]
            await APIGatewayConnectionManager.instance.disconnect(apigw_url, req_body["client_id"])
            raise AuthenticationError('API Gateway key mismatch')
    except (KeyError, json.JSONDecodeError, AuthenticationError):
        return JSONResponse({
            'error': 'Forbidden',
            'source_ip': request.client.host,
        }, status_code=403)

    connection_manager = APIGatewayConnectionManager.instance
    client_id = req_body["client_id"]
    apigw_url = req_body["apigw_ws_endpoint"]

    if not connection_manager.validate_client(client_id):
        await connection_manager._send(apigw_url, client_id, 'Error', 'Unauthorized')
        await connection_manager.disconnect(apigw_url, client_id)
        return JSONResponse({
            'error': 'Unauthorized'
        }, status_code=401)

    if isinstance(message := req_body['message'], Dict):
        bot_name = connection_manager.client_id_to_bot[client_id]
        await FactoryServerEvent.get_event(message, bot_name).run()
    else:
        logger.info(f'Client ({client_id}) sent an invalid message: {message}')
        return JSONResponse({
            'error': 'Invalid message'
        }, status_code=400)


# @app.on_event("startup")
# async def startup_complete():
#     await ConnectionManager.instance.broadcast(
#         '',
#         'server_starting',
#         {
#             'message': 'Server instance is starting',
#         }
#     )


# @app.on_event("shutdown")
# async def shutdown_event():
#     await ConnectionManager.instance.broadcast(
#         '',
#         'server_shutdown',
#         {
#             'message': 'Server instance is shutting down',
#         }
#     )
