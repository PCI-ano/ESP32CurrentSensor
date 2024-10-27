import time

class AQM1602A:
    
    
    def __init__(self, i2c):
        self.i2c = i2c

    def init(self):
        self.i2c.writeto(0x3e, b'\x00\x38')
        time.sleep_ms(1)
        self.i2c.writeto(0x3e, b'\x00\x39')
        time.sleep_ms(1)
        self.i2c.writeto(0x3e, b'\x00\x14')
   
        time.sleep_ms(1)
        self.i2c.writeto(0x3e, b'\x00\x73')
        time.sleep_ms(1)
        self.i2c.writeto(0x3e, b'\x00\x56')
        time.sleep_ms(1)
        self.i2c.writeto(0x3e, b'\x00\x6C')
        time.sleep_ms(1) #
        self.i2c.writeto(0x3e, b'\x00\x38')
        time.sleep_ms(1)
        self.i2c.writeto(0x3e, b'\x00\x01')
        time.sleep_ms(1)
        self.i2c.writeto(0x3e, b'\x00\x0C')
        time.sleep_ms(1)
    
    def write(self, str, start=0, end=31):
        text_byte = str.encode('shift_jis') # テキストをshift_jisの値に変換

        for ch, pos in zip(text_byte, range(start, end + 1)): # 文字数または指定した表示範囲のうち少ないほうの回数繰り返す
            ddram_address = (0x30 + pos) if 16 <= pos else pos

            self.i2c.writeto(0x3e, b'\x00' + (0x80 + ddram_address).to_bytes(1, 'big'))
            self.i2c.writeto(0x3e, b'\x40' + ch.to_bytes(1, 'big'))

        text_len = len(text_byte)
        if text_len < (end - start + 1): # 文字数よりも指定した表示範囲のほうが大きい場合
            # 残りの範囲を空白で埋める
            for pos in range(start + text_len, end + 1):
                ddram_address = 0x30 + pos if 16 <= pos else pos
                self.i2c.writeto(0x3e, b'\x00' + (0x80 + ddram_address).to_bytes(1, 'big'))
                self.i2c.writeto(0x3e, b'\x40' + b'\x20')
