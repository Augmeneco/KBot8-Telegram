import requests, json

class InputMediaPhotoUrl:
    url = None
    
    def setUrl(self,url):
        self.url = url
        return self
    
class InputMediaPhotoFile:
    data = None
    name = None

    def setData(self,data):
        self.data = data
        return self
    def setName(self,name):
        self.name = name
        return self

class Telegram:
    def __init__(self):
        self.config = json.loads(open('data/config.json','r').read())
        self.token = 'bot'+self.config['telegram_token']
        self.update_id = None

    def getUpdates(self):
        result = requests.post(
            'https://api.telegram.org/'+self.token+'/getUpdates',
            data = {'offset':self.update_id}
        ).json()['result']

        for update in result:
            self.update_id = update['update_id']+1
            if 'message' not in update: continue
            yield update['message']

    def sendMessage(self,text,chat_id):
        result = requests.post(
            'https://api.telegram.org/'+self.token+'/sendMessage',
            data = {
                'chat_id':chat_id,
                'text':text,
                'parse_mode':'HTML'
            }
        )
        return result.json()
    
    def sendVideo(self,path,chat_id):
        result = requests.post(
            'https://api.telegram.org/'+self.token+'/sendVideo',
            data = {
                'chat_id':chat_id
            },
            files={'video':open(path,'rb')}
        )

    def sendPhoto(self,media,chat_id,caption=None):
        photo = None
        inputMedia = None
        if type(media) == InputMediaPhotoFile:
            inputMedia = {'photo':('photo',media.data,'multipart/form-data')}
        if type(media) == InputMediaPhotoUrl:
            photo = media.url

        result = requests.post(
            'https://api.telegram.org/'+self.token+'/sendPhoto',
            files = inputMedia,
            data = {
                'chat_id':chat_id,
                'caption':caption,
                'photo':photo
            }
        ).json()

        return result        
        
    
    def sendMediaGroup(self,media,chat_id):
        inputMedia = []
        files = []
        
        #if len(media) == 1: 
        #    self.sendPhoto(media[0],chat_id)

        for file in media:
            if type(file) == InputMediaPhotoUrl:
                inputMedia.append({
                    'type':'photo',
                    'media':file.url
                })
            if type(file) == InputMediaPhotoFile:
                inputMedia.append({
                    'type':'photo',
                    'media':'attach://'+file.name
                })

        result = requests.post(
            'https://api.telegram.org/'+self.token+'/sendMediaGroup',
            data = {
                'chat_id':chat_id,
                'media':json.dumps(inputMedia)
            }
        ).json()
        
        return result
        
    def getFile(self,file_id):
        result = requests.post(
            'https://api.telegram.org/'+self.token+'/getFile',
            data = {
                'file_id':file_id
            }
        ).json()

        return result


telegram = Telegram()