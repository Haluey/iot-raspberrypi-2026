from flask import Flask

app = Flask(__name__)

@app.route('/')	# 메인 페이지
def home():
	return "Flask Server Test!!"

@app.route('/user')
def user():
	return "admin"

@app.route('/pw')
def pw():
	return "1111"

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
