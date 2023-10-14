from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

# class TestConsumer(WebsocketConsumer):
class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = 'test_consumer'
        self.room_group_name = 'test_consumer_group'
        # print(self.room_group_name, self.channel_name)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(text_data=json.dumps({
            'status': 'connected from django channel'
        }))

        # self.room_group_name = 'test'

        # async_to_sync(self.channel_layer.group_add)(
        #     self.room_group_name,
        #     self.channel_name
        # )

        # self.accept()

    def receive(self, text_data):
        # print(text_data)
        self.send(text_data=json.dumps({
            'status': 'we got you'
        }))
        # text_data_json = json.loads(text_data)
        # message = text_data_json['message']

        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name,{
        #         'type': 'chat_message',
        #         'message': message
        #     }
        # )

        # print('Message:', message)

        # self.send(text_data = json.dumps({
        #     'type': 'chat',
        #     'message': message
        # }))

    def disconnect(self, *args, **kwargs):
        print('disconnected')

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'type':'chat',
            'message':message
        }))

    def send_notification(self, event):
        data = json.loads(event.get('value'))
        self.send(text_data=json.dumps({
            'payload': data
        }))