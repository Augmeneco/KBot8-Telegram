import requests, re
from plugins.utils import *
from bs4 import BeautifulSoup as bs

class google_img:
    level = 1
    names = ['g','г','гугл','фото','гы']
    
    def execute(self, msg):
        if msg.user_text == '':
            msg.sendMessage('Ты забыл указать что именно искать')
            return
        google_url = 'https://www.google.ru/search?tbm=isch&q='+msg.user_text
        user_agent = {'User-Agent':'LG8700/1.0 UP.Browser/6.2.3.9 (GUI) MMP/2.0'}

        index = bs(requests.get(
            google_url,
            headers = user_agent
        ).text,'html.parser')
        
        imgs = index.body.contents[2].contents[0].contents[0]
        imgs = [
            re.findall('imgurl=(.+)&imgrefurl',i.a['href'])[0] for i in imgs.contents
        ]

        out = []
        count = 0
        for img in imgs:
            try:
                if check_image_tg(img):
                    out.append(
                        telegram.InputMediaPhotoUrl().setUrl(img)
                    )
            except:
                pass
            count += 1
            if count == 11: break
            

        msg.sendMediaGroup(out)

commands.register(google_img)