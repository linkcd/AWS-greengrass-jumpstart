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

        # iot core msg publishing
        iotcore_req = PublishToIoTCoreRequest()
        iotcore_req.topic_name = publishtopic
        iotcore_req.payload = bytes(msgstring, "utf-8")
        iotcore_req.qos = qos
        iotcore_operation = ipc_client.new_publish_to_iot_core()
        iotcore_operation.activate(iotcore_req)
        iotcore_future = iotcore_operation.get_response()
        iotcore_future.result(TIMEOUT)

        # ipc local msg publishing
        ipc_request = PublishToTopicRequest()
        ipc_request.topic = publishtopic
        ipc_publish_message = PublishMessage()
        ipc_publish_message.binary_message = BinaryMessage()
        ipc_publish_message.binary_message.message = bytes(msgstring, "utf-8")

        ipc_request.publish_message = ipc_publish_message
        ipc_operation = ipc_client.new_publish_to_topic()
        ipc_operation.activate(ipc_request)
        ipc_future = ipc_operation.get_response()
        ipc_future.result(TIMEOUT)

while True:
    publishJoystickEvents(publishtopic)


print("Joystick event detect finished")