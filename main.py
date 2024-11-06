from machine import Timer, ADC, I2C
import time
import math
from display.aqm1602a import AQM1602A

import network
import socket
import ujson

def main():
    # 設定ファイルの読み込み
    config_file = open('config.json', 'r')
    config = ujson.load(config_file)
    
    adc32 = ADC(32, atten=ADC.ATTN_0DB)
    i2c0 = I2C(0)
    disp = None

    # ディスプレイの検出と初期化
    if 62 in i2c0.scan():
        disp = AQM1602A(i2c0)
        disp.init()
    else:
        print('ディスプレイが接続されていません')
    
    # Wi-Fi接続
    connectWiFi(config['wifi_ssid'], config['wifi_pass'])
    
    # 電流の繰り返し測定
    while True:
        current = measureRMSCurrent(adc32, 3000, 10)
        # 電流値を送る
        sock = socket.socket()
        sock.connect(
            socket.getaddrinfo(config['ip_addr'], 40000)[0][-1]
            )
        current_send_value = int(current * 100)
        sock.send(current_send_value.to_bytes(2, 'little'))
        sock.close()

        if(disp):
            disp.write(f'{current:05.2f} A')
        time.sleep_ms(2000)


# Wi-Fi接続
def connectWiFi(ssid, passwd):
    # エラーの発生を防ぐため、接続再試行は少し時間を空けています
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(reconnects=0) # 接続自動再試行の無効化
    while not wlan.isconnected():
        print("Wi-Fi接続試行中...")
        wlan.connect(ssid, passwd)
        time.sleep_ms(4000)
    print("Wi-Fi接続完了!")


# 実効値電流の算出
def measureRMSCurrent(adc, ratio, resistance):
    # コールバック関数との 合計値,サンプリング回数 の受け渡しクラス 
    class Message:
        sum = 0
        count = 0
    
    # ADCの値の2乗値をsumに加算する
    def addADCValueSquared(t, message):
        adc_value = adc.read()
        message.sum += ((adc_value-2047) ** 2)
        message.count += 1


    tim_message = Message() # 合計値の受け渡し用
    tim = Timer(0)
    # 1800Hzで200ms間addADCValueSquaredを繰り返し実行する 
    tim.init(mode=Timer.PERIODIC, freq=1800, callback=lambda t: addADCValueSquared(t, tim_message))
    time.sleep_ms(200)
    tim.deinit()

    # 電流の計算
    avg = tim_message.sum / tim_message.count
    current = (math.sqrt(avg) * (1.1 / 4096) / resistance) * ratio
    return current


if __name__ == "__main__":
    main()