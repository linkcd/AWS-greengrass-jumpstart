import sys
import time
import traceback
import json

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    #for iot core msg
    IoTCoreMessage,
    QOS,
    PublishToIoTCoreRequest,
    SubscribeToIoTCoreRequest,

    #for local ipc msg
    PublishToTopicRequest,
    PublishMessage,
    BinaryMessage
)

def myRoundFun(x):
    round_parameter = 2
    return round(x, round_parameter)

def get_sensor_data():
    #set_imu_config(compass_enabled, gyro_enabled, accel_enabled)
    #sense.set_imu_config(True, True, True)
    orientation = sense.get_orientation()
    pitch = myRoundFun(orientation["pitch"])
    roll = myRoundFun(orientation["roll"])
    yaw = myRoundFun(orientation["yaw"])
    #print("p: %s, r: %s, y: %s" % (pitch,roll,yaw))

    # sense.set_imu_config(True, False, False) #disable the gyroscope and accelerometer then gets the direction of North from the magnetometer in degrees.
    # north = sense.get_compass()
    # print("North: %s" % north)
    
    # sense.set_imu_config(False, True, False) #disable the magnetometer and accelerometer then gets the current orientation from the gyroscope only.
    # gyro_only = sense.get_gyroscope()
    # print("p: {pitch}, r: {roll}, y: {yaw}".format(**gyro_only))

    # sense.set_imu_config(False, False, True) #disable the magnetometer and gyroscope then gets the current orientation from the accelerometer only.
    # accel_only = sense.get_accelerometer()
    # print("p: {pitch}, r: {roll}, y: {yaw}".format(**accel_only))

    temperature = sense.get_temperature()
    pressure = sense.get_pressure()
    humidity = sense.get_humidity()

    temperature = myRoundFun(temperature)
    pressure = myRoundFun(pressure)
    humidity = myRoundFun(humidity)
    
    #msg = "Temperature = %s, Pressure=%s, Humidity=%s" % (temperature, pressure, humidity)

    message =  {
        "timemillis": round(time.time() * 1000),
        "pitch": pitch,
        "roll": roll,
        "yaw": yaw,
        "temperature": temperature,
        "pressure": pressure,
        "humidity": humidity
    }
    return message


def publishSensorData(ipc_client, iotcore_publishtopic):

    try:
        

        message = get_sensor_data()
        msgstring = json.dumps(message)

        # iot core msg publishing
        iotcore_req = PublishToIoTCoreRequest()
        iotcore_req.topic_name = iotcore_publishtopic
        iotcore_req.payload = bytes(msgstring, "utf-8")
        iotcore_req.qos = qos
        iotcore_operation = ipc_client.new_publish_to_iot_core()
        iotcore_operation.activate(iotcore_req)
        iotcore_future = iotcore_operation.get_response()
        iotcore_future.result(TIMEOUT)
    
    except Exception as e:
        print("Error publishSensorData:", type(e), e)

from sense_hat import SenseHat 
sense = SenseHat()

iotcore_publishtopic = str(sys.argv[1])
puiblish_interval = int(sys.argv[2])

TIMEOUT = 10
qos = QOS.AT_LEAST_ONCE
subqos = QOS.AT_MOST_ONCE


# Have to leave this out of the loop, otherewise will eat all memory of pi.
ipc_client = awsiot.greengrasscoreipc.connect()

while True:
    publishSensorData(ipc_client, iotcore_publishtopic)
    time.sleep(puiblish_interval)
    


