from gpiozero import PWMOutputDevice
from time import sleep
import readchar

# GPIO핀 설정
buzzer = PWMOutputDevice(21)

# 음계 정의
notes = {
	"C4": 261.63, "D4": 293.66,
	"E4": 329.63, "F4": 349.23,
	"G4": 392.00, "A4": 440.00,
	"B4": 493.88, "C5": 523.25
}

# 도레미파솔라시도
scale = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]

def play_note(index):
	note = scale[index]
	print(note)

	freq = notes[note]
	buzzer.frequency = freq
	buzzer.value = 0.5
	sleep(0.15)

	buzzer.off()

try:
	while True:
		key = readchar.readkey()

		if key == "q":
			break

		index = int(key) - 1
		play_note(index)

finally:
	buzzer.off()
	buzzer.close()
	print("종 료")

