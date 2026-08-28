#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <QDebug>
#include <QTimer>
#include <QDateTime>
#include <QApplication>

#include <QVBoxLayout>
#include <QPainter>
#include <QPen>
#include <QFont>

#include <unistd.h>
#include <chrono>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <thread>

#define TRIG_PIN 23
#define ECHO_PIN 24
#define BUZZER_PIN 18

#define MOTOR_IN1 5
#define MOTOR_IN2 6
#define MOTOR_IN3 13
#define MOTOR_IN4 19

#define WARNING_LED_PIN 16

#define REQUEST_SWITCH_PIN 26

#define PCF8591_ADDR 0x48

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)   // 부모 초기화
    , ui(new Ui::MainWindow)    // 동적 생성
{
    ui->setupUi(this);

    chip = gpiod_chip_open("/dev/gpiochip0");

    if (!chip) {
        qDebug() << "chip open fail";
        return;
    }

    gpiod_line_settings *out_settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(out_settings, GPIOD_LINE_DIRECTION_OUTPUT);

    gpiod_line_settings *led_settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(led_settings, GPIOD_LINE_DIRECTION_OUTPUT);
    gpiod_line_settings_set_active_low(led_settings, true);

    gpiod_line_settings *in_settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(in_settings, GPIOD_LINE_DIRECTION_INPUT);
    gpiod_line_settings_set_bias(in_settings,GPIOD_LINE_BIAS_PULL_UP);

    gpiod_line_config *line_cfg = gpiod_line_config_new();

    unsigned int output_pins[] = {
        TRIG_PIN,
        BUZZER_PIN,
        MOTOR_IN1,
        MOTOR_IN2,
        MOTOR_IN3,
        MOTOR_IN4
    };
    unsigned int led_pins[] = {WARNING_LED_PIN};
    unsigned int input_pins[] = {
        ECHO_PIN,
        REQUEST_SWITCH_PIN
    };

    gpiod_line_config_add_line_settings(line_cfg, output_pins, 6, out_settings);
    gpiod_line_config_add_line_settings(line_cfg, led_pins, 1, led_settings);
    gpiod_line_config_add_line_settings(line_cfg, input_pins, 2, in_settings);

    gpiod_request_config *req_cfg = gpiod_request_config_new();

    request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);

    if (!request) {
        qDebug() << "request fail";
    }

    gpiod_line_settings_free(out_settings);
    gpiod_line_settings_free(led_settings);
    gpiod_line_settings_free(in_settings);
    gpiod_line_config_free(line_cfg);
    gpiod_request_config_free(req_cfg);

    i2cFd = open("/dev/i2c-1", O_RDWR);

    if (i2cFd < 0) {
        qDebug() << "i2c open fail";
    }

    timer = new QTimer(this);
    connect(timer, &QTimer::timeout, this, [this]() {
        refreshSensorData();
    });

    switchTimer = new QTimer(this);
    connect(switchTimer, &QTimer::timeout, this, [this]() {
        checkRequestSwitch();
    });
    switchTimer->start(50);

    ui->label_mode->setText("Manual Mode");
    ui->label_request->setText("No Request");

    ui->spin_distance_limit->setValue(20);
    ui->spin_light_limit->setValue(30);

    ui->btn_allow_access->setEnabled(false);

    setupDistanceChart();

    statusBlinkTimer = new QTimer(this);

    connect(statusBlinkTimer, &QTimer::timeout, this, [this]() {
        statusBlinkOn = !statusBlinkOn;

        if (statusBlinkOn) {
            ui->label_status->setStyleSheet(
                "background-color: red;"
                "color: white;"
                "font-weight: bold;"
                "border: 1px solid black;"
                );
        }
        else {
            ui->label_status->setStyleSheet(
                "background-color: #ffb3b3;"
                "color: black;"
                "font-weight: bold;"
                "border: 1px solid black;"
                );
        }
    });
}

MainWindow::~MainWindow()
{
    // GPIO 정리
    if (request)
        gpiod_line_request_release(request);

    if (chip)
        gpiod_chip_close(chip);

    if (i2cFd >= 0)
        ::close(i2cFd);

    delete ui;
}

double MainWindow::measureDistanceCm()
{
    using namespace std::chrono;

    gpiod_line_request_set_value(request, TRIG_PIN, GPIOD_LINE_VALUE_INACTIVE);
    usleep(2);

    gpiod_line_request_set_value(request, TRIG_PIN, GPIOD_LINE_VALUE_ACTIVE);
    usleep(10);

    gpiod_line_request_set_value(request, TRIG_PIN, GPIOD_LINE_VALUE_INACTIVE);

    auto timeoutStart = high_resolution_clock::now();

    while (gpiod_line_request_get_value(request, ECHO_PIN) == GPIOD_LINE_VALUE_INACTIVE) {
        if (duration_cast<milliseconds>(high_resolution_clock::now() - timeoutStart).count() > 100)
            return -1;
    }

    auto start = high_resolution_clock::now();

    while (gpiod_line_request_get_value(request, ECHO_PIN) == GPIOD_LINE_VALUE_ACTIVE) {
        if (duration_cast<milliseconds>(high_resolution_clock::now() - start).count() > 100)
            return -1;
    }

    auto end = high_resolution_clock::now();

    double durationUs = duration_cast<microseconds>(end - start).count();

    return durationUs * 0.0343 / 2.0;
}

int MainWindow::readLightValue()
{
    if (i2cFd < 0)
        return -1;

    ioctl(i2cFd, I2C_SLAVE, PCF8591_ADDR);

    char cmd = 0x40; // A0
    write(i2cFd, &cmd, 1);

    char dummy;
    read(i2cFd, &dummy, 1);

    char value;
    read(i2cFd, &value, 1);

    return static_cast<unsigned char>(value);
}

void MainWindow::beep(int ms)
{
    int frequency = 2000;
    int delayUs = 1000000 / frequency / 2;

    int count = (ms * 1000) / (delayUs * 2);

    for (int i = 0; i < count; i++) {

        gpiod_line_request_set_value(
            request,
            BUZZER_PIN,
            GPIOD_LINE_VALUE_ACTIVE
            );

        usleep(delayUs);

        gpiod_line_request_set_value(
            request,
            BUZZER_PIN,
            GPIOD_LINE_VALUE_INACTIVE
            );

        usleep(delayUs);
    }
}

void MainWindow::setMotorStep(int a, int b, int c, int d)
{
    gpiod_line_request_set_value(request, MOTOR_IN1, a ? GPIOD_LINE_VALUE_ACTIVE : GPIOD_LINE_VALUE_INACTIVE);
    gpiod_line_request_set_value(request, MOTOR_IN2, b ? GPIOD_LINE_VALUE_ACTIVE : GPIOD_LINE_VALUE_INACTIVE);
    gpiod_line_request_set_value(request, MOTOR_IN3, c ? GPIOD_LINE_VALUE_ACTIVE : GPIOD_LINE_VALUE_INACTIVE);
    gpiod_line_request_set_value(request, MOTOR_IN4, d ? GPIOD_LINE_VALUE_ACTIVE : GPIOD_LINE_VALUE_INACTIVE);
}

void MainWindow::stopMotor()
{
    setMotorStep(0, 0, 0, 0);
}

void MainWindow::rotateMotor(int steps, bool clockwise)
{
    int sequence[8][4] = {
        {1, 0, 0, 0},
        {1, 1, 0, 0},
        {0, 1, 0, 0},
        {0, 1, 1, 0},
        {0, 0, 1, 0},
        {0, 0, 1, 1},
        {0, 0, 0, 1},
        {1, 0, 0, 1}
    };

    for (int i = 0; i < steps; i++) {
        int index;

        if (clockwise) {
            index = i % 8;
        } else {
            index = 7 - (i % 8);
        }

        setMotorStep(
            sequence[index][0],
            sequence[index][1],
            sequence[index][2],
            sequence[index][3]
            );

        usleep(2000);
    }

    stopMotor();
}

void MainWindow::closeGate()
{
    if (!gateClosed) {
        rotateMotor(512, true);   // 약 90도
        gateClosed = true;
    }
}

void MainWindow::openGate()
{
    if (gateClosed) {
        rotateMotor(512, false);  // 다시 원위치
        gateClosed = false;
    }
}

void MainWindow::setWarningLed(bool on)
{
    gpiod_line_request_set_value(
        request,
        WARNING_LED_PIN,
        on ? GPIOD_LINE_VALUE_ACTIVE : GPIOD_LINE_VALUE_INACTIVE
        );
}

void MainWindow::blinkWarningLed(int count)
{
    for (int i = 0; i < count; i++) {
        setWarningLed(true);
        usleep(150000);
        setWarningLed(false);
        usleep(150000);
    }
}

void MainWindow::checkRequestSwitch()
{
    int value =
        gpiod_line_request_get_value(
            request,
            REQUEST_SWITCH_PIN
            );

    // Pull-up 사용:
    // 안 누름 = ACTIVE
    // 누름 = INACTIVE

    bool pressed =
        (value == GPIOD_LINE_VALUE_INACTIVE);

    // 처음 눌렸을 때만 감지
    if (pressed && !previousSwitchPressed) {

        accessRequest = true;

        QString currentTime =
            QDateTime::currentDateTime()
                .toString("HH:mm:ss");

        ui->label_request->setText(
            "Access Request"
        );

        ui->btn_allow_access->setEnabled(true);

        ui->list_log->addItem(
            "[" + currentTime +
            "] Access Request Detected"
        );

        beep(80);
    }

    previousSwitchPressed = pressed;
}

void MainWindow::runAlertAction(int beepMs, int blinkCount, bool closeGateFlag)
{
    if (warningActionRunning)
        return;

    warningActionRunning = true;

    std::thread([this, beepMs, blinkCount, closeGateFlag]() {

        std::thread buzzerThread([this, beepMs]() {
            beep(beepMs);
        });

        std::thread ledThread([this, blinkCount]() {
            blinkWarningLed(blinkCount);
        });

        if (closeGateFlag) {
            closeGate();
        }

        buzzerThread.join();
        ledThread.join();

        warningActionRunning = false;

    }).detach();
}

void MainWindow::setupDistanceChart()
{
    distanceSeries = new QLineSeries(this);
    distanceSeries->setName("Distance");

    QPen linePen(QColor(80, 190, 255));
    linePen.setWidth(3);
    linePen.setCapStyle(Qt::RoundCap);
    linePen.setJoinStyle(Qt::RoundJoin);
    distanceSeries->setPen(linePen);

    QChart *chart = new QChart();
    chart->addSeries(distanceSeries);
    chart->setTitle("Distance Monitor");
    chart->legend()->hide();

    chart->setMargins(QMargins(10, 10, 25, 10));
    chart->setBackgroundRoundness(8);

    QFont titleFont;
    titleFont.setPointSize(11);
    titleFont.setBold(true);
    chart->setTitleFont(titleFont);

    axisX = new QValueAxis(this);
    axisX->setRange(0, 30);
    axisX->setTitleText("Time");
    axisX->setLabelFormat("%d");
    axisX->setTickCount(6);

    axisY = new QValueAxis(this);
    axisY->setRange(0, 200);
    axisY->setTitleText("Distance (cm)");
    axisY->setLabelFormat("%d");
    axisY->setTickCount(6);

    QFont axisFont;
    axisFont.setPointSize(8);

    axisX->setLabelsFont(axisFont);
    axisY->setLabelsFont(axisFont);
    axisX->setTitleFont(axisFont);
    axisY->setTitleFont(axisFont);

    chart->addAxis(axisX, Qt::AlignBottom);
    chart->addAxis(axisY, Qt::AlignLeft);

    distanceSeries->attachAxis(axisX);
    distanceSeries->attachAxis(axisY);

    distanceChartView = new QChartView(chart);
    distanceChartView->setRenderHint(QPainter::Antialiasing);
    distanceChartView->setMinimumSize(420, 260);

    QVBoxLayout *layout = new QVBoxLayout(ui->widget_distance_chart);
    layout->addWidget(distanceChartView);
    layout->setContentsMargins(0, 0, 0, 0);

    ui->widget_distance_chart->setLayout(layout);
}

void MainWindow::updateDistanceChart(double distance)
{
    if (distance < 0)
        return;

    if (distance > 200) {
        distance = 200;
    }

    distanceHistory.append(distance);

    if (distanceHistory.size() > 30) {
        distanceHistory.removeFirst();
    }

    QList<QPointF> points;

    for (int i = 0; i < distanceHistory.size(); i++) {
        points.append(QPointF(i, distanceHistory[i]));
    }

    distanceSeries->replace(points);

    axisX->setRange(0, 31);
}

void MainWindow::startStatusBlink()
{
    if (!statusBlinkTimer->isActive()) {
        statusBlinkTimer->start(300);
    }
}

void MainWindow::stopStatusBlink()
{
    statusBlinkTimer->stop();
    statusBlinkOn = false;
}

void MainWindow::refreshSensorData()
{
    double distance = measureDistanceCm();
    int light = readLightValue();

    if (distance < 0) {
        ui->label_distance->setText("Measure Failed");
    }
    else if (distance > 200) {
        ui->label_distance->setText("200+ cm");
    }
    else {
        ui->label_distance->setText(
            QString::number(distance, 'f', 1) + " cm"
            );
    }

    updateDistanceChart(distance);

    ui->label_light->setText(QString::number(light));

    updateStatus(distance, light);
}

void MainWindow::updateStatus(double distance, int light)
{
    double detectDistance = ui->spin_distance_limit->value();
    double warningDistance = 10.0;

    int lightLimit = ui->spin_light_limit->value();

    QString currentTime =
        QDateTime::currentDateTime().toString("HH:mm:ss");

    // 거리 경고
    if (distance > 0 && distance < warningDistance) {

        QString message =
            "[" + currentTime + "] Warning Distance : " +
            QString::number(distance, 'f', 1) + " cm";

        ui->label_status->setText("WARNING");

        ui->list_log->addItem(message);

        startStatusBlink();

        runAlertAction(100, 3, true);
    }

    else if (distance > 0 && distance < detectDistance) {

        QString message =
            "[" + currentTime + "] Visitor Detected : " +
            QString::number(distance, 'f', 1) + " cm";

        ui->label_status->setText("DETECTED");

        stopStatusBlink();

        ui->label_status->setStyleSheet(
            "background-color: orange;"
            "color: black;"
            "font-weight: bold;"
            "border: 1px solid black;"
            );

        ui->list_log->addItem(message);

        setWarningLed(true);
    }

    // 조도 경고
    else if (light >= 0 && light < lightLimit) {

        QString message =
            "[" + currentTime + "] Too Dark : " +
            QString::number(light);

        ui->label_status->setText("WARNING");
        startStatusBlink();

        ui->label_status->setStyleSheet(
            "background-color: red;"
            "color: white;"
            "font-weight: bold;"
            "border: 1px solid black;"
            );

        ui->list_log->addItem(message);

        runAlertAction(50, 2, false);
    }

    // 정상 상태
    else {
        stopStatusBlink();

        setWarningLed(false);
        openGate();

        ui->label_status->setText("NORMAL");

        ui->label_status->setStyleSheet(
            "background-color: green;"
            "color: white;"
            "font-weight: bold;"
            "border: 1px solid black;"
        );
    }
}

void MainWindow::on_btn_refresh_clicked()
{
    refreshSensorData();
}

void MainWindow::on_btn_mode_clicked()
{
    monitorMode = !monitorMode;

    if (monitorMode) {
        ui->label_mode->setText("Monitor Mode");

        // Monitor Mode에서는 자동 갱신이므로 Refresh 버튼 비활성화
        ui->btn_refresh->setEnabled(false);

        refreshSensorData();
        timer->start(1000);
    }
    else {
        ui->label_mode->setText("Manual Mode");

        // Manual Mode에서는 직접 Refresh 가능
        ui->btn_refresh->setEnabled(true);

        timer->stop();
    }
}

void MainWindow::on_btn_buzzer_clicked()
{
    beep(200);
}

void MainWindow::on_btn_allow_access_clicked()
{
    if (!accessRequest)
        return;

    accessRequest = false;

    QString currentTime =
        QDateTime::currentDateTime()
            .toString("HH:mm:ss");

    ui->label_request->setText("Access Granted");

    ui->btn_allow_access->setEnabled(false);

    QApplication::processEvents();

    ui->list_log->addItem(
        "[" + currentTime +
        "] Access Granted"
    );

    // 부저 병렬 실행
    std::thread buzzerThread([this]() {
        beep(150);
    });

    // LED 병렬 실행
    std::thread ledThread([this]() {

        setWarningLed(true);

        usleep(700000);

        setWarningLed(false);
    });

    // 모터는 메인에서 바로 실행
    rotateMotor(512, false);

    buzzerThread.join();
    ledThread.join();
}
