#Weather station data acquisition and database
import time
import board
from adafruit_bme280 import basic as adafruit_bme280
import mariadb

conn = mariadb.connect(
    user="pi",
    password="raspberry",
    host="localhost",
    database="weather")

cur = conn.cursor()

i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)


def add_data(ambient_temp, pressure, humidity):
    try:
        cur.execute("INSERT INTO weather_measurements (ambient_temperature,pressure,humidity) VALUES (?, ?,?)", (ambient_temp,pressure,humidity))
    except mariadb.Error as e:
        print(f"Error: {e}")

while True:
	ambient_temp=bme280.temperature
	pressure=bme280.pressure
	humidity=bme280.humidity
	add_data(ambient_temp, pressure, humidity)
	conn.commit() 
	#print(f"Last Inserted ID: {cur.lastrowid}")
	#print("\nTemperature: %0.1f C" % ambient_temp)
	#print("Humidity: %0.1f %%" % humidity)
	#print("Pressure: %0.1f hPa" % pressure)
	time.sleep(60)

