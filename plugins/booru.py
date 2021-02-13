import random, requests, xmltodict, traceback, time
from plugins.utils import *

class booru:
    level = 1
    names = ['арт','хентай','art','hentai','бура','booru']
    def execute(self, msg):
        count = 10
        needtag = False
        if '-tags' in msg.user_text:
            msg.user_text = msg.user_text.replace(' -tags ','').replace(' -tags','')
            needtag = True
        if msg.user_text.split(' ')[0].isdigit():
            count = int(msg.user_text.split(' ')[0])
            if count <= 0: count = 1
            if count > 10 and msg.user.level < 2:
                msg.sendMessage('Обычный пользователь не может больше 10 артов за раз, тебе нужен второй ранг :(')
                count = 10
            query = ' '.join(msg.user_text.split(' ')[1:]).replace(' ','+')
        else:
            query = msg.user_text.replace(' ','+')
        imgs = []
        
        result = requests.get('http://0s.m5swyytpn5zhkltdn5wq.cmle.ru/index.php?page=dapi&s=post&q=index&limit=1000&tags='+query).text
        result = dict(xmltodict.parse(result))['posts']
        if 'post' not in result:
            msg.sendMessage('Ничего не найдено :(')
            return 0
        if len(result['post']) < count:
            count = len(result['post'])
        tags = '{0} мс\n({1}/{2})\nВсе теги: '
        posts = list(range(len(result['post'])))
        nums = []

        def load_img():
            i=0
            while i != count:
                if len(nums) == count: return
                randnum = random.choice(posts)
                if randnum not in nums:
                    url = result['post'][randnum]['@file_url'].replace('https://img2.gelbooru.com/','http://0s.nfwwomq.m5swyytpn5zhkltdn5wq.cmle.ru/')
                    img_stream = requests.get(url,stream=True)

                    if int(img_stream.headers['Content-Length'])/1024 > 5120: 
                        img_stream.close()
                        continue
                    if img_stream.headers['Content-Type'] not in ['image/png','image/jpeg']: 
                        img_stream.close()
                        continue
                    
                    img_stream.close()

                    if len(nums) == count: return
                    nums.append(randnum)
                    i += 1

        for _ in range(5):
            threading.Thread(target=load_img).start()
        
        while True:
            if len(nums) == count: break
            time.sleep(0.1)

        for i in nums:
            url = result['post'][i]['@file_url']
            tags += result['post'][i]['@tags']
            imgs.append(
                telegram.InputMediaPhotoUrl()
                    .setUrl(url)
            )
        timer = time.time()
        imglist = list(chunks(imgs,10))
        for imgs in imglist:
            ret = msg.sendMediaGroup(imgs)
        if needtag:
            tags = tags.format(time.time()-timer,count,len(result['post']))
            msg.sendMessage(tags)

commands.register(booru)