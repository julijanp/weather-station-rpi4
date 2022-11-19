#Weather station data acquisition and database
import time
import board
import statistics
from gpiozero import Button #anenometer
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_ads1x15.ads1015 as ADS #wind vane
from adafruit_ads1x15.analog_in import AnalogIn #wind vane
i2c = board.I2C()  # uses board.SCL and board.SDA
import mariadb

conn = mariadb.connect(
    user="pi",
    password="raspberry",
    host="localhost",
    database="weather")

cur = conn.cursor()

#ambient sensor
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

#Wind direction
ads = ADS.ADS1015(i2c)
chan = AnalogIn(ads, ADS.P0)
direction={2.5: "S",
           2.9: "SE",
           1.5: "SW",
           0.3: "W",
           0.6: "NW",
           0.9: "N",
           2.0: "NE",
           3.1: "E"} #10kOhm

#Wind speed
wind_speed_sensor = Button(5) #aneometer as button gpio pin 5 (29)
wind_count=0 #counts how many half rotations of  aneometer
wind_interval=5 #gust measurement time interval
time_interval=300 #measurements time interval

#Rainfall
rain_sensor = Button(6) #rainfall sensor as button gpio pin 6
rain_count=0 
BUCKET_SIZE = 0.2794
def bucket_tipped():
    global rain_count
    rain_count = rain_count + 1
    #print (rain_count * BUCKET_SIZE)

def reset_rainfall():
    global rain_count
    rain_count = 0

def spin():
    global wind_count
    wind_count=wind_count+1

def calculate_speed(time_sec):
    global wind_count
    speed_s=wind_count / time_sec
    speed=speed_s * 2.4
    return speed

def reset_wind():
    global wind_count
    wind_count = 0



def add_data(ambient_temp, pressure, humidity, wind_direction, wind_speed, wind_gust, rainfall):
    try:
        cur.execute("INSERT INTO weather_measurements (ambient_temperature,pressure,humidity,wind_direction,wind_speed,wind_gust_speed,rainfall) VALUES (?,?,?,?,?,?,?)", (ambient_temp,pressure,humidity,wind_direction,wind_speed,wind_gust,rainfall))
    except mariadb.Error as e:
        print(f"Error: {e}")

wind_speed_sensor.when_pressed=spin
rain_sensor.when_pressed = bucket_tipped
#while True:
	#ambient_temp=bme280.temperature
	#pressure=bme280.pressure
	#humidity=bme280.humidity
	#add_data(ambient_temp, pressure, humidity)
	#conn.commit() 
	#print(f"Last Inserted ID: {cur.lastrowid}")
	#print("\nTemperature: %0.1f C" % ambient_temp)
	#print("Humidity: %0.1f %%" % humidity)
	#print("Pressure: %0.1f hPa" % pressure)
	#time.sleep(60)
	
	
while True:
        #wind gusts/direction statistics
        store_wind_speed=[]
        store_wind_direction=["N"]
        start_time = time.time()
        while time.time() - start_time <= time_interval:
            #speed
            reset_wind()
            time.sleep(wind_interval)
            final_speed = calculate_speed(wind_interval)
            store_wind_speed.append(final_speed)
            #direction
            wind_dir=round(chan.voltage,1)
            if not wind_dir in direction:
                x=1
            else:
                store_wind_direction.append(direction[wind_dir])

        wind_gust = max(store_wind_speed) #max wind gust speed
        wind_speed = statistics.mean(store_wind_speed) #average wind speed
        wind_direction = statistics.mode(store_wind_direction) #mode wind direction
        ambient_temp=bme280.temperature
        pressure=bme280.pressure
        humidity=bme280.humidity
        rainfall=rain_count * BUCKET_SIZE
        reset_rainfall()
        add_data(ambient_temp, pressure, humidity, wind_direction, wind_speed, wind_gust, rainfall)
        conn.commit()
        #print(f"Last Inserted ID: {cur.lastrowid}")
        #print("\nTemperature: %0.1f C" % ambient_temp)
        #print("Humidity: %0.1f %%" % humidity)
        #print("Pressure: %0.1f hPa" % pressure)
        #print("Wind speed:" +  str(wind_speed) + "km/h")
        #print("Wind gust speed:" +  str(wind_gust) + "km/h")
        #print("Wind direction:"+str(wind_direction))
        #print()


