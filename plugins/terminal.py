import subprocess
from plugins.utils import *

class terminal:
    level = 256
    names = ['терм','term']
    def execute(self, msg):
        cmd = msg.user_text.replace('—','--').split('<br>')
        with open('/tmp/cmd.sh', 'w') as cl:
            for i in range(len(cmd)):
                cl.write(cmd[i]+'\n')
        shell = subprocess.getoutput('chmod 755 /tmp/cmd.sh;bash /tmp/cmd.sh')
        msg.sendMessage(shell)

#commands.register(terminal)