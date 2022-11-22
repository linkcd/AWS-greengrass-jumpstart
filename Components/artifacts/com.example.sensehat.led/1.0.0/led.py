import sys
import time
import json
import traceback
import concurrent.futures
import random

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    UnauthorizedError
)

from awsiot.greengrasscoreipc.model import GetThingShadowRequest
from awsiot.greengrasscoreipc.model import UpdateThingShadowRequest

topic = "ipc/joystick"

from sense_hat import SenseHat
sense = SenseHat()

CURRENT_NUMBER = int(sys.argv[1])
CURRENT_R = 255
CURRENT_B = 255
CURRENT_G = 255
CURRENT_DISPLAY_ON = True

THING_NAME = "PiWithSenseHat"
SHADOW_NAME = "NumberLEDNamedShadow"

TIMEOUT = 10


class StreamHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        global CURRENT_NUMBER
        global CURRENT_R
        global CURRENT_B
        global CURRENT_G
        global CURRENT_DISPLAY_ON
        
        try:
            
            raw_payload = str(event.binary_message.message, "utf-8")
            print("Parsing raw payload: " + raw_payload)

            payload = json.loads(raw_payload)

            msg_direction = payload["direction"]
            msg_action = payload["action"]

            print("Received direction: " + msg_direction)
            print("Received action: " + msg_action)

            if msg_action != "pressed":
                #ignore action that is NOT pressed
                return

            if msg_direction == "up":
                #increase number until 9
                CURRENT_NUMBER = min(CURRENT_NUMBER + 1, 9)
            
            if msg_direction == "down":
                #decrease number until 0
                CURRENT_NUMBER = max(CURRENT_NUMBER - 1, 0)

            if msg_direction == "left" or msg_direction == "right":
                #get random new color
                CURRENT_R = random.randint(0, 255)
                CURRENT_B = random.randint(0, 255)
                CURRENT_G = random.randint(0, 255)

            if msg_direction == "middle":
                #toggle led display on/off
                CURRENT_DISPLAY_ON = not CURRENT_DISPLAY_ON
                
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        print("Received a stream error.", file=sys.stderr)
        traceback.print_exc()
        return False  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        print('Subscribe to topic stream closed.')


#initial settings for the reported states of the device
currentstate =  {
   "state":{
      "reported":{
         "status":"startup",
         "number":CURRENT_NUMBER
      }
   }
}

#Get the shadow from the local IPC
def sample_get_thing_shadow_request(ipc_client, thingName, shadowName):
    global CURRENT_NUMBER

    try:
        # create the GetThingShadow request
        get_thing_shadow_request = GetThingShadowRequest()
        get_thing_shadow_request.thing_name = thingName
        get_thing_shadow_request.shadow_name = shadowName

        print(thingName)
        print(shadowName)
        
        # retrieve the GetThingShadow response after sending the request to the IPC server
        op = ipc_client.new_get_thing_shadow()
        op.activate(get_thing_shadow_request)
        fut = op.get_response()
        
        result = fut.result(TIMEOUT)

        #convert string to json object
        jsonmsg = json.loads(result.payload)

        #print desired states 
        CURRENT_NUMBER = int(jsonmsg['state']['desired']['number'])

        print("get shadow is:" + json.dumps(jsonmsg))
        return result.payload
        
    except Exception as e:
        print("Error get shadow", type(e), e)
        # except ResourceNotFoundError | UnauthorizedError | ServiceError


#Set the local shadow using the IPC
def sample_update_thing_shadow_request(ipc_client, thingName, shadowName, payload):
    try:
        # create the UpdateThingShadow request
        update_thing_shadow_request = UpdateThingShadowRequest()
        update_thing_shadow_request.thing_name = thingName
        update_thing_shadow_request.shadow_name = shadowName
        update_thing_shadow_request.payload = payload
                        
        # retrieve the UpdateThingShadow response after sending the request to the IPC server
        op = ipc_client.new_update_thing_shadow()
        op.activate(update_thing_shadow_request)
        fut = op.get_response()
        
        result = fut.result(TIMEOUT)

        jsonmsg = json.loads(result.payload)
        print("get shadow is:" + json.dumps(jsonmsg))
        return result.payload
        
    except Exception as e:
        print("Error update shadow", type(e), e)
        # except ConflictError | UnauthorizedError | ServiceError


### Subscribe IPC call back###
ipc_client = awsiot.greengrasscoreipc.connect()

request = SubscribeToTopicRequest()
request.topic = topic
handler = StreamHandler()
operation = ipc_client.new_subscribe_to_topic(handler)
future = operation.activate(request)
future.result(TIMEOUT)
print('Successfully subscribed to topic: ' + topic)


# Loop listening to shadow and refresh display number and color
while True:
    print("getting shadow document")
    #check document to see if led states need updating
    sample_get_thing_shadow_request(ipc_client, THING_NAME, SHADOW_NAME)
    time.sleep(10)

    #set current status to good and update actual value of led output to reported
    print("setting shadow good")
    currentstate['state']['reported']['status'] = "good"
    currentstate['state']['reported']['number'] = CURRENT_NUMBER
    sample_update_thing_shadow_request(ipc_client, THING_NAME, SHADOW_NAME, bytes(json.dumps(currentstate), "utf-8"))   

    time.sleep(1)

    if CURRENT_DISPLAY_ON:
        sense.show_letter(str(CURRENT_NUMBER), text_colour=[CURRENT_R,CURRENT_G,CURRENT_B])
    else:
        sense.clear()


