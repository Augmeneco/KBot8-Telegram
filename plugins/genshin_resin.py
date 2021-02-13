from plugins.utils import *
import time, json

def timer_resin(msg):
    msg.sendMessage('Ur resin regenerates to '+str(msg.data['data']['need_count']))

class genshin_resin:
    level = 1
    names = ['resin']

    def execute(self,msg):
        if msg.user_text == 'help' or msg.user_text == '':
            msg.sendMessage(
'''/resin help - this help
/resin set [ur resin count] [minutes to next resin] [alarm at count]
/resin time - time to next resin regen'''
            )

        text_split = msg.user_text.split(' ')

        if text_split[0] == 'set':
            resin_count = int(text_split[1])
            minutes = int(text_split[2])
            need_count = int(text_split[3])  

            Events.add(msg,'timer','timer_resin',{
                'timer':time.time() + (((need_count-resin_count)*8)-(8-minutes))*60,
                'need_count':need_count
            })
            
            msg.sendMessage('Timer is set to +{:.2f} hours'.format((((need_count-resin_count)*8)-(8-minutes))/60))
        if text_split[0] == 'time':
            db_cur.execute('SELECT * FROM events WHERE user_id=%s',[msg.from_id])
            events = db_cur.fetchall()

            if events == []: 
                msg.sendMessage('U have not incoming timers')
                return
            out = 'Incoming timers:\n\n'
            i = 0
            for event in events:
                if event[3] == 'timer':
                    i += 1
                    data = json.loads(event[5])
                    out += '{}) {:.2f} minutes or {:.2f} hours\n'.format(
                        i,(data['timer'] - time.time())/60,((data['timer'] - time.time())/60)/60
                    ) 
            msg.sendMessage(out)

commands.register(genshin_resin)
contexts.register('timer_resin',timer_resin)