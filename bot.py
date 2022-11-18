import telebot
from telebot import types
import re
import requests
import urllib3
http = urllib3.PoolManager()
from statistics import mode
import nltk
#nltk.download('averaged_perceptron_tagger_ru')
#nltk.download('punkt')

bot = telebot.TeleBot('5615009716:AAE9o2yXbqNIrxKr4vXjkxl6wNhlolcT-kw')


@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь? Напиши /help")


@bot.message_handler(commands=['help'])
def get_help(message):
    if message.text == '/help':
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        item_btn1 = types.KeyboardButton('Проверить сайт')
        item_btn2 = types.KeyboardButton('Проанализировать текст')
        item_btn3 = types.KeyboardButton('Воспользоваться калькулятором')
        keyboard.add(item_btn1, item_btn2, item_btn3)
        bot.send_message(message.chat.id, "Что я могу для тебя сделать?", reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
	if message.text == 'Проверить сайт':
		bot.send_message(message.from_user.id, 'Напиши URL-адрес сайта на проверку или "другое" для выхода')
		bot.register_next_step_handler(message, get_URL); 
	elif message.text == 'Проанализировать текст':
		bot.send_message(message.from_user.id, 'Напиши текст, который нужно проанализировать или "другое" для выхода')
		bot.register_next_step_handler(message, get_analysis);
	elif message.text == 'Воспользоваться калькулятором':
		bot.send_message(message.from_user.id, 'Напиши два числа через пробел или "другое" для выхода')
		bot.register_next_step_handler(message, get_calc); 
	else:	
		bot.send_message(message.from_user.id, 'Напиши, пожалуйста, /help')

#Проверка сайта
def get_URL(message):
	global URL
	URL = message.text.lower()
	if URL == 'другое':
		bot.send_message(message.from_user.id, 'Выбери что-то другое через /help')
	else: 
		try:
			response = requests.get(URL)
			bot.send_message(message.from_user.id, 'Сайт доступен, ура! 🥳 ')
		except:
			bot.send_message(message.from_user.id, 'Сайт не доступен, прости 💔 ')


#Калькулятор
def get_calc(message):
	global string_numbers
	string_numbers = message.text.lower()
	if string_numbers == 'другое':
		bot.send_message(message.from_user.id, 'Выбери что-то другое через /help')
	else: 
		calc = types.ReplyKeyboardMarkup(row_width=2)
		item_btn1 = types.KeyboardButton('+')
		item_btn2 = types.KeyboardButton('-')
		item_btn3 = types.KeyboardButton('*')
		item_btn4 = types.KeyboardButton('/')
		calc.add(item_btn1, item_btn2, item_btn3, item_btn4)
		bot.send_message(message.chat.id, 'Выбери математический оператор:', reply_markup=calc)
		bot.register_next_step_handler(message, calc_do)

def calc_do(message):
	try: 
		counts = string_numbers.split()
		if message.text == '+':
			summa = int(counts[0]) + int(counts[1])
			bot.send_message(message.from_user.id, f'Сумма твоих чисел равна {summa}')
		elif message.text == '-':
			minus = int(counts[0]) - int(counts[1])
			bot.send_message(message.from_user.id, f'Разность твоих чисел равна {minus}')
		elif message.text == '*':
			proizv = int(counts[0]) * int(counts[1])
			bot.send_message(message.from_user.id, f'Произведение твоих чисел равно {proizv}')
		elif message.text == '/':
			if int(counts[1]) == 0:
				bot.send_message(message.from_user.id, 'На 0 делить нельзя')
			else:
				chast = int(counts[0]) / int(counts[1])
				bot.send_message(message.from_user.id, f'Частное чисел равно {chast}')
	except:
		bot.send_message(message.from_user.id, 'Остановись, это уже перебор!')

	calc = types.ReplyKeyboardRemove(selective=True)
	bot.send_message(message.chat.id, 'Введи два числа через пробел или "другое" для выхода: ', reply_markup=calc)
	bot.register_next_step_handler(message, get_calc)

#Анализ текста
def get_analysis(message):
	user_text = message.text.lower()
	if user_text == 'другое':
		bot.send_message(message.from_user.id, 'Выбери что-то другое через /help')
	else:
		final_text = re.sub(r'[^\w\s]','', user_text)
		all_words = final_text.split() #список ВСЕХ слов без знаков препинания
		longest_word = max(all_words, key=len)
		text_dict = {}
		for word in all_words:
			if word in text_dict:
				text_dict[word] += 1
			else:
				text_dict[word] = 1

		new_text = re.sub(r'[.!?]\s', r'|', user_text)
		count_sent = len(new_text.split('|')) #считаем предложения

		sl_parts = {'CONJ', 'PR'}
		new_words = [word for word, pos in nltk.pos_tag(all_words, lang='rus') if pos not in sl_parts] #список слов БЕЗ союзов, предлогов и знаков препинания
		    	
		bot.send_message(message.from_user.id, f'''Анализ исходного текста: 
		всего слов в тексте - {len(all_words)},
		количество предложений - {count_sent}, 
		самое популярное слово (не учитывая предлоги и союзы) - "{mode(new_words)}", 
		самое длинное слово - "{longest_word}",  
		количество каждого слова: {text_dict},
		всего уникальных слов - {len(text_dict)}''')
        

bot.polling(none_stop=True, interval=0)