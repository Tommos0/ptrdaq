import socket
BUFFER_SIZE = 1024
TCP_IP = '192.168.3.2'
TCP_PORT = 9999

def sendmsg(msg):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.send(msg)
        data = s.recv(BUFFER_SIZE)
        s.close()
        if (data=="ok"):
            return True
        else:
            return False
    except:
        return False

def test():
    return sendmsg("test")
def on():
    return sendmsg("on")
def off():
    return sendmsg("off")
