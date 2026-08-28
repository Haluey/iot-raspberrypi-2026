from flask import Flask

app = Flask(__name__)

@app.route('/')	# 메인 페이지
def home():
	return "Flask Server Test!!"

# 변수 규칙
@app.route('/user/<username>')
def user_profile(username):
	return "user: %s" % username

@app.route('/pw/<int:pw_num>')
def show_pw(pw_num):
	return "pw: %d" % pw_num

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
