from gpiozero import Button, LED
import time

# 버튼 설정
color_button = Button(2)
power_button = Button(23)

# LED 설정
leds = [
	LED(17, active_high = False),
	LED(18, active_high = False),
	LED(27, active_high = False)
]

current_index = 0
is_led_on = False

def turn_off_all_leds():
	for led in leds:
		led.off()

turn_off_all_leds()

try:
	while True:
		# 색상 변경 버튼
		if color_button.is_pressed:
			print("Color Button is pressed")

			# LED가 켜져있을 때만 색상 변경
			if is_led_on:
				turn_off_all_leds()

				current_index = (current_index + 1) % len(leds)
				leds[current_index].on()

			time.sleep(0.3)	# 채터링 현상 때문에 필요

		# ON/OFF 버튼
		elif power_button.is_pressed:
			print("ON/OFF Button is pressed")

			if is_led_on:
				leds[current_index].off()
				is_led_on = False

			else:
				leds[current_index].on()
				is_led_on = True

			time.sleep(0.3)

except KeyboardInterrupt:
	turn_off_all_leds()
	print("\n exit")
