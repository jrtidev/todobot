import json 
import time
import requests
import urllib
from dbhelper import DBHelper 

TOKEN = '<YOUR TOKEN>'
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)
db = DBHelper()

#downloads content from url and gives us a string
def get_url(url):
	response = requests.get(url)
	content = response.content.decode('utf8')
	return content

#parse url response into dictionary object
def get_json_from_url(url):
	content = get_url(url)
	js = json.loads(content)
	return js

#get updates of all messages 
def get_updates(offset=None):
	url = URL + 'getUpdates?timeout=100'
	#offset param indicate which message is latest so that older messages won't be uploaded
	if offset:
		url +='&offset={}'.format(offset)
		print(url)
	js = get_json_from_url(url)
	return js

def get_last_update_id(updates):
	update_ids = []
	for update in updates['result']:
		update_ids.append(int(update['update_id']))
	return max(update_ids)

def handle_updates(updates):
	for update in updates['result']:
		# if 'sticker' in update['message'].keys():
		# 	print('Message: Sticker')
		text = update['message']['text']
		chat = update['message']['chat']['id']
		items = db.get_items(chat)
		if text =='/done':
			keyboard = build_keyboard(items)
			send_message('Select an item to delete', chat, keyboard)
		elif text == '/gif':
			send_message('Ваша рандомная гифка дня!', chat)
			url = 'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC'
			r = requests.get(url)
			jr = r.json()
			randGif = jr['data']['image_original_url']
			send_message(randGif, chat)
		elif text == '/start':
			send_message('Добро пожаловать в Telegram TODO List!', chat)
			time.sleep(1)
			send_message('Работать с ним так же просто, как досчитать до 3-х...', chat)
			time.sleep(1)
			send_message('1. Любое ваше сообщение отправляется в ваш собственный TODO List', chat)
			time.sleep(1)
			send_message('2. Когда список будет готов, отправьте сообщение с текстом \'/done\' и вы сможете начать его выполнять!', chat)
			time.sleep(1)
			send_message('3. Выполнив пункт списка, нажмите на кнопку с соответствующим текстом и он удалится будет удалён!', chat)
			time.sleep(1)
			send_message('Успехов!', chat)
		elif text.startswith('/'):
			continue
		elif text in items:
			db.delete_item(text, chat)
			print('dublicate item')
			items = db.get_items(chat)
			keyboard = build_keyboard(items)
			send_message('Select an item to delete', chat, keyboard)
		else:
			db.add_item(text, chat)
			print('item added')
			items = db.get_items(chat)
			message = '\n'.join(items)
			send_message(message, chat)
			
#add keyboard
def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)
	
#get only last chat message instead of all
def get_last_chat_id_and_text(updates):
	num_updates = len(updates['result'])
	last_update = num_updates-1
	text = updates['result'][last_update]['message']['text']
	chat_id = updates['result'][last_update]['message']['chat']['id']
	return (text, chat_id)

#sending message
def send_message(text, chat_id, reply_markup=None):
	text = urllib.parse.quote_plus(text)
	url = URL + 'sendMessage?text={}&chat_id={}&parse_mode=Markdown'.format(text, chat_id)
	if reply_markup:
		url += '&reply_markup={}'.format(reply_markup)
	get_url(url)

def main():
	db.setup()
	last_update_id = None
	while True:
		updates = get_updates(last_update_id)
		if len (updates['result'])>0:
			last_update_id = get_last_update_id(updates)+1
			handle_updates(updates)
		time.sleep(0.5)

if __name__ == '__main__':
	main()
