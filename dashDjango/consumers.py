# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DashConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Here, you can process the message received from the Dash app
        print("Message received from Dash app:", message)
