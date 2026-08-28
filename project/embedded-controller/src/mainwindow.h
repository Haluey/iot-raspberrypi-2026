#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

#include <QtCharts/QChartView>
#include <QtCharts/QLineSeries>
#include <QtCharts/QValueAxis>
#include <QtCharts/QChart>

#include <gpiod.h>

QT_BEGIN_NAMESPACE  // 매크로
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);  // 생성자
    ~MainWindow();  // 소멸자

private slots:
    void on_btn_refresh_clicked();
    void on_btn_mode_clicked();
    void on_btn_buzzer_clicked();

    void on_btn_allow_access_clicked();

private:
    Ui::MainWindow *ui; // 객체 포인터

    gpiod_chip *chip = nullptr;
    gpiod_line_request *request = nullptr;

    QTimer *timer = nullptr;
    QTimer *switchTimer;

    bool monitorMode = false;
    int i2cFd = -1;
    bool gateClosed = false;
    bool previousSwitchPressed = false;
    bool accessRequest = false;
    bool warningActionRunning = false;

    bool statusBlinkOn = false;

    QChartView *distanceChartView;
    QLineSeries *distanceSeries;
    QValueAxis *axisX;
    QValueAxis *axisY;
    QList<double> distanceHistory;

    QTimer *statusBlinkTimer;

    double measureDistanceCm();
    int readLightValue();

    void refreshSensorData();
    void beep(int ms);
    void updateStatus(double distance, int light);

    void setMotorStep(int a, int b, int c, int d);
    void stopMotor();
    void rotateMotor(int steps, bool clockwise);
    void closeGate();
    void openGate();

    void setWarningLed(bool on);
    void blinkWarningLed(int count);

    void checkRequestSwitch();

    void runAlertAction(int beepMs, int blinkCount, bool closeGateFlag);

    void setupDistanceChart();
    void updateDistanceChart(double distance);

    void startStatusBlink();
    void stopStatusBlink();
};
#endif // MAINWINDOW_H
