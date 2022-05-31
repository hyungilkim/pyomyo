import UdpComms as UDP
import struct
import multiprocessing

from pyomyo import Myo, emg_mode

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
	m = Myo(mode=emg_mode.RAW)
	m.connect()
	
	def add_to_queue(emg, movement):
		q.put(emg)

	m.add_emg_handler(add_to_queue)
	
	def print_battery(bat):
		print("Battery level:", bat)

	m.add_battery_handler(print_battery)

	 # Orange logo and bar LEDs
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

IP = "127.0.0.1"
portTX = 8000
portRX = 8001

sock = UDP.UdpComms(IP, portTX, portRX, enableRX=True, suppressWarnings=True)

# -------- Main Program Loop -----------
if __name__ == "__main__":
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	try:
		while True:
			# Get the emg data and plot it
			while not(q.empty()):
				emg = list(q.get())
				bytes = struct.pack('>8i', *emg)
				sock.SendData(bytes)
				print(emg)
				# print(bytes)

	except KeyboardInterrupt:
		print("Quitting")
		quit()