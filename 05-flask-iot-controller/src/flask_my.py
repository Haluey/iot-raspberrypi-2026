from flask import Flask

app = Flask(__name__)

@app.route('/')	# 메인 페이지
def home():
	return "Flask Server Test!!"

@app.route('/이름')
def name():
	return "김민주"

@app.route('/성별')
def wo():
	return "여자"

@app.route('/주소')
def address():
	return "부산시 연제구"

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
