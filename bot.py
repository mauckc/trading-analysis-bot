import os,psycopg2

import telegram
from telegram import ParseMode
from telegram.ext import Updater,CommandHandler,MessageHandler,Filters

from binance.client import Client

import infolib,tradelib,indexlib,misclib

TOKEN=os.environ['TELEGRAM_TOKEN']

SECRET_KEY=os.environ['SECRET_KEY']
API_KEY=os.environ['API_KEY']
client=Client(API_KEY,SECRET_KEY)

DB_NAME=os.environ['DB_NAME']
DB_USERNAME=os.environ['DB_USERNAME']
DB_HOST=os.environ['DB_HOST']
DB_PASSWORD=os.environ['DB_PASSWORD']
DB_URL="dbname='"+DB_NAME+"' user='"+DB_USERNAME+"' host='"+DB_HOST+"' password='"+DB_PASSWORD+"'"

conn=psycopg2.connect(DB_URL)
cur=conn.cursor()
cur.execute("SELECT user_name FROM customers")
customers=cur.fetchall()
user_list=[customer[0] for customer in customers]
cur.execute("SELECT chat_id FROM users")
users=cur.fetchall()
id_list=[chat_id[0] for chat_id in users]
cur.close()
conn.close()

ADMIN_ID=378003568
ADMIN_USERNAME='tjeuly'

def admin(bot,update,args):
    if str(update.message.from_user.username)==ADMIN_USERNAME:
        opt=args[0]
        global user_list
        if opt=='update_user':
            conn=psycopg2.connect(DB_URL)
            cur=conn.cursor()
            cur.execute("SELECT user_name FROM customers")
            customers=cur.fetchall()
            user_list=[customer[0] for customer in customers]
            cur.close()
            conn.close()
            bot.send_message(chat_id=update.message.chat_id,text="Updated users list: "+", ".join(user_list))
        if opt=='add_user':
            conn=psycopg2.connect(DB_URL)
            cur=conn.cursor()
            for user_name in args[1:]:
                db_cmd="INSERT INTO customers (user_name) VALUES ('"+user_name+"')"
                cur.execute(db_cmd)
            conn.commit()
            cur.execute("SELECT user_name FROM customers")
            customers=cur.fetchall()
            user_list=[customer[0] for customer in customers]
            cur.close()
            conn.close()
            bot.send_message(chat_id=update.message.chat_id,text="Users list: "+", ".join(user_list))
        if opt=='del_user':
            conn=psycopg2.connect(DB_URL)
            cur=conn.cursor()
            for user_name in args[1:]:
                db_cmd="DELETE FROM customers WHERE user_name = '"+user_name+"'"
                cur.execute(db_cmd)
            conn.commit()
            cur.execute("SELECT user_name FROM customers")
            customers=cur.fetchall()
            user_list=[customer[0] for customer in customers]
            cur.close()
            conn.close()
            bot.send_message(chat_id=update.message.chat_id,text="Users list: "+", ".join(user_list))
        if opt=='view_user':
            bot.send_message(chat_id=update.message.chat_id,text="Users list: "+", ".join(user_list))
        if opt=='update_id':
            conn=psycopg2.connect(DB_URL)
            cur=conn.cursor()
            cur.execute("SELECT chat_id FROM users")
            users=cur.fetchall()
            id_list_old=[chat_id[0] for chat_id in users]
            new_id_list=list(set(id_list)-set(id_list_old))
            for new_id in new_id_list:
                db_cmd="INSERT INTO users (chat_id) VALUES ('"+str(new_id)+"')"
                cur.execute(db_cmd)
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(chat_id=update.message.chat_id,text="ID list: "+str(id_list))
        if opt=='view_id':
            bot.send_message(chat_id=update.message.chat_id,text="ID list: "+str(id_list))
            
def send_msg(bot,update):
    msg=update.message.text
    if msg[0:10]=='/send_msg ':
        msg=msg[10:]
        for id_item in id_list:
            bot.send_message(chat_id=id_item,text=msg,parse_mode=ParseMode.MARKDOWN)

def a(bot,update,args):
    bot.send_chat_action(chat_id=update.message.chat_id,action=telegram.ChatAction.TYPING)
    if args[-1] in ['500','1000','1500','2000','2500','5000','7500','10000','12500','15000','17500','20000','25000','30000','35000','40000','45000','50000']:
        num_trades=int(args[-1])
        coin_list=args[:-1]
    else:
        num_trades=5000
        coin_list=args
    for coinName in coin_list:
        market=infolib.getMarket(coinName)
        tradelib.trade_msg(client,market,num_trades)
        bot.send_photo(chat_id=update.message.chat_id, photo=open(str(market)+'.png', 'rb'))
        tradelib.trade_msg_m30(client,market,num_trades)
        bot.send_photo(chat_id=update.message.chat_id, photo=open(str(market)+'.png', 'rb'))
        if str(update.message.from_user.username)!=ADMIN_USERNAME:
            bot.sendMessage(ADMIN_ID,'chat_id: '+str(update.message.chat_id)+' username: @'+str(update.message.from_user.username)+' market: /'+str(market))
         
def ic(bot,update):
    bot.send_chat_action(chat_id=update.message.chat_id,action=telegram.ChatAction.TYPING)
    indexlib.crix_index(client)
    bot.send_photo(chat_id=update.message.chat_id, photo=open('crix.png', 'rb'))
    if str(update.message.from_user.username)!=ADMIN_USERNAME:
        bot.sendMessage(ADMIN_ID,'chat_id: '+str(update.message.chat_id)+' username: @'+str(update.message.from_user.username)+' cmd: crix')
            
def h(bot,update):
    if str(update.message.from_user.username) in user_list:
        bot.send_chat_action(chat_id=update.message.chat_id,action=telegram.ChatAction.TYPING)
        misclib.trading_sessions(client)
        bot.send_photo(chat_id=update.message.chat_id, photo=open('trading-sessions.png', 'rb'))
        if str(update.message.from_user.username)!=ADMIN_USERNAME:
            bot.sendMessage(ADMIN_ID,'chat_id: '+str(update.message.chat_id)+' username: @'+str(update.message.from_user.username)+' cmd: h')
                
def manual(bot,update):
    global id_list
    if update.message.chat_id not in id_list:
        id_list.append(update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id,text="@Trading\_Analysis\_Bot provides technical and empirical analysis for crypto-trading on Binance exchange, developed by @tjeuly and published at https://trading-analysis-bot.herokuapp.com.\n*Features*\n- Standard technical indicators.\n- Order flow.\n- Market indexes.\n- Customized notifications.\n*Commands*\n- /a <coin1> <market2> <coin3> <number-of-recent-trades> - Transactions volume versus price statistics. Examples: /a qtumusdt hot bcn or /a hot npxs btcusdt 20000.\n- /ic - Market index CRIX.\n- /h - Trading sesions.\n*Supports*\nIf you don't have a crypto-trading account yet please use the these links to register to [Binance](https://www.binance.com/?ref=13339920) or [Huobi](https://www.huobi.br.com/en-us/topic/invited/?invite_code=x93k3).\nIn case you want to give me a coffee:\n- BTC: 1DrEMhMP5rAytKyKXRzc6szTcUX8bZzZgq\n- ETH: 0x3915D216f9Fc6ec08f956555e84385513dE5f214\n- LTC: LX8GJkGTZFmAA7puCyVp48333iQdCN6vca",parse_mode=ParseMode.MARKDOWN,disable_web_page_preview=True)
    if str(update.message.from_user.username)!=ADMIN_USERNAME:
        bot.sendMessage(ADMIN_ID,'chat_id: '+str(update.message.chat_id)+' username: @'+str(update.message.from_user.username))

def main():
    updater=Updater(TOKEN)
    dp=updater.dispatcher
    dp.add_handler(CommandHandler("start",manual))
    dp.add_handler(CommandHandler("help",manual))
    dp.add_handler(CommandHandler("a",a,pass_args=True))
    dp.add_handler(CommandHandler("ic",ic))
    dp.add_handler(CommandHandler("h",h))
    dp.add_handler(CommandHandler("admin",admin,pass_args=True))
    dp.add_handler(MessageHandler(Filters.text,send_msg))
    dp.add_handler(MessageHandler(Filters.command,send_msg))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()