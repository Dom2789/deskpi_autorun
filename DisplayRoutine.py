import RPi.GPIO as GPIO
from smbus import SMBus
from oled96 import ssd1306
import threading
import time
from PIL import ImageFont
from DataExchange import Data


class Display_Routine(threading.Thread):
    def __init__(self):
        super(Display_Routine, self).__init__()
        self.data = Data()

    def run(self):
        #setup
        GPIO.setmode(GPIO.BOARD)
        i2cbus = SMBus(1)        # 1 = Raspberry Pi but NOT early REV1 board
        oled = ssd1306(i2cbus)   # create oled object, nominating the correct I2C bus, default address
        oled.cls()
        draw = oled.canvas
        font = ImageFont.load_default()
        try:
            while True:
                # Draw a black filled box to clear the image.
                draw.rectangle((0,0,128,96), outline=0, fill=0)
                # Collect Data from BME280 includes sleep(0.5)
                temp, pres, humi = self.read_BME280(i2cbus)
                self.data.set_data((temp, pres, humi))
                timestamp = time.strftime("%H:%M:%S")
                draw.text((8, 8),'Time: ' + timestamp,  font=font, fill=1)
                draw.text((8, 22),'temp: %.2f C' %temp, font=font, fill=1)
                draw.text((8, 36),'pres: %.2f hPa' %pres ,  font=font, fill=1)
                draw.text((8, 50),'humi: %.2f %%' %humi, font=font, fill=1)
                oled.display()
                time.sleep(0.5)
        except KeyboardInterrupt:
            oled.cls()
            GPIO.cleanup()

    def read_BME280(self, i2cbus: SMBus):
        # BME280 address, 0x76(118)
        # Read data back from 0x88(136), 24 bytes
        b1 = i2cbus.read_i2c_block_data(0x76, 0x88, 24)

        # Convert the data
        # Temp coefficients
        dig_T1 = b1[1] * 256 + b1[0]
        dig_T2 = b1[3] * 256 + b1[2]
        if dig_T2 > 32767 :
            dig_T2 -= 65536
        dig_T3 = b1[5] * 256 + b1[4]
        if dig_T3 > 32767 :
            dig_T3 -= 65536

        # Pressure coefficients
        dig_P1 = b1[7] * 256 + b1[6]
        dig_P2 = b1[9] * 256 + b1[8]
        if dig_P2 > 32767 :
            dig_P2 -= 65536
        dig_P3 = b1[11] * 256 + b1[10]
        if dig_P3 > 32767 :
            dig_P3 -= 65536
        dig_P4 = b1[13] * 256 + b1[12]
        if dig_P4 > 32767 :
            dig_P4 -= 65536
        dig_P5 = b1[15] * 256 + b1[14]
        if dig_P5 > 32767 :
            dig_P5 -= 65536
        dig_P6 = b1[17] * 256 + b1[16]
        if dig_P6 > 32767 :
            dig_P6 -= 65536
        dig_P7 = b1[19] * 256 + b1[18]
        if dig_P7 > 32767 :
            dig_P7 -= 65536
        dig_P8 = b1[21] * 256 + b1[20]
        if dig_P8 > 32767 :
            dig_P8 -= 65536
        dig_P9 = b1[23] * 256 + b1[22]
        if dig_P9 > 32767 :
            dig_P9 -= 65536

        # BME280 address, 0x76(118)
        # Read data back from 0xA1(161), 1 byte
        dig_H1 = i2cbus.read_byte_data(0x76, 0xA1)

        # BME280 address, 0x76(118)
        # Read data back from 0xE1(225), 7 bytes
        b1 = i2cbus.read_i2c_block_data(0x76, 0xE1, 7)

        # Convert the data
        # Humidity coefficients
        dig_H2 = b1[1] * 256 + b1[0]
        if dig_H2 > 32767 :
            dig_H2 -= 65536
        dig_H3 = (b1[2] &  0xFF)
        dig_H4 = (b1[3] * 16) + (b1[4] & 0xF)
        if dig_H4 > 32767 :
            dig_H4 -= 65536
        dig_H5 = (b1[4] / 16) + (b1[5] * 16)
        if dig_H5 > 32767 :
            dig_H5 -= 65536
        dig_H6 = b1[6]
        if dig_H6 > 127 :
            dig_H6 -= 256

        # BME280 address, 0x76(118)
        # Select control humidity register, 0xF2(242)
        #		0x01(01)	Humidity Oversampling = 1
        i2cbus.write_byte_data(0x76, 0xF2, 0x01)
        # BME280 address, 0x76(118)
        # Select Control measurement register, 0xF4(244)
        #		0x27(39)	Pressure and Temperature Oversampling rate = 1
        #					Normal mode
        i2cbus.write_byte_data(0x76, 0xF4, 0x27)
        # BME280 address, 0x76(118)
        # Select Configuration register, 0xF5(245)
        #		0xA0(00)	Stand_by time = 1000 ms
        i2cbus.write_byte_data(0x76, 0xF5, 0xA0)

        time.sleep(0.5)

        # BME280 address, 0x76(118)
        # Read data back from 0xF7(247), 8 bytes
        # Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB
        # Temperature xLSB, Humidity MSB, Humidity LSB
        data = i2cbus.read_i2c_block_data(0x76, 0xF7, 8)

        # Convert pressure and temperature data to 19-bits
        adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
        adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16

        # Convert the humidity data
        adc_h = data[6] * 256 + data[7]

        # Temperature offset calculations
        var1 = ((adc_t) / 16384.0 - (dig_T1) / 1024.0) * (dig_T2)
        var2 = (((adc_t) / 131072.0 - (dig_T1) / 8192.0) * ((adc_t)/131072.0 - (dig_T1)/8192.0)) * (dig_T3)
        t_fine = (var1 + var2)
        cTemp = (var1 + var2) / 5120.0
        fTemp = cTemp * 1.8 + 32

        # Pressure offset calculations
        var1 = (t_fine / 2.0) - 64000.0
        var2 = var1 * var1 * (dig_P6) / 32768.0
        var2 = var2 + var1 * (dig_P5) * 2.0
        var2 = (var2 / 4.0) + ((dig_P4) * 65536.0)
        var1 = ((dig_P3) * var1 * var1 / 524288.0 + ( dig_P2) * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * (dig_P1)
        p = 1048576.0 - adc_p
        p = (p - (var2 / 4096.0)) * 6250.0 / var1
        var1 = (dig_P9) * p * p / 2147483648.0
        var2 = p * (dig_P8) / 32768.0
        pressure = (p + (var1 + var2 + (dig_P7)) / 16.0) / 100

        # Humidity offset calculations
        var_H = ((t_fine) - 76800.0)
        var_H = (adc_h - (dig_H4 * 64.0 + dig_H5 / 16384.0 * var_H)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * var_H * (1.0 + dig_H3 / 67108864.0 * var_H)))
        humidity = var_H * (1.0 -  dig_H1 * var_H / 524288.0)
        if humidity > 100.0 :
            humidity = 100.0
        elif humidity < 0.0 :
            humidity = 0.0
        return cTemp, pressure, humidity