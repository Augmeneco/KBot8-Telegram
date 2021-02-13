from plugins.utils import *
import time

def execute(msg):
    events = Events.get()

    if events:
        for event in events:

            if event['type'] == 'timer':
                if event['data']['timer'] <= time.time():
                    contexts.find(event['name'])['execute'](
                        Msg()
                            .setChat(event['peer_id'])
                            .setUser(event['user_id'])
                            .setText('')
                            .setData(event)
                    )
                    Events.delete(event['id'])

def handler_thread():
    while True:
        try:
            execute(Msg())
        except:
            print(traceback.format_exc())
        time.sleep(0.1)