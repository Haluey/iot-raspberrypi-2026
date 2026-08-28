from gpiozero import PWMOutputDevice
from time import sleep

# GPIO핀 설정
buzzer = PWMOutputDevice(21)

# 음계 정의
notes = {
	"도": 261.63, "레": 293.66,
	"미": 329.63, "파": 349.23,
	"솔": 392.00, "라": 440.00,
	"시": 493.88, "도": 523.25
}

# 도레미파솔라시도
scale = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]

# 나비야 곡
melody = [
	"솔", "미", "미", "파", "레", "레", "도", "미", "미", "파", "솔", "솔", "솔",
	"솔", "미", "미", "파", "레", "레", "도", "미", "솔", "솔", "미", "미", "미",
	"레", "레", "레", "레", "미", "파", "미", "미", "미", "미", "파", "솔",
	"솔", "미", "미", "파", "레", "레", "도", "미", "솔", "솔", "미", "미", "미"
]

try:
	for note in melody:
		freq = notes[note]
		buzzer.frequency = freq
		buzzer.value = 0.5	# duty cycle (소리 크기)
		sleep(0.5)

		buzzer.off()
		sleep(0.1)

finally:
	buzzer.close()
