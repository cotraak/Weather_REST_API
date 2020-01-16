from flask import Flask, request, redirect, url_for
from flask_jsonpify import jsonify
from flask import render_template
from flask import abort
from flask import Response
from flask_api import status
import json
from flaskext.mysql import MySQL
import pandas as pd
import requests
from datetime import datetime, timedelta
import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    mpl.use('Agg')
import matplotlib.pyplot as plt
import base64
import io

app = Flask(__name__)
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'cloud'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

db = mysql.connect()
cursor = db.cursor()

@app.route('/')
def homepage():
    return  render_template('forecast.html')

@app.route('/historical/', methods=['GET','POST'])   #lists all the dates
def historical():
    if(request.method=='GET'):
        dates_list = []
        cursor.execute("select DATE from dailyweather")
        query=cursor.fetchall()
        my_hist = [i[0] for i in query]
        for item in my_hist:
            a = {"DATE":str(item)}
            dates_list.append(a)
        js = json.dumps(dates_list)
        return js, 200
    else:
       l=request.get_json()
       d=l['DATE']
       tmax=l['TMAX']
       tmin=l['TMIN']
       obj = {}
       cursor.execute("select DATE from dailyweather")
       q=cursor.fetchall()
       list=[i[0] for i in q]
       x=0
       for item in list:
           if(int(d)==item):
               x=1
       if(x==1):
		cursor.execute("update dailyweather set TMAX=%f, TMIN=%f where DATE=%d" %(float(tmax),float(tmin),int(d)))
       else:
        cursor.execute("insert into dailyweather values(%d,%f,%f)" % (int(d),float(tmax),float(tmin)))
       db.commit()
       obj={"DATE":str(d)}
       return jsonify(obj), 201

@app.route('/historical/<string:DATE>', methods=['GET'])    #gets the weather info of a particular day
def get_info(DATE):
    obj = {}
    l=[]
    cursor.execute("select DATE,TMAX,TMIN from dailyweather where DATE =%d" % int(DATE))
    q=cursor.fetchall()
    if(len(q)>0):
        for i in range(3):
            l.append(q[0][i])
        obj =  {
                "DATE": str(l[0]),
                "TMAX": float(l[1]),
                "TMIN": float(l[2])
                }
        return jsonify(obj), 200
    else:
        return '', 404

@app.route('/historical/<int:DATE>', methods=['DELETE'])
def del_info(DATE):
    obj={}
    l=[]
    cursor.execute("select DATE,TMAX,TMIN from dailyweather where DATE=%d" % int(DATE))
    query=cursor.fetchall()
    cursor.execute("delete from dailyweather where DATE=%d" % int(DATE))
    db.commit()
    if(len(query)>0):
        for i in range(3):
			 l.append(str(query[0][i]))
        obj =  {
                "DATE": l[0],
                "TMAX": l[1],
                "TMIN": l[2]
                }
        return jsonify(obj), 200
    else:
        return '', 204

@app.route('/forecast/<DATE>', methods=['GET'])   #forecasts weather info of the next 7days
def forecast(DATE):
    lst_dates = []
    lst_obj = []
    current_date = pd.to_datetime(DATE,format='%Y%m%d')
    stop_date = current_date+timedelta(days=7)
    while current_date<stop_date:
        lst_dates.append(str(pd.to_datetime(current_date)).split(' ')[0].replace("-",""))
        current_date = current_date+timedelta(days=1)
    for curr_date in lst_dates:
        cursor.execute("select DATE,TMAX,TMIN from dailyweather where DATE =%d" % int(curr_date))
        query=cursor.fetchall()
        if (len(query) > 0):
            obj = {
                    "DATE": curr_date,
                    "TMAX": float(query[0][1]),
                    "TMIN": float(query[0][2])
                    }
            lst_obj.append(obj)
        else:
            cursor.execute("select ROUND(RAND()*(80-75+1),1)+75")
            q=cursor.fetchall()
            cursor.execute("select ROUND(RAND()*(50-45+1),1)+45")
            q1=cursor.fetchall()
            obj = {
                    "DATE": curr_date,
                    "TMAX": float(q[0][0]),
                    "TMIN": float(q1[0][0])
                }
            lst_obj.append(obj)
    return jsonify(lst_obj), 200

@app.route('/forecast',methods=['GET','POST'])
def plot_graph():
    DATE=int(request.form['date'])
    lst_dates = []
    lst = []
    tmax_lst=[]
    tmin_lst=[]
    current_date = pd.to_datetime(DATE,format='%Y%m%d')
    stop_date = current_date+timedelta(days=7)
    while current_date<stop_date:
        lst_dates.append(str(pd.to_datetime(current_date)).split(' ')[0].replace("-",""))
        current_date = current_date+timedelta(days=1)
    for curr_date in lst_dates:
        cursor.execute("select DATE,TMAX,TMIN from dailyweather where DATE =%d" % int(curr_date))
        query=cursor.fetchall()
        if (len(query) > 0):
            tmax_lst.append(query[0][1])
            tmin_lst.append(query[0][2])
        else:
            cursor.execute("select ROUND(RAND()*(80-75+1),1)+75")
            q=cursor.fetchall()
            cursor.execute("select ROUND(RAND()*(50-45+1),1)+45")
            q1=cursor.fetchall()
            tmax_lst.append(q[0][0])
            tmin_lst.append(q1[0][0])
    img = io.BytesIO()
    plt.xlabel('Date')
    plt.ylabel('Temperature')
    plt.plot(lst_dates, tmax_lst, color='g',label='TMAX')
    plt.plot(lst_dates, tmin_lst, color='r', label='TMIN')
    plt.legend()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return render_template('forecast.html', value='data:image/png;base64,{}'.format(graph_url))

if __name__ == '__main__':
     app.run(host='0.0.0.0',debug=True,port=80)
