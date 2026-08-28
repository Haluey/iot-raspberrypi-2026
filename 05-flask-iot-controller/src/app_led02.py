from flask import Flask, render_template, redirect, url_for
from gpiozero import LED

app = Flask(__name__)

led = LED(17, active_high=False)

@app.route("/")
def index():
	state = "ON" if led.is_lit else "OFF"	# 파이썬에서 제공하는 3항 연산자

	return render_template("led.html", state=state)

@app.route("/led/on", methods=["POST"])
def led_on():
	led.on()

	return redirect(url_for("index"))	# index함수로 이동해라

@app.route("/led/off", methods=["POST"])
def led_off():
	led.off()

	return redirect(url_for("index"))

if __name__ == "__main__":
	try:
		app.run(host="0.0.0.0", port=5000, use_reloader=False)

	finally:
		led.off()
		led.close()
