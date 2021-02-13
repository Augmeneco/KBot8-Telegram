import random, requests, re
from bs4 import BeautifulSoup as bs
from plugins.utils import *

class bash:
	level = 1
	names = ['баш','bash']
	def execute(self, msg):
		max = int(re.findall('"index" value="(\d*)" auto',requests.get('https://bash.im/').text)[0])
		randnum = str(random.randint(1,max)) 
		index = requests.get('https://bash.im/index/'+randnum).text 
		index = bs(index,'html.parser')
		index = index.find_all('div',"quote__body")
		index = random.choice(index)
		text = str(index)
		#index = [str(i) for i in index.contents]
		#text = '\n'.join(index).replace('<br/>','\n').replace('\n      ','')
		text = text.replace('<br/>','\n')
		for clear in ['&lt;','&gt;','<div class="quote__body">','</div>']:
			text = text.replace(clear,'')
		msg.sendMessage(text)

commands.register(bash)