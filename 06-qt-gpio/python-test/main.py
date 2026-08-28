import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from gpiozero import LED

GPIO_PIN = 17

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Qt Designer에서 만든 ui 파일 불러오기
        uic.loadUi("mainwindow.ui", self)

        # LED 설정
        # active_high=False는 C++의 active_low(true)와 비슷한 역할
        self.led = LED(GPIO_PIN, active_high=False)

        # 처음 상태 OFF
        self.led.off()
        self.label_led.setStyleSheet(
            "background-color: gray;"
            "border-radius: 20px;"
        )

        # 버튼 이벤트 연결
        self.pushButton.clicked.connect(self.led_on)
        self.pushButton_2.clicked.connect(self.led_off)

    def led_on(self):
        self.led.on()

        self.label_led.setStyleSheet(
            "background-color: red;"
            "border-radius: 20px;"
        )

    def led_off(self):
        self.led.off()

        self.label_led.setStyleSheet(
            "background-color: gray;"
            "border-radius: 20px;"
        )

    def closeEvent(self, event):
        # 창 닫을 때 GPIO 정리
        self.led.off()
        self.led.close()
        event.accept()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
