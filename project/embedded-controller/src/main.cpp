#include "mainwindow.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv); // 객체 생성
    MainWindow w;
    w.show();
    return a.exec();
}
