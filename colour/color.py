# -*- coding: utf-8 -*-
import flask
import telebot
import conf

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)

bot = telebot.TeleBot(conf.TOKEN, threaded=False)  # бесплатный аккаунт pythonanywhere запрещает работу с несколькими тредами

# удаляем предыдущие вебхуки, если они были
bot.remove_webhook()

# ставим новый вебхук = Слышь, если кто мне напишет, стукни сюда — url
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

# coding: utf-8

# In[1]:

import re


# In[2]:

def questions_list():#массив вопросов
    fr = open('/home/panteleeva/mysite/questions.txt')
    questions = []
    for line in fr:
        line = re.sub ('\n','',line)
        questions.append(line)
    return questions


# In[3]:

def questions_dict():
    questions = questions_list()
    dict_q = {}
    i = 0
    for q in questions:
        dict_q[q] = i
        i += 1
    return dict_q


# In[4]:

dict_q = questions_dict()
#dict_q = {'q0':0, 'q1':1, 'q2':2, 'q3':3, 'q4':4}
print(dict_q)
dict_r_rev = {v: k for k, v in dict_q.items()}
print(dict_r_rev)
keys = list(dict_r_rev.keys())
print(keys)


# In[5]:

import telebot
import conf
import random

bot = telebot.TeleBot(conf.TOKEN, threaded=False)


# In[6]:

dict_data = {}


# In[7]:

dict_mass = {}
def remember(id_user):
    if id_user in dict_mass:
        return dict_mass[id_user]
    else:
        dict_mass[id_user] = []
        return dict_mass[id_user]


# In[8]:

def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


# In[9]:

def languages():
    lang_list = []
    for every in dict_data:
        lang_list.append(dict_data[every][0])
    lang_dict = {}
    for i in lang_list:
        if i not in lang_dict:
            lang_dict[i] = [i]
        else:
            lang_dict[i].append(i)
    for lang in lang_dict:
        lang_dict[lang] = len(lang_dict[lang])
    return lang_dict


# In[10]:

def cleaning(answer):
    answer = answer.lower()
    return answer


# In[11]:

import copy
def file_str():
    questions = questions_list()
    dict_data_file = copy.deepcopy(dict_data)
    for us in dict_data_file:
        for p in range(0,88):
            if p not in dict_data_file[us]:
                dict_data_file[us][p] = ''
    main_str = 'id\t'
    for x in questions:
        main_str = main_str + x + '\t'
    main_str = main_str + '\n'
    for user in dict_data_file:
        user_string = str(user) + '\t'
        for j in sorted(dict_data_file[user].keys()):
            user_string = user_string + dict_data_file[user][j] + '\t'
        main_str = main_str + user_string + '\n'
    return main_str


# In[12]:

@bot.message_handler(commands=['fileget'])
def file_create(message):
    string = file_str()
    with open('/home/panteleeva/mysite/results.tsv', 'w', encoding='utf-8') as results:
        results.write(string)
    doc = open('/home/panteleeva/mysite/results.tsv', 'rb')
    bot.send_document(message.chat.id, doc)
    mass = remember(message.chat.id)
    if len(mass) != 0 and len(dict_data) != 0 and dict_data[message.chat.id][mass[-1]] == '':
        bot.send_message(message.chat.id, dict_r_rev[mass[-1]])
    elif len(mass) == 0 and len(dict_data) != 0:
        bot.send_message(message.chat.id, dict_r_rev[0])


# In[13]:

@bot.message_handler(commands=['info'])#если пользователь уже ответил на какие-то вопросы, то значит он принял участие
def inform(message):
    lang_dict = languages()
    string = ''
    mass = remember(message.chat.id)
    for one in lang_dict:
        if lang_dict[one] == 1:
            string = string + one + ': ' + str(lang_dict[one]) + ' person' + '\r\n'
        else:
            string = string + one + ': ' + str(lang_dict[one]) + ' people' + '\r\n'
    if len(dict_data) == 0:
        bot.send_message(message.chat.id, "You are the first person who is taking part in this research! Call the command /begin to start.")
    elif dict_data[message.chat.id][0] == '':
        bot.send_message(message.chat.id, "You are the first person who is taking part in this research!")
    elif len(dict_data) == 1 and dict_data[message.chat.id][0] != '':
        bot.send_message(message.chat.id, "Only 1 person took part in this research. His language is {}. Call the command /fileget to get the file with all answers.".format(get_key(lang_dict, 1)))
    else:
        bot.send_message(message.chat.id, "{} people took part in this research. Their languages are:\r\n{}\r\nCall the command /fileget to get the file with all answers.".format(len(dict_data),string))
    if len(mass) != 0 and len(dict_data) != 0 and dict_data[message.chat.id][mass[-1]] == '':
        bot.send_message(message.chat.id, dict_r_rev[mass[-1]])
    elif len(mass) == 0 and len(dict_data) != 0:
        bot.send_message(message.chat.id, dict_r_rev[0])


# In[14]:

@bot.message_handler(commands=['start'])# этот обработчик запускает функцию send_welcome, когда пользователь отправляет команду /help
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello! This bot asks you about the color terms in your native language. Please answer the questions.\r\nIf you need help, call the command /help.\r\nIf you need overall information, call the command /info.")
    if message.chat.id in dict_data:
        bot.send_message(message.chat.id, "You cannot fill in the form once again. Your answers were written down.")
    else:
        bot.send_message(message.chat.id, dict_r_rev[0])
        id_user = message.chat.id
        dict_data[id_user] = {0:''}#создается значение с новым юзером {user1:{0:'/start'}}

# In[15]:

@bot.message_handler(commands=['help'])
def help_user(message):
    bot.send_message(message.chat.id, "This bot asks you about the color terms in your native language.\r\nIf you need overall information, call the command /info.")

# In[17]:

@bot.message_handler()# этот обработчик записывает результаты
def get_answer(message):
    id_user = message.chat.id
    mass = remember(id_user)
    if len(dict_data[id_user]) != 88:
        q_num = random.choice(keys)
        while q_num in dict_data[id_user]:
            q_num = random.choice(keys)
        if q_num not in dict_data[id_user]:# если ещё нет ответа на этот вопрос, то спрашивает #3#2#4
            mass.append(q_num)#добавляем в массив номер вопроса [3]#[3,2]#[3,2,4]
            bot.send_message(message.chat.id, "{}/88. {}".format(len(mass),dict_r_rev[q_num]))
            if q_num == 2:
                photo = open('/home/panteleeva/mysite/2.jpeg', 'rb')
                bot.send_photo(id_user, photo)
            if q_num == 11:
                photo = open('/home/panteleeva/mysite/11.jpg', 'rb')
                bot.send_photo(id_user, photo)
            if q_num == 1:
                photo = open('/home/panteleeva/mysite/1.jpg', 'rb')
                bot.send_photo(id_user, photo)
            if q_num == 43:
                photo = open('/home/panteleeva/mysite/43.jpg', 'rb')
                bot.send_photo(id_user, photo)
            if q_num == 69:
                photo = open('/home/panteleeva/mysite/69.jpg', 'rb')
                bot.send_photo(id_user, photo)
            if q_num == 80:
                photo = open('/home/panteleeva/mysite/80.jpg', 'rb')
                bot.send_photo(id_user, photo)
            if q_num == 83:
                photo = open('/home/panteleeva/mysite/83.jpg', 'rb')
                bot.send_photo(id_user, photo)
            if q_num == 65:
                photo = open('/home/panteleeva/mysite/65.jpg', 'rb')
                bot.send_photo(id_user, photo)
            if q_num == 66:
                photo = open('/home/panteleeva/mysite/66.jpg', 'rb')
                bot.send_photo(id_user, photo)
            if q_num == 84:
                photo = open('/home/panteleeva/mysite/84.jpg', 'rb')
                bot.send_photo(id_user, photo)
            answer = cleaning(message.text)#ans0#ans3#squians2
            if len(dict_data[id_user]) == 1:#если пока записан только ответ на 1 вопрос
                dict_data[id_user][0] = answer#{user1:{0:'ans0'}}
                dict_data[id_user][q_num] = ''#{user1:{0:'ans0',3:'ans0'}}
            else:
                dict_data[id_user][mass[-2]] = answer#{user1:{0:'ans0',3:'ans3',2:'ans2'}}
                dict_data[id_user][q_num] = ''#{user1:{0:'ans0',3:'ans3',2:'ans2',4:''}}
        else:
            bot.send_message(message.chat.id, 'Error.')
    else:
        bot.send_message(message.chat.id, 'Thank you for your answers.')
        if dict_data[message.chat.id][mass[-1]] == '':
            ans = cleaning(message.text)
            dict_data[id_user][mass[-1]] = ans


# пустая главная страничка для проверки
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'


# обрабатываем вызовы вебхука = функция, которая запускается, когда к нам постучался телеграм
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)
