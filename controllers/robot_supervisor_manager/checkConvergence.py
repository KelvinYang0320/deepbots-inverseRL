import matplotlib.pyplot as plt
import numpy as np
def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

fp=open("Episode-score.txt", "r")
lines = fp.read().splitlines()
scores = list(map(float, lines))
episode = list(range(1, 1+len(scores)))
print(scores)
print(episode)
	
plt.figure()
plt.title("Episode scores over episode")
plt.plot(episode, scores, label='Raw data')
SMA = moving_average(scores, 500)
plt.plot(SMA, label='SMA500')
plt.xlabel("episode")
plt.ylabel("episode score")

plt.legend()
plt.savefig('trend.png')
print("Last SMA500:",np.mean(scores[-500:]))
