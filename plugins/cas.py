import random, requests, os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from plugins.utils import *

class cas:
    level = 1
    names = ['cas','жмых','кас']
    def execute(self, msg):
        if len(msg.files) == 0: 
            msg.sendMessage('Фото забыл приложить')
            return
        else:
            ret = requests.get(msg.files[0],stream=True).content
            img_size = Image.open(BytesIO(ret))
            size = img_size.size
            img_size.close()
            
            if len(msg.user_text.split(' ')) == 2:
                rescale = msg.user_text.split(' ')
                
                if not rescale[0].isdigit() and not rescale[1].isdigit():
                    msg.sendMessage('Аргументы должны быть числами')
                    return 0
                if int(rescale[0]) > 100 and int(rescale[1]) > 100:
                    msg.sendMessage('Нельзя больше 100')
                    return 0
                if int(rescale[0]) <= 0 and int(rescale[1]) <= 0:
                    msg.sendMessage('Нельзя меньше 0')
                    return 0
                rescale = rescale[0]+'x'+rescale[1]+'%\!'
            else:
                rescale = '50x50%\!'  
            msg.sendMessage('Жмыхаю картинку... создание шок контента может занять до 20 секунд')
            open('/tmp/'+str(msg.from_id)+'.jpg','wb').write(ret)
            os.system('convert /tmp/'+str(msg.from_id)+'.jpg  -liquid-rescale '+rescale+' /tmp/'+str(msg.from_id)+'_out.jpg')
            image_obj = Image.open('/tmp/'+str(msg.from_id)+'_out.jpg').convert('RGBA')
            imgByteArr = BytesIO()
            image_obj = image_obj.resize(size)

            image_obj.save(imgByteArr,format='PNG')

            msg.sendPhoto(
                telegram.InputMediaPhotoFile().setData(imgByteArr.getvalue()),
                caption = "Готово"
            )

            os.system('rm /tmp/'+str(msg.from_id)+'_out.jpg')
            os.system('rm /tmp/'+str(msg.from_id)+'.jpg')
            image_obj.close()

commands.register(cas)