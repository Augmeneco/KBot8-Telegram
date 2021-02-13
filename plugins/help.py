from plugins.utils import *

class help:
    level = 1
    names = ['помощь','help','start','начать','команды','commands','хелп']

    def execute(self,msg):
        out = '''[ КОМАНДЫ ]

/help - эта команда
/г [запрос] - поиск в гугле по запросу
/стат - статистика бота
/resin - смола в гейшите
/бура [теги] - поиск артов по тегам в safebooru
/жмых - жмыхает фотку'''
        msg.sendMessage(out)

commands.register(help)