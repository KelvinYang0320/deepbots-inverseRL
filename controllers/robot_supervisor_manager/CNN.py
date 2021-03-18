import socket
import pickle
import numpy as np
HOST = '127.0.0.1'
PORT = 8000

reward = -1
pickle.dumps(reward)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
cnt = 0
while(1):
    print(cnt)
    cnt = cnt + 1
    client.send(pickle.dumps(reward))
    # serverMessage = str(client.recv(1024), encoding='utf-8')
    recv = client.recv(2**16)
    serverMessage = pickle.loads(recv)
    img = np.array(serverMessage)
    print(img.shape)
    # print('Observation:', serverMessage)
    print(type(serverMessage))

client.close()