from plugins.utils import *
import time

def t_con(msg):
    msg.sendMessage('ТАЙМЕР #'+str(msg.data['id']))

class test:
    names = ['тест','test']
    level = 1
    def execute(self,msg):
        Events.add(msg,'timer','t_con',{"timer":time.time()+10})


contexts.register('t_con',t_con)
commands.register(test)