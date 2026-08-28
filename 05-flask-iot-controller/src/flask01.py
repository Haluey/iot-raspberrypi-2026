# 이 방식이 GET방식
from flask import Flask

app = Flask(__name__)

# 주소창에 '/' 이런형태로 작성되면 'hello_world'함수를 실행해라
@app.route('/')	# 기본 문법, 이 뒤에는 무조건 함수
def hello_world():
	return 'Hello World'	# 이 함수에는 무조건 return이 와야됨

if __name__ == "__main__":	# 실행 파일이면
	app.run(host='0.0.0.0',port=9011, debug=True)	# 어떤 ip든지 접속 가능하게 하겠다
