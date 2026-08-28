from gpiozero import Button, LED
from signal import pause
import time

# 버튼 설정
color_button = Button(2, pull_up=False, bounce_time=0.05)
power_button = Button(23, pull_up=False, bounce_time=0.05)

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

def color_button_pressed():
	global current_index, is_led_on

	print("Color Button is pressed")
	print(color_button.value)

	# LED가 켜져있을 때만 색상 변경
	if is_led_on:
		turn_off_all_leds()

		current_index = (current_index + 1) % len(leds)
		leds[current_index].on()

def power_button_pressed():
	global current_index, is_led_on

	print("ON/OFF Button is pressed")
	print(power_button.value)

	if is_led_on:
		leds[current_index].off()
		is_led_on = False

	else:
		leds[current_index].on()
		is_led_on = True


turn_off_all_leds()
color_button.when_pressed = color_button_pressed
power_button.when_pressed = power_button_pressed

try:
	pause()
except KeyboardInterrupt:
	turn_off_all_leds()
	for led in leds:
		led.off()
	print("\n exit")
