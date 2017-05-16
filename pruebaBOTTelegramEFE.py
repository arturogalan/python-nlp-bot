import sys,os
import chardet
import csv
import codecs  # Know your encoding
import re
from collections import Counter
from nltk.stem.snowball import SpanishStemmer
from collections import defaultdict
from math import log
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction import DictVectorizer
import unicodedata, string
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters

model_vect = DictVectorizer()
stemmer = SpanishStemmer()
news_file_csv = os.getcwd() + '/news_from_agencies.csv'

STOPWORDS = set('''
a al algo algunas algunos ante antes como con contra cual cuando de del desde donde durante e el ella ellas ellos
en entre era erais eran eras eres es esa esas ese eso esos esta estaba estabais estaban estabas estad estada estadas
estado estados estamos estando estar estaremos estara estaran estaras estare estareis estaria estariais estariamos
estarian estarias estas este estemos esto estos estoy estuve estuviera estuvierais estuvieran estuvieras estuvieron
estuviese estuvieseis estuviesen estuvieses estuvimos estuviste estuvisteis estuvieramos estuviesemos estuvo esta
estabamos estais estan estas este esteis esten estes fue fuera fuerais fueran fueras fueron fuese fueseis fuesen fueses
fui fuimos fuiste fuisteis fueramos fuesemos ha habida habidas habido habidos habiendo habremos habra habran habras
habre habreis habria habriais habriamos habrian habrias habeis habia habiais habiamos habian habias han has hasta
hay haya hayamos hayan hayas hayais he hemos hube hubiera hubierais hubieran hubieras hubieron hubiese hubieseis
hubiesen hubieses hubimos hubiste hubisteis hubieramos hubiesemos hubo la las le les lo los me mi mis mucho muchos
muy mas mi mia mias mio mios nada ni no nos nosotras nosotros nuestra nuestras nuestro nuestros o os otra otras otro
otros para pero poco por porque que quien quienes que se sea seamos sean seas sentid sentida sentidas sentido sentidos
seremos sera seran seras sere sereis seria seriais seriamos serian serias seais siente sin sintiendo sobre sois somos
son soy su sus suya suyas suyo suyos si tambien tanto te tendremos tendra tendran tendras tendre tendreis tendria
tendriais tendriamos tendrian tendrias tened tenemos tenga tengamos tengan tengas tengo tengais tenida tenidas tenido
tenidos teniendo teneis tenia teniais teniamos tenian tenias ti tiene tienen tienes todo todos tu tus tuve tuviera
tuvierais tuvieran tuvieras tuvieron tuviese tuvieseis tuviesen tuvieses tuvimos tuviste tuvisteis tuvieramos tuviesemos
tuvo tuya tuyas tuyo tuyos tu un una uno unos vosostras vosostros vuestra vuestras vuestro vuestros y ya yo el eramos
'''.split())

def clean(x):
   x = unicodedata.normalize('NFKD', x).encode('ascii','ignore').lower()
   replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
   x = x.translate(replace_punctuation)
   x = re.sub('@%$&[\n/:!,;)()_?¿¡<>]', ' ', x)
   x = re.sub(' - ', ' ', x)
   x = re.sub(' +',' ', x).strip()
   return x

def get_keywords(words):
    '''Return the top10 frequent words.
    '''
    return [
        x for x,_ in 
        sorted(
            Counter(words).iteritems(),
            key=lambda (_,freq):freq,
            reverse=True
        )
    ][:10]



def txt2words4(txt):
        
    txt = ''.join([
        letter for letter in txt 
        if letter in set(u'abcdefghijklmnñopqrstuvwxyz0123456789 ')]
    )
    words = [
        stemmer.stem(w)
        for w in txt.split(' ')
        if w!='' and w not in STOPWORDS
    ]
    return words

headers = []
documents = []

with open(news_file_csv, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:            
        row['text'] = clean(unicode(row['text'], 'utf-8'))
        documents.append(row)

for document in documents:
    document['keywords'] = get_keywords(txt2words4(document['text']))

docs_vect = model_vect.fit_transform([Counter(doc['keywords']) for doc in documents])
    
def query_vect(text):
    doc = model_vect.transform(Counter(txt2words4(text)))
    similarities = cosine_similarity(doc, docs_vect)
    doc_id,score = similarities.argmax(), similarities.max()    
    #print doc_id
    #print score
    return doc_id

print 'Dataset configurado....'


#textQuery='Trump'
#print documents[query_vect(textQuery)]['href']
#print documents[query_vect(textQuery)]['keywords']  


def start(bot, update):
    update.message.reply_text('Hello World!')

def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))

def echo(bot, update):
    textQuery=update.message.text
    hrefText=documents[query_vect(textQuery)]['href']
    print hrefText
    bot.sendMessage(chat_id=update.message.chat_id, text=hrefText)
#    bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)

    
    
updater = Updater('334282521:AAEw55DqIqY5KuxjEErmkqMuyV_83n0nGoI')

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', hello))
echo_handler = MessageHandler(Filters.text, echo)
updater.dispatcher.add_handler(echo_handler)

updater.start_polling()
updater.idle()

print 'Bender escuchando....'
