from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def get():
	value1 = request.args.get('이름', 'user')	# request를 사용해서 값 얻어옴
	value2 = request.args.get('지역', '부산')
	return value1 + " : " + value2

# GET방식 주소 입력
# http://192.168.0.3:5000/?이름=홍길동&지역=서울

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
