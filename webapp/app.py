import mariadb
from datetime import datetime
from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.secret_key = "super secret key"

@app.route('/')
def index():

    conn = mariadb.connect(
       user="pi",
       password="raspberry",
       host="localhost",
       database="weather")
    cur = conn.cursor()
    cur.execute("SELECT ambient_temperature,pressure,humidity,wind_speed,wind_gust_speed,wind_direction,rainfall,created FROM weather_measurements ORDER BY id DESC LIMIT 1")
    records = cur.fetchall()
    for row in records:
        temp=row[0]
        pre=row[1]
        hum=row[2]
        spee=row[3]
        gust=row[4]
        dire=row[5]
        rain=row[6]
        cre=row[7]
# rain over 24 hours
    cur.execute("SELECT rainfall,created FROM weather_measurements ORDER BY id DESC LIMIT 288")
    records_rain24 = cur.fetchall()
    rain24=[float(row[0]) for row in records_rain24]
    rain24=round(sum(rain24),2)
# rain over 30 days
    cur.execute("SELECT rainfall,created FROM weather_measurements ORDER BY id DESC LIMIT 8640")
    records_rain30 = cur.fetchall()
    rain30=[float(row[0]) for row in records_rain30]
    rain30=round(sum(rain30),2)
    cur.close()
    #spee=1.5
    #gust=3.5
    #dire="S"
    return render_template("index.html",temperature=temp,pressure=pre,humidity=hum,time=cre,windspeed=spee,windgust=gust,winddirection=dire,rainfall=rain,rain24=rain24,rain30=rain30)

@app.route('/chart', methods=('GET', 'POST'))
def chart():
    nm=250
    if request.method == 'POST':
        nm = request.form['Nm']
        #print(nm)
    if not nm:
        flash('Number is required!')
        nm=250
    conn = mariadb.connect(
       user="pi",
       password="raspberry",
       host="localhost",
       database="weather")
    cur = conn.cursor()
    cur.execute("SELECT ambient_temperature,pressure,humidity,wind_speed,wind_gust_speed,wind_direction,rainfall,created FROM weather_measurements ORDER BY id DESC LIMIT 1")
    records = cur.fetchall()
    for row in records:
        temp=row[0]
        pre=row[1]
        hum=row[2]
        spee=row[3]
        gust=row[4]
        dire=row[5]
        rain=row[6]
        cre=row[7]
    cur.execute("SELECT ambient_temperature,pressure,humidity,wind_speed,wind_gust_speed,wind_direction,rainfall,created,id FROM weather_measurements ORDER BY id DESC LIMIT "+str(nm))
    data=cur.fetchall()
    #spee=1.5
    #gust=3.5
    #dire="NE"
    list={"N":0,"NE":45,"E":90,"SE":135,"S":180,"SW":225,"W":270,"NW":315}
    temperatures=[float(row[0]) for row in data]
    pressures=[float(row[1]) for row in data]
    humiditys=[float(row[2]) for row in data]
    speeds=[float(row[3]) for row in data]
    gusts=[float(row[4]) for row in data]
    directions=[row[5] for row in data]
    list_dir=[directions.count("N"),directions.count("NE"),directions.count("E"),directions.count("SE"),directions.count("S"),directions.count("SW"),directions.count("W"),directions.count("NW")]
    rainfalls=[float(row[6]) for row in data]
    labels=[int(datetime.timestamp(row[7]))*1000 for row in data]
    #labels=[int(row[3]) for row in data]
    #print(list_dir)
    return render_template("chart.html",temperature=temp,pressure=pre,humidity=hum,time=cre,windspeed=spee,windgust=gust,winddirection=dire,rainfall=rain,labels=labels,temperatures=temperatures,pressures=pressures,humiditys=humiditys,speeds=speeds,gusts=gusts,directions=directions,rainfalls=rainfalls,list_dir=list_dir)
if __name__ == '__main__':
    app.run(host='0.0.0.0')
