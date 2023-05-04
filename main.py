import json
from threading import Thread

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


class ChatAPI:
    def __init__(self, server_url):
        self.server_url = server_url

    def send_message(self, nickname, message):
        response = requests.post(self.server_url + '/messages', json={"messages": [{"nickname": nickname, "message": message}]})
        return response.json()

    def get_messages(self):
        response = requests.get(self.server_url + '/messages')
        return response.json()


class MyRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.api = None
        self.nickname = None
        self.messages = []

        self.ip_text = TextInput(text='127.0.0.1', font_size=36)
        self.nickname_text = TextInput(hint_text='Nickname', font_size=36)
        self.connect_btn = Button(text='Connect', font_size=32, size=(100, 50), size_hint=(1, None), height=70)
        self.connect_btn.bind(on_press=self.connect_to_server)

        self.connection_grid = BoxLayout(orientation='horizontal', padding=10, spacing=10, height=125, size_hint=(1, None))
        self.connection_grid.add_widget(self.ip_text)
        self.connection_grid.add_widget(self.nickname_text)

        self.chat_history_label = Label(text='Chat History', font_size=30, height=50, size_hint=(1, None), color=(0.92, 0.45, 0, 1))
        self.chat_text = TextInput(multiline=True, font_size=36, readonly=True, disabled=True)

        self.message_label = Label(text='Your Message', font_size=42, height=50, size_hint=(1, None), color=(0.92, 0.45, 0, 1))
        self.message_text = TextInput(font_size=36)
        self.send_btn = Button(text='Send', font_size=32, size=(100, 50), on_press=self.send_message, disabled=True)

        
        self.add_widget(self.connection_grid)
        self.add_widget(self.connect_btn)
        self.add_widget(self.chat_history_label)
        self.add_widget(self.chat_text)
        self.add_widget(self.message_label)
        self.add_widget(self.message_text)
        self.add_widget(self.send_btn)

        Clock.schedule_interval(self.update_messages, 1)

    def connect_to_server(self, *args):
        server_ip = self.ip_text.text
        self.nickname = self.nickname_text.text
        if server_ip and self.nickname:
            self.api = ChatAPI('http://' + server_ip + ':5000')
            self.connect_btn.disabled = True
            self.ip_text.disabled = True
            self.nickname_text.disabled = True
            self.send_btn.disabled = False

    def send_message(self, *args):
        message = self.message_text.text
        if message and self.api:
            Thread(target=self.api.send_message, args=(self.nickname, message)).start()
            self.message_text.text = ''

    def update_messages(self, *args):
        if self.api:
            messages = self.api.get_messages()
            if messages != self.messages:
                chat_history = ''
                s = 0 
                while s < len(messages):
                    chat_history += messages["messages"][s]["nickname"]  + ': ' + messages["messages"][s]["message"] + '\n'
                    s+= 1
            self.chat_text.text = chat_history

class ChatApp(App):
    def build(self):
        return MyRoot()

if __name__ == '__main__':
    ChatApp().run()