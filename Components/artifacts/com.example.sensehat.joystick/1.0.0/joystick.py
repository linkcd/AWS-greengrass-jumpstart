import sys
import time
import traceback
import json

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    PublishToIoTCoreRequest,
    SubscribeToIoTCoreRequest
)

from sense_hat import SenseHat
sense = SenseHat()

publishtopic = str(sys.argv[1])
TIMEOUT = 10
qos = QOS.AT_LEAST_ONCE
subqos = QOS.AT_MOST_ONCE

ipc_client = awsiot.greengrasscoreipc.connect()

def publishJoystickEvents(publishtopic):
    for event in sense.stick.get_events():
        
        message =  {
            "timemillis": round(time.time() * 1000),
            "direction": event.direction,
            "action": event.action
        }

        msgstring = json.dumps(message)

        pubrequest = PublishToIoTCoreRequest()
        pubrequest.topic_name = publishtopic
        pubrequest.payload = bytes(msgstring, "utf-8")
        pubrequest.qos = qos
        operation = ipc_client.new_publish_to_iot_core()
        operation.activate(pubrequest)
        future = operation.get_response()
        future.result(TIMEOUT)

while True:
    publishJoystickEvents(publishtopic)


print("Joystick event detect finished")