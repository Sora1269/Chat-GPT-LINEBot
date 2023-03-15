import openai
import os
import time
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,

app = Flask(__name__)

openai.api_key = os.environ["OPENAI_API_KEY"]
line_bot_api = LineBotApi(os.environ["LINE_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_ACCESS_SECRET"])

def create_response(text):
	response = openai.ChatCompletion.create(
		model="gpt-3.5-turbo",
		messages=[
			{"role": "system", "content": text}
		]
	)
	result = response["choices"][0]["message"]["content"]
	return result

@app.route("/callback", methods=['POST'])
def callback():
	signature = request.headers['X-Line-Signature']

	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)

	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		print("Invalid signature. Please check your channel access token/channel secret.")
		abort(400)

	return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	response_message = create_response(event.message.text)
	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text=response_message))

if __name__ == '__main__':
	app.run()
