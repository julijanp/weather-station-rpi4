#Weather station data acquisition and database
import time
import board
from adafruit_bme280 import basic as adafruit_bme280
import mariadb
from gpiozero import Button
import board
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
#conn = mariadb.connect(
    #user="pi",
    #password="raspberry",
    #host="localhost",
    #database="weather")

#cur = conn.cursor()

i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
#Wind direction
ads = ADS.ADS1015(i2c)
chan = AnalogIn(ads, ADS.P0)

wind_speed_sensor = Button(5) #aneometer as button gpio pin 5 (28)
wind_count=0 #counts how many half rotations of  aneometer
time_interval=5

def add_data(ambient_temp, pressure, humidity):
    try:
        cur.execute("INSERT INTO weather_measurements (ambient_temperature,pressure,humidity) VALUES (?, ?,?)", (ambient_temp,pressure,humidity))
    except mariadb.Error as e:
        print(f"Error: {e}")

def spin():
    global wind_count
    wind_count=wind_count+1

def calculate_speed(time_sec):
    global wind_count
    speed_s=wind_count / time_sec
    speed=speed_s * 2.4
    return speed

wind_speed_sensor.when_pressed=spin

while True:
        ambient_temp=bme280.temperature
        pressure=bme280.pressure
        humidity=bme280.humidity
        #add_data(ambient_temp, pressure, humidity)
        #conn.commit() 
        #print(f"Last Inserted ID: {cur.lastrowid}")
        print("\nTemperature: %0.1f C" % ambient_temp)
        print("Humidity: %0.1f %%" % humidity)
        print("Pressure: %0.1f hPa" % pressure)
        print("N spins:" +  str(wind_count))
        print("Speed:" +  str(calculate_speed(time_interval)) + "km/h")
        print("Digital:"+str(chan.value)+" Volatage:"+str(chan.voltage)+"V")
        wind_count=0
        time.sleep(time_interval)
