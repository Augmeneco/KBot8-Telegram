import requests, os, datetime, json, threading, time, psycopg2, traceback
import plugins.telegram as telegram

config = json.loads(open('data/config.json','r').read())

db = psycopg2.connect(database='kbot')
db_cur = db.cursor()
db_cur_events = db.cursor()

db_cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER,level INTEGER,context TEXT,data TEXT)')
db_cur.execute('CREATE TABLE IF NOT EXISTS system (name TEXT,data TEXT)')
db_cur.execute('CREATE TABLE IF NOT EXISTS chats (id numeric,data TEXT,users TEXT)')
db_cur.execute('CREATE TABLE IF NOT EXISTS events (id SERIAL,user_id INTEGER,peer_id INTEGER,type TEXT,name TEXT,data TEXT)')
db.commit()

tg = telegram.Telegram()

def log(text):
    print(datetime.datetime.today().strftime("%H:%M:%S")+' | '+text)

class Events:
    def get():
        out = []
        db_cur_events.execute('SELECT * FROM events')
        raw = db_cur_events.fetchall()
        for event in raw:
            out.append(
                {
                    "id":event[0],
                    "user_id":event[1],
                    "peer_id":event[2],
                    "type":event[3],
                    "name":event[4],
                    "data":json.loads(event[5])
                }
            )
        return out

    def delete(id):
        db_cur_events.execute('DELETE FROM events WHERE id=%s',[id])
        db.commit()

    def add(msg,type_,name,data):
        db_cur_events.execute('INSERT INTO events (user_id,peer_id,type,name,data) VALUES (%s,%s,%s,%s,%s)',
            [msg.from_id,msg.chat_id,type_,name,json.dumps(data)]
        )
        db.commit()
        

class Registry:
    def __init__(self):
        self.data = {}
        db_cur.execute('SELECT * FROM system')
        data = db_cur.fetchall()
        for line in data:
            self.data[line[0]] = line[1]
    
    def save(self): #переделать говнокод
        db_cur.execute('DROP TABLE system')
        db_cur.execute('CREATE TABLE IF NOT EXISTS system (name TEXT,data TEXT)')
        for line in self.data:
            db_cur.execute(
                'INSERT INTO system VALUES (%s,%s)',
                [line,self.data[line]]
            )
        db.commit()

registry = Registry()

class Commands:
    def __init__(self):
        self.cmds = []
        self.names = []

    def find(self,name):
        for cmd in self.cmds:
            if name in cmd.names:
                return cmd
        return None
    
    def register(self,cmd_obj):
        for name in cmd_obj.names:
            self.names.append(name)
        self.cmds.append(cmd_obj)
        log('Registered plugin {}'.format(cmd_obj.names[0]))

commands = Commands()

class Contexts:
    def __init__(self):
        self.contexts = []
        self.names = []

    def find(self,name):
        if name in self.names:
            for context in self.contexts:
                if context['name'] == name:
                    return context
        return None
    
    def register(self,name,execute):
        context_obj = {'name':name,'execute':execute}
        if type(context_obj) == dict:
            self.names.append(context_obj['name'])
            self.contexts.append(context_obj)
        if type(context_obj) == list:
            for obj in context_obj:
                self.register(obj)
        log('Registered context {}'.format(context_obj['name']))

contexts = Contexts()
        
def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

class User:
    def __init__(self,user_id):
        self.id = user_id
        db_cur.execute(
            'SELECT * FROM users WHERE id=%s',
            [self.id]
        )
        self.info = db_cur.fetchone()
        self.net_user = False
        if self.info == None:
            db_cur.execute(
                'INSERT INTO users VALUES (%s,%s,%s,%s)',
                [self.id,1,'main','{}']
            )
            db.commit()
            self.data = {}
            self.level = 1
            self.context = 'main'
            self.net_user = True
        else:
            self.data = json.loads(self.info[3])
            self.context = self.info[2]
            self.level = self.info[1]

    def change_context(self,name):
        self.context = name
        self.save()

    def reload(self):
        db_cur.execute('SELECT * FROM users WHERE id=%s',[self.id])
        self.info = db_cur.fetchone()
        self.data = json.loads(self.info[3])
        self.level = self.info[1]
    def save(self):
        db_cur.execute(
            'UPDATE users SET level = %s, context = %s, data = %s WHERE id = %s',
            [self.level,self.context,json.dumps(self.data),self.id]
        )
        db.commit()

class Chat:
    def __init__(self,chat_id):
        self.id = chat_id
        self.new_chat = False
        db_cur.execute('SELECT * FROM chats WHERE id=%s',[self.id])
        data = db_cur.fetchone()
        if data == None:
            db_cur.execute(
                'INSERT INTO chats VALUES (%s,%s,%s)',
                [self.id,'{}','[]']
            )
            db.commit()
            self.data = {}
            self.users = []
            self.new_chat = True
        else:
            self.data = json.loads(data[1])
            self.users = json.loads(data[2])
    
    def add_user(self,user_id):
        if user_id not in self.users:
            self.users.append(user_id)
            self.save()
            return True
        return False
        
    def reload(self):
        db_cur.execute(
            'SELECT * FROM users WHERE id=%s',
            [self.id]
        )
        data = db_cur.fetchone()
        self.data = json.loads(data[1])
        self.users = json.loads(data[2])

    def save(self):
        db_cur.execute(
            'UPDATE chats SET data=%s, users=%s WHERE id=%s',
            [json.dumps(self.data),json.dumps(self.users),self.id]
        )
        db.commit()

def is_cmd(text):
    text_split = text.split(' ')
    if text == '': return {'is_cmd':False}
    if text_split[0] == '/':
        if len(text_split) == 1: return {'is_cmd':False}
        del text_split[0]
    '''if text[0] != '/':
        return {'is_cmd':False}'''
    if text_split[0][0] == '/':
        text_split[0] = text_split[0][1:]
    if text_split[0] in commands.names:
        cmdname = text_split[0]
        del text_split[0]
        return {'is_cmd':True,'text':' '.join(text_split),'command':cmdname}
    if text_split[0] in config['names']:
        del text_split[0]
    if len(text_split) == 0:
        return {'is_cmd':False}
    if text_split[0] in commands.names:
        return {'is_cmd':True,'text':' '.join(text_split),'command':text_split[0]}
    return {'is_cmd':False} 

def check_image_tg(url,stream=None):
    if stream == None:
        img_stream = requests.head(url)
        if int(img_stream.headers['Content-Length'])/1024 > 5120: 
            return False
        if img_stream.headers['Content-Type'] not in ['image/png','image/jpeg']: 
            return False
    else:
        img_stream = requests.get(url,stream=True)
        if int(img_stream.headers['Content-Length'])/1024 > 5120: 
            img_stream.close()
            return False
        if img_stream.headers['Content-Type'] not in ['image/png','image/jpeg']: 
            img_stream.close()
            return False

    return True

class Msg:
    text = None
    text_split = None
    chat_id = None
    from_id = None
    files = []
    user = None
    chat = None
    user_text = None
    data = None
    need_skip = True
    reply = None

    def parseUpdate(self,update):
        if 'reply_to_message' in update:
            self.parseUpdate(update['reply_to_message'])
            self.reply = Msg().parseUpdate(update['reply_to_message'])

        if 'text' in update:
            self.setText(update['text'])

        if 'photo' in update:
            self.setFiles(update['photo'])
            if 'caption' in update:
                self.setText(update['caption'])
        
        self.setChat(update['chat']['id'])
        self.setUser(update['from']['id'])

        return self

    def setText(self,text):
        self.text = text
        self.text_split = text.split(' ')
        self.need_skip = False
        return self

    def setUserText(self,user_text):
        self.user_text = user_text
        return self
    
    def setFiles(self,files):
        file_id = files[-1]['file_id']
        file_info = tg.getFile(file_id)
        self.addFile(
            'https://api.telegram.org/file/{}/{}'.format(
                tg.token,
                file_info['result']['file_path']
            )
        )

        return self
    
    def addFile(self,file):
        self.files.append(file)
        return self

    def setUser(self,user_id):
        self.user = User(user_id)
        self.from_id = user_id
        return self

    def setChat(self,chat_id):
        self.chat = Chat(chat_id)
        self.chat_id = chat_id
        return self
        
    def setData(self,data):
        self.data = data
        return self

    def sendMessage(self,text):
        return tg.sendMessage(text,self.chat_id)

    def sendMediaGroup(self,media):
        return tg.sendMediaGroup(media,self.chat_id)
    
    def sendPhoto(self,media,caption=None):
        return tg.sendPhoto(media,self.chat_id,caption=None)

class Legacy:
    def msg_gen(data):
        msg = {}
        msg['text'] = data.text
        msg['text_split'] = data.text_split
        msg['user_text'] = data.user_text
        msg['toho'] = data.chat_id
        msg['userid'] = data.from_id
        msg['userdata'] = data.user.data
        msg['userinfo'] = data.user
        msg['dialogdata'] = data.chat.data
        msg['dialoginfo'] = data.chat
        msg['config'] = config
        
        return msg
    
    def apisay(text,toho):
        return tg.sendMessage(text,toho)
