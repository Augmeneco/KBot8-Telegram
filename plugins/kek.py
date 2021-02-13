from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from plugins.utils import *

class kek:
	level = 1
	names = ['кек','kek']
	def execute(self,msg):
		if len(msg.files) == 0:
			msg.sendMessage('Фото забыл приложить')
			return
		ret = requests.get(msg.files[0],stream=True).content
		
		outimgs = []
		
		image_obj = Image.open(BytesIO(ret))
		imgByteArr = BytesIO()
		image2 = image_obj.crop([0,0,int(image_obj.size[0]/2),int(image_obj.size[1])])
		image2 = image2.transpose(Image.FLIP_LEFT_RIGHT)
		image_obj.paste(image2,(int(image_obj.size[0]/2),0))
		image_obj.save(imgByteArr,format='PNG')
		outimgs.append(imgByteArr.getvalue())
	
		imgByteArr = BytesIO()
		image_obj = Image.open(BytesIO(ret))
		image2 = image_obj.transpose(Image.FLIP_LEFT_RIGHT)
		image2 = image2.crop([0,0,int(image_obj.size[0]/2),int(image_obj.size[1])])
		image2 = image2.transpose(Image.FLIP_LEFT_RIGHT)
		image_obj = image_obj.transpose(Image.FLIP_LEFT_RIGHT)
		image_obj.paste(image2,(int(image_obj.size[0]/2),0))
		image_obj.save(imgByteArr,format='PNG')
		outimgs.append(imgByteArr.getvalue())

		apisay('Готово!',msg['toho'],photo=outimgs)