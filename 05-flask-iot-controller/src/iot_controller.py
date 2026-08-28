from flask import Flask, render_template, redirect, url_for
from gpiozero import LED, PWMOutputDevice, DistanceSensor
import smbus

app = Flask(__name__)

# LED
leds = {
	"led1":	LED(17, active_high=False),
	"led2": LED(27, active_high=False),
	"led3": LED(22, active_high=False)
}

# Buzzer
buzzer = PWMOutputDevice(18)

# Ultrasonic
sensor = DistanceSensor(echo=23, trigger=24)

# CDS
bus = smbus.SMBus(1)
ADDR = 0x48

def read_cds():
	bus.write_byte(ADDR, 0x40)
	bus.read_byte(ADDR)

	return bus.read_byte(ADDR)

def get_led_states():
	led_states = {}

	for name, led in leds.items():
		led_states[name] = "ON" if led.is_lit else "OFF"

	return led_states

@app.route("/")
def index():
	led_states = get_led_states()
	buzzer_state = "ON" if buzzer.value > 0 else "OFF"
	cds = read_cds()
	distance = round(sensor.distance * 100, 2)

	return render_template(
		"iot_controller.html",
		led1_state=led_states["led1"],
		led2_state=led_states["led2"],
		led3_state=led_states["led3"],

		buzzer_state=buzzer_state,

		cds=cds,
		distance=distance
	)

# LED1
@app.route("/led1/on", methods=["POST"])
def led1_on():
	leds["led1"].on()

	return redirect(url_for("index"))

@app.route("/led1/off", methods=["POST"])
def led1_off():
	leds["led1"].off()

	return redirect(url_for("index"))

# LED2
@app.route("/led2/on", methods=["POST"])
def led2_on():
	leds["led2"].on()

	return redirect(url_for("index"))

@app.route("/led2/off", methods=["POST"])
def led2_off():
	leds["led2"].off()

	return redirect(url_for("index"))

# LED3
@app.route("/led3/on", methods=["POST"])
def led3_on():
	leds["led3"].on()

	return redirect(url_for("index"))

@app.route("/led3/off", methods=["POST"])
def led3_off():
	leds["led3"].off()

	return redirect(url_for("index"))

# Buzzer
@app.route("/buzzer/on", methods=["POST"])
def buzzer_on():
	buzzer.frequency = 1000
	buzzer.value = 0.5

	return redirect(url_for("index"))


@app.route("/buzzer/off", methods=["POST"])
def buzzer_off():
	buzzer.off()

	return redirect(url_for("index"))

# Run
if __name__ == "__main__":
	try:
		app.run(host="0.0.0.0", port=5000, use_reloader=False)

	finally:
		for led in leds.values():
			led.off()
			led.close()

		buzzer.off()
		buzzer.close()
