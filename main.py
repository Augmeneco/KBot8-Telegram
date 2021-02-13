from plugins.utils import *
import plugins.handler as handler
import os, importlib, traceback

plugins = [plugin for plugin in os.listdir('plugins') if plugin not in [
    'utils.py','__pycache__','handler.py','telegram.py']
]
for plugin in plugins:
    if os.path.isfile('plugins/'+plugin):
        importlib.import_module('plugins.'+plugin.replace('.py',''))

registry.data['start_time'] = time.monotonic()
registry.data['bot_uses'] = 0

threading.Thread(target=handler.handler_thread).start()

while True:
    try:
        for update in tg.getUpdates():        
            #print(update)

            msg = Msg()
            msg.parseUpdate(update)

            if msg.need_skip: continue

            if msg.user.context == 'main': 
                cmd_info = is_cmd(msg.text)
                if not cmd_info['is_cmd']: continue
                msg.setUserText(cmd_info['text'])

                log('Executed command {} in {}'.format(cmd_info['command'],msg.chat_id))

                threading.Thread(
                    target=commands.find(cmd_info['command'])().execute,
                    args=(msg,)
                ).start()
            else:
                threading.Thread(
                    target=contexts.find(msg.user.context)['execute'],
                    args=(msg,)
                ).start()
            registry.data['bot_uses'] += 1
    except Exception as error:
        if error == KeyboardInterrupt: os._exit(0)
        print(traceback.format_exc())