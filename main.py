from machine import Timer, ADC, I2C
import time
import math
from display.aqm1602a import AQM1602A


def main():
    adc32 = ADC(32, atten=ADC.ATTN_0DB)
    i2c0 = I2C(0)
    disp = None
    if 62 in i2c0.scan(): # ディスプレイが接続されている場合
        disp = AQM1602A(i2c0)
        disp.init()
    else:
        print('ディスプレイが接続されていません')
    
    while True:
        current = measureRMSCurrent(adc32, 3000, 10)
        print(current)
        if(disp):
            disp.write(f'{current:05.2f} A')
        time.sleep_ms(5000)

    



def measureRMSCurrent(adc, ratio, resistance):
    # コールバック関数との合計値の受け渡しクラス 
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