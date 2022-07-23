import telegram
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
 
token = "5428220063:AAG2T1SxO2rCRVkbA2-EDG9ZOAVfUkFFQDU"
id = "5472701536"
 
bot = telegram.Bot(token)
# bot.sendMessage(chat_id=id, text="테스트 중입니다.")

def sendTelegram(_text):
    bot.sendMessage(chat_id=id, text=_text)
 
# updater
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
updater.start_polling()
 
# 사용자가 보낸 메세지를 읽어들이고, 답장을 보내줍니다.
def handler(update, context):
    user_text = update.message.text # 사용자가 보낸 메세지를 user_text 변수에 저장합니다.
    if user_text == "안녕": 
        bot.send_message(chat_id=id, text="어 그래 안녕") 
    elif user_text == "뭐해": 
        bot.send_message(chat_id=id, text="그냥 있어") 
    elif user_text == "1": 
        bot.send_message(chat_id=id, text="3") 
    elif user_text == "그림": 
        bot.send_photo(chat_id = id, photo=open('./image/test.jpg', 'rb'))
 
echo_handler = MessageHandler(Filters.text, handler)
dispatcher.add_handler(echo_handler)
