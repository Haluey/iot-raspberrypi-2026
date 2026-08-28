from gpiozero import Buzzer
from time import sleep

# GPIO 21번 핀에 부저의 +극을 연결한 경우
buzzer = Buzzer(21)

while True:
	buzzer.on()
	print("Buzzer on")
	sleep(1)

	buzzer.off()
	print("Buzzer off")
	sleep(1)
