import requests
from googletrans import Translator
from bottle import (
    run, post, response, request as bottle_request
)
import logging
import json

translator = Translator()


def get_ngrok_url():
    url = "http://localhost:4040/api/tunnels"
    res = requests.get(url)
    res_unicode = res.content.decode("utf-8")
    res_json = json.loads(res_unicode)
    return res_json["tunnels"][0]["public_url"]


class Telebot:
    def __init__(self):
        self.bot_url = 'https://api.telegram.org/bot1291011387:AAEDG2wqE0t4XHbe_9RurkcJHJ_Fdw99rf8/'
        self.chat_id = ''
        self.text = ''

    def set_webhook(self):
        # first check the existing webhook
        check_webhook_url = self.bot_url+'getWebHookinfo'
        webhook_response = requests.get(check_webhook_url).json()
        webhook_url = webhook_response['result']['url']

        ngrok_url = get_ngrok_url()

        if not ngrok_url[-17:].__eq__(webhook_url[-17:]):
            print("Previous Webhook: "+webhook_url)
            print("New Webhook: "+ngrok_url)

            method = 'deleteWebHook'
            requests.get(self.bot_url + method)

            method = 'setWebHook' + f'?url=https://{ngrok_url[-17:]}'
            response = requests.get(self.bot_url + method)

    def get_details(self, data):

        # Get the chat id and sender information
        self.chat_id = data['message']['chat']['id']
        self.sender = data['message']['from']['first_name']
        try:
            self.text = data['message']['text']
        except:
            self.text = 'error'

        log_message = f'Text:{self.text} From:{self.sender} chat_id:{self.chat_id}'
        logging.info(log_message)

    def reply(self):
        message_url = self.bot_url+'sendMessage'

        if self.text.__eq__('/start'):
            message = "You seem to be new here. I'm here to guide.Send me Something and I will convert it to Spanish"
        elif self.text.__eq__('error'):
            message = 'Error Occured!'
        else:
            try:
                translated_text = translator.translate(
                    self.text, dest='es', src='en')
                message = translated_text.text
            except:
                message = 'Error occured while translating! Dont include any emoji'

        json_data = {
            "chat_id": self.chat_id,
            "text": message
        }

        requests.post(message_url, json=json_data)


@post('/')
def main():
    data = bottle_request.json
    bot.get_details(data)
    bot.reply()
    return response


if __name__ == '__main__':
    bot = Telebot()
    # bot.set_webhook()
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        filename='bot.log', datefmt="%H:%M:%S")
    logging.info("Started server at port 8080")
    run(host='localhost', port=8080, debug=True)
