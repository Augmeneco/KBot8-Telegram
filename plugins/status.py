from plugins.utils import *
import psutil

class status:
	level = 1
	names = ['стат','статус','stat','status']

	def execute(self,msg):
		text = '[ Статистика ]\nСистема:\n&#8195;Процессор:\n'
		for idx, cpu in enumerate(psutil.cpu_percent(interval=1, percpu=True)):
			text += '&#8195;&#8195;Ядро №'+str(idx+1)+': '+str(cpu)+'%\n'
		mem = psutil.virtual_memory()
		MB = 1024 * 1024

		text += '&#8195;ОЗУ:\n&#8195;&#8195;Всего: '+str(int(mem.total / MB))+'MB\n'
		text += '&#8195;&#8195;Использовано: '+str(int((mem.total - mem.available) / MB))+'MB\n'
		text += '&#8195;&#8195;Свободно: '+str(int(mem.available / MB))+'MB\n'
		text += '&#8195;&#8195;Использовано ботом: '+str(int(psutil.Process().memory_info().rss / MB))+'MB\n'

		end_time = time.monotonic()

		text += 'Бот:\n&#8195;&#8195;Время работы: '+str(datetime.timedelta(seconds=end_time - registry.data['start_time']))+'\n'
		text += '&#8195;&#8195;Обращений: '+str(registry.data['bot_uses'])

		msg.sendMessage(text)

commands.register(status)