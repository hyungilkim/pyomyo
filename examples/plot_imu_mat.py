import multiprocessing
import queue
import numpy as np
import mpl_toolkits.mplot3d as plt3d
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.cm import get_cmap

from pyomyo import Myo, emg_mode

print("Press ctrl+pause/break to stop")

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
	m = Myo(mode=emg_mode.FILTERED)
	m.connect()

	def add_to_queue(quat, acc, gyro):
		imu_data = acc + gyro
		q.put(imu_data)

	m.add_imu_handler(add_to_queue)
	
	# Purple logo and bar LEDs
	m.set_leds([128, 0, 128], [128, 0, 128])
	# Vibrate to know we connected okay
	m.vibrate(1)

	"""worker function"""
	while True:
		try:
			m.run()
		except:
			print("Worker Stopped")
			quit()

# ------------ Plot Setup ---------------
QUEUE_SIZE = 200
SENSORS = 6
subplots = []
lines = []
# Set the size of the plot
plt.rcParams["figure.figsize"] = (16,8)
# using the variable axs for multiple Axes
fig, subplots = plt.subplots(SENSORS, 1)
fig.canvas.manager.set_window_title("IMU plot (3DOF acc + 3DOF gyro)")
fig.tight_layout()
# Set each line to a different color

name = "tab10" # Change this if you have sensors > 10
cmap = get_cmap(name)  # type: matplotlib.colors.ListedColormap
colors = cmap.colors  # type: list

for i in range(0,SENSORS):
	ch_line,  = subplots[i].plot(range(QUEUE_SIZE),[0]*(QUEUE_SIZE), color=colors[i])
	lines.append(ch_line)

subplots[0].set_ylabel('acc_x')
subplots[0].set_ylabel('acc_y')
subplots[0].set_ylabel('acc_z')

imu_queue = queue.Queue(QUEUE_SIZE)

def animate(i):
	# Myo Plot
	while not(q.empty()):
		myox = list(q.get())
		if (imu_queue.full()):
			imu_queue.get()
		imu_queue.put(myox)

	channels = np.array(imu_queue.queue)

	if (imu_queue.full()):
		for i in range(0,SENSORS):
			channel = channels[:,i]
			lines[i].set_ydata(channel)
			subplots[i].set_ylim(min(-1024,min(channel)),max(1024,max(channel)))
			

if __name__ == '__main__':
	# Start Myo Process
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	while(q.empty()):
		# Wait until we actually get data
		continue
	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
	def on_close(event):
		p.terminate()
		raise KeyboardInterrupt
		print("On close has ran")
	fig.canvas.mpl_connect('close_event', on_close)

	try:
		plt.show()
	except KeyboardInterrupt:
		plt.close()
		p.close()
		quit()