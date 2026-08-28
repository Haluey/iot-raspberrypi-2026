from flask import Flask
from gpiozero import LED

app = Flask(__name__)

@app.route('/')
def home():
	return "Web LED Control"

@app.route('/led/on')
def ledOn():
	return '<h1> Led On </h1>'

@app.route('/led/off')
def ledOf():
	return '<h1> Led Off </h1>'

@app.route('/led/clean')
def gpioCleanup():
	return '<h1> GPIO CLEANUP </h1>'

if __name__ == "__main__":
	try:
		app.run(host='0.0.0.0', debug=True)

	finally:
		led.off()
		led.close()
