import sys
import datetime
import eventlet
import json
import paho.mqtt.client as mqtt_client
from flask import Flask, render_template, request, redirect, url_for
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
import pymysql
import traceback
import requests
mqttClient = mqtt_client.Client()

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template('register.html')

@app.route('/registuser')
def getRigistRequest():
    db = pymysql.connect(host="localhost", user="root", password="1234", database="iotdb", charset="utf8")
    cursor = db.cursor()
    if(len(request.args.get('user')) == 0 or request.args.get('email') == 0 or request.args.get('password') == 0):
        return '注册失败，用户名、邮箱或密码不能为空！'

    sql = "INSERT INTO user(User_name, User_email,User_password) VALUES ('" + request.args.get('user') + "', '" + request.args.get('email') + "','" + request.args.get(
        'password') + "')"
    try:
        cursor.execute(sql)
        db.commit()
        db.close()
        return render_template('login.html')
    except:
        traceback.print_exc()
        db.rollback()
        db.close()
        return '注册失败，用户名或邮箱重复注册！'

@app.route('/login')
def getLoginRequest():
    db = pymysql.connect(host="localhost", user="root", password="1234", database="iotdb", charset="utf8")
    cursor = db.cursor()
    sql = "select * from user where User_name='"+request.args.get('user')+"' and User_password='"+request.args.get('password')+"'"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        print(len(results))
        db.commit()
        db.close()
        if len(results)==1:
            return redirect(url_for('main'))
        else:
            return '用户名或密码不正确'
    except:
        traceback.print_exc()
        db.rollback()
        return '登录失败'

@app.route('/main.html')
def main():
    db = pymysql.connect(host="localhost", user="root", password="1234", database="iotdb", charset="utf8")
    cursor = db.cursor()

    sql = "select Device_id from device"
    cursor.execute(sql)
    all = cursor.fetchall()
    numall = len(all)
    numonline = 5
    devnum = []
    devnum.append(numall)
    devnum.append(numonline)
    j = 0
    data = [0 for x in range(0, numall)]
    for i in all:
        sql = "select * from message where Device_id ='"+"".join(i)+"'"
        cursor.execute(sql)
        row = cursor.fetchall()
        data[j] = len(row)
        j = j+1
    db.commit()
    db.close()

    return render_template('main.html', all=all, data=data, devnum = devnum)


@app.route('/device_search')
def getdevicesearchRequest():
    db = pymysql.connect(host="localhost", user="root", password="1234", database="iotdb", charset="utf8")
    cursor = db.cursor()
    sql = "select * from message where Device_id = '" + request.args.get('devid') + "'"
    try:
        cursor.execute(sql)
        dbresult = cursor.fetchall()
        db.commit()
        db.close()
        return render_template('data_searchresult.html', u = dbresult)
    except:
        traceback.print_exc()
        db.rollback()
        db.close()

@app.route('/device_create')
def getdevicecreateRequest():
    db = pymysql.connect(host="localhost", user="root", password="1234", database="iotdb", charset="utf8")
    cursor = db.cursor()
    sql = "INSERT INTO device(Device_id, Device_name,Device_remark) VALUES ('" + request.args.get('devid') + "', '" + request.args.get('devname') + "','" + request.args.get(
        'devremark') + "')"
    try:
        cursor.execute(sql)
        db.commit()
        db.close()
        return render_template('device.html')
    except:
        traceback.print_exc()
        db.rollback()
        db.close()
        return '设备创建失败'

@app.route('/device_change')
def getdevicechangeRequest():
    db = pymysql.connect(host="localhost", user="root", password="1234", database="iotdb", charset="utf8")
    cursor = db.cursor()

    sql = "UPDATE device SET Device_name = '"+request.args.get('devcname')+"', Device_remark = '"+request.args.get('devcremark')+"' WHERE Device_id = '"+request.args.get('devcid')+"'"
    try:
        cursor.execute(sql)
        db.commit()
        db.close()
        return render_template('device.html')
    except:
        traceback.print_exc()
        db.rollback()
        db.close()
        return '设备修改失败'

@app.route('/trail_search')
def getdeviceTrailRequest():
    db = pymysql.connect(host="localhost", user="root", password="1234", database="iotdb", charset="utf8")
    cursor = db.cursor()

    sql = "select Message_alert from message where Device_id = '" + request.args.get('devid') + "' ORDER BY Message_time ASC"
    try:
        cursor.execute(sql)
    except:
        traceback.print_exc()
        db.rollback()
        db.close()

    all = cursor.fetchall()
    alert = [0.0 for x in range(0, len(all))]
    j = 0
    for i in all:
        alert[j] = i[0]
        j = j+1

    sql = "select Message_lat from message where Device_id = '" + request.args.get('devid') + "' ORDER BY Message_time DESC"
    try:
        cursor.execute(sql)
    except:
        traceback.print_exc()
        db.rollback()
        db.close()

    all2 = cursor.fetchall()
    dlat = [0.0 for x in range(0, len(all2))]
    j = 0
    for i in all2:
        dlat[j] = i[0]
        j = j + 1

    sql = "select Message_lng from message where Device_id = '" + request.args.get('devid') + "' ORDER BY Message_time DESC"
    try:
        cursor.execute(sql)
    except:
        traceback.print_exc()
        db.rollback()
        db.close()

    all3 = cursor.fetchall()
    dlng = [0.0 for x in range(0, len(all3))]
    j = 0
    for i in all3:
        dlng[j] = i[0]
        j = j + 1

    db.commit()
    db.close()

    return render_template('trail_result.html', num = len(all), alert =alert, dlat=dlat, dlng =dlng)

@app.route('/link_main')
def ret1():
    return redirect(url_for('main'))
@app.route('/link_data')
def ret2():
    return render_template('data_search.html')
@app.route('/search_return')
def ret2search():
    return render_template('data_search.html')
@app.route('/link_device')
def ret3():
    return render_template('device.html')
@app.route('/device_cr')
def ret3cr():
    return render_template('device_create.html')
@app.route('/device_ch')
def ret3ch():
    return render_template('device_change.html')
@app.route('/link_trail')
def ret4():
    return render_template('trail.html')
@app.route('/link_login')
def ret5():
    return render_template('login.html')
@app.route('/link_register')
def getretRegister():
    return render_template('register.html')



@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'])


@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])


@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    socketio.emit('mqtt_message', data=data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

def DB_num():
    db = pymysql.connect(host="localhost", user="root", password="1234", database="iotdb", charset="utf8")
    cursor = db.cursor()
    sql = "select * from message"
    cursor.execute(sql)
    return len(cursor.fetchall())

def mqtt_message_come(lient, userdata, msg):
    db = pymysql.connect(host="localhost", user="root", password="1234", database="iotdb", charset="utf8")
    cursor = db.cursor()

    message = str(msg.payload.decode("utf-8"))
    messageList = message.split("\"")
    messageList[2] = messageList[2].strip(':').strip(',')
    messageList[12] = messageList[12].strip(':').strip(',')
    messageList[14] = messageList[14].strip(':').strip(',')
    messageList[16] = messageList[16].strip(':').strip(',')
    messageList[18] = messageList[18].strip(':').strip(',').strip('}')
    message_id = DB_num()
    stmt = f'insert into message(Message_id, Device_id, Message_info, Message_value, Message_lat, Message_lng, Message_time, Message_alert) values ("{int(message_id)}","{messageList[5]}", "{messageList[9]}", "{int(messageList[18])}", "{float(messageList[12])}", "{float(messageList[14])}" ,"{messageList[16]}", "{int(messageList[2])}")'

    try:
        cursor.execute(stmt)
    except:
        traceback.print_exc()
        db.rollback()
        db.close()

    db.commit()
    db.close()


def mqtt_connect():
    mqttClient.connect('localhost', 1883, 60)
    mqttClient.loop_start()

def mqtt_subscribe(mqtt_topic):
    mqttClient.subscribe(mqtt_topic, 1)  # 主题为"test"
    mqttClient.on_message = mqtt_message_come  # 消息到来处理函数
    print(" mqtt_subscribe " + mqtt_topic)

if __name__ == '__main__':
    mqtt_topic = "testapp"
    mqtt_connect()
    mqtt_subscribe(mqtt_topic)

    socketio.run(app, host='127.0.0.1', port=5001, use_reloader=False, debug=True)