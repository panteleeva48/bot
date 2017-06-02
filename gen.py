import flask
import telebot
import conf
import re
import random
from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)

bot = telebot.TeleBot(conf.TOKEN, threaded=False)

bot.remove_webhook()

bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

morph = MorphAnalyzer()
m = Mystem()

def file(name):
    f = open(name, 'r', encoding = 'utf-8')
    fr = f.read()
    f.close()
    return fr

def writefile(namefile,result):
    file = open(namefile, "w", encoding = "utf-8")
    file.write(result)
    file.close()

def list_words():# делает словарь из частей речи и лемм
    w = file('/home/panteleeva/mysite/words.txt')
    w = re.sub('[0-9]','',w)
    w = re.sub('\t','',w)
    w = re.sub('[A-Za-z]','',w)
    list_w = w.split('\n')
    list_l_pos = []
    for w in list_w:
        ana = morph.parse(w)
        first = ana[0]
        lemma = first.normal_form
        pos = first.tag.POS
        gen = first.tag.gender
        if pos == 'NOUN':
            pos = gen
        list_l_pos.append((lemma,pos))
    d = {}
    for el in list_l_pos:
        if el[1] not in d:
            d[el[1]] = [el[0]]
        else:
            d[el[1]].append(el[0])
    for key in d:
        d[key] = set(d[key])#чтобы не было повторений при добавлении
    return d

d = list_words()
for j in d:
    d[j] = list(d[j])

def razbor_omon(message):#разбор введенного предложения
    lemmas = m.lemmatize(message)
    analy = m.analyze(message)
    forms = []
    for word in analy:
            form = word['text']
            forms.append(form)
    mass_l_f = []
    for x in range(len(lemmas)):
        l_f = (lemmas[x],forms[x])
        mass_l_f.append(l_f)
    #print(mass_l_f)
    info = []
    for element in mass_l_f:#чтобы была снята омонимия, сравниваю с показателями mystem, если вообще никакой разбор не подошёл, то беру 1
        ana_p = morph.parse(element[1])
        for k in range(len(ana_p)):
            if element[0] in str(ana_p[k]):
                razbor = ana_p[k]
                break
            else:
                razbor = ana_p[0]
        info.append(razbor)
    return info

def noun(new_gr_min,one,prog,case,num):#если есть все, то меняет, если нет - то возращает введенное слово
    if case == None or num == None:
        res = one.word
    else:
        res = prog.inflect({case, num})
    return res

def grnd(new_gr_min,one,prog,pos_s,time):#если есть все, то меняет, если нет - то возращает введенное слово
    if pos_s == None or time == None:
        res = one.word
    else:
        res = prog.inflect({pos_s, time})
    return res

def adj(new_gr_min,one,prog,case,num,gender):#если есть все, то меняет, если нет - то возращает введенное слово
    if case == None or num == None or gender == None:
        res = one.word
    else:
        res = prog.inflect({case, num, gender})
    return res

def verb(new_gr_min,one,prog,time,gender,num,mood,per):
    if time == 'past':
        if gender == None:
            res = prog.inflect({time, num, mood})
        else:
            res = prog.inflect({time, gender, num, mood})
    else:
        if time == None or num == None or per == None or mood == None:
            res = one.word
        else:
            res = prog.inflect({time, num, per, mood})
    return res

def prtf(new_gr_min,one,prog,case,num,gender,time,voice):
    if case == None or num == None or gender == None or time == None or voice == None:
        res = one.word
    else:
        res = prog.inflect({case, num, gender, time, voice})
    return res

def adjs(new_gr_min,one,prog,num,gender,pos_s):#если есть все, то меняет, если нет - то возращает введенное слово
    if pos_s == None or num == None or gender == None:
        res = one.word
    else:
        res = prog.inflect({num, gender,pos_s})
    return res

def prts(new_gr_min,one,prog,pos_s,num,gender,time,voice):
    if pos_s == None or num == None or gender == None or time == None or voice == None:
        res = one.word
    else:
        res = prog.inflect({pos_s, gender, num, time, voice})
    return res

def numer(new_gr_min,one,prog,case):
    if case == None:
        res = one.word
    else:
        res = prog.inflect({case})
    return res

def pred(new_gr_min,one,prog,time):
    if time == None:
        res = one.word
    else:
        res = prog.inflect({time})
    return res

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Здравствуйте! Это бот, который генерирует похожие предложения. Напишите любое предложение.")

@bot.message_handler(func=lambda m: True)
def send_len(message):
    morph = MorphAnalyzer()
    info = razbor_omon(message.text)
    alll = ''
    for one in info:
        pos_s = one.tag.POS
        gend = one.tag.gender
        spec = one.tag.POS
        if pos_s != None:
            if  str(pos_s) == 'CONJ' or str(pos_s) == 'PREP' or str(pos_s) == 'NPRO':
                new_1 = one.word
            else:
                if spec == 'NOUN':
                    spec = gend
                new_1 = random.choice(d[str(spec)])
        else:
            new_1 = one.word
        prog = morph.parse(new_1)[0]
        case = one.tag.case          # падеж
        gender = one.tag.gender        # род (мужской, женский, средний)
        mood = one.tag.mood          # наклонение (повелительное, изъявительное)
        num = one.tag.number        # число (единственное, множественное)
        per = one.tag.person        # лицо (1, 2, 3)
        time = one.tag.tense         # время (настоящее, прошедшее, будущее)
        voice = one.tag.voice         # залог (действительный, страдательный)
        new_gr = [new_1, pos_s, case,gender,mood,num,per,time,voice]
        new_gr_min = []
        for n in new_gr:
            if n != None:
                new_gr_min.append(n)
        if len(new_gr_min) >= 2:
            if new_gr_min[1] == 'NOUN':
                res = noun(new_gr_min,one,prog,case,num)
            elif new_gr_min[1] == 'GRND':
                res = grnd(new_gr_min,one,prog,pos_s,time)
            elif new_gr_min[1] == 'ADVB':
                res = new_gr_min[0]
            elif new_gr_min[1] == 'ADJF':
                res = adj(new_gr_min,one,prog,case,num,gender)
            elif new_gr_min[1] == 'VERB':
                res = verb(new_gr_min,one,prog,time,gender,num,mood,per)
            elif new_gr_min[1] == 'PRTF':
                res = prtf(new_gr_min,one,prog,case,num,gender,time,voice)
            elif new_gr_min[1] == 'ADJS':
                res = adjs(new_gr_min,one,prog,num,gender,pos_s)
            elif new_gr_min[1] == 'COMP' or new_gr_min[1] == 'INFN' or new_gr_min[1] == 'PRCL' or new_gr_min[1] == 'INTJ':
                res = prog.inflect({pos_s})
            elif new_gr_min[1] == 'PRTS':
                res = prts(new_gr_min,one,prog,pos_s,num,gender,time,voice)
            elif new_gr_min[1] == 'NUMR':
                res = numer(new_gr_min,one,prog,case)
            elif new_gr_min[1] == 'PRED':
                res = pred(new_gr_min,one,prog,time)
            else:
                res = one.word
        else:
            res = new_gr_min[0]
        if res == None:
            res = one.word
        if type(res) != str:
            res = res.word
        alll = alll + res
    alll = alll.capitalize()
    bot.send_message(message.chat.id, '{}'.format(alll))

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)
