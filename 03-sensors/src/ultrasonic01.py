from gpiozero import DistanceSensor
from time import sleep

sensor = DistanceSensor(echo=23, trigger=24)

try:
	while True:
		print('Distance: ', sensor.distance, 'm')
		sleep(1)

except KeyboardInterrupt:
	sensor.close()
