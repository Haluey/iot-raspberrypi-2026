# POST방식
from flask import Flask, render_template  # 이걸 임포트해야 html파일 불러오기가 가능함

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')	# 이 파일은 templates라는 폴더 안에 있어야됨

@app.route('/user/')
def user_profile():
	user = '홍길동'
	user_age = 50
	return render_template('index.html', name = user, age = user_age)

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)
