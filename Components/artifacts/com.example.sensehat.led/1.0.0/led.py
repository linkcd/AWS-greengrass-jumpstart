import sys
import time
import json
import traceback
import concurrent.futures
import random
from enum import Enum
from sense_hat import SenseHat

import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    UnauthorizedError,
    GetThingShadowRequest,
    UpdateThingShadowRequest
)

class Device_Status(Enum):
    STARTUP = "device start up"
    UPDATED_BY_SHADOW = "device updated by shadow"
    UPDATED_BY_LOCAL = "device updated by local"

sense = SenseHat()

CURRENT_STATUS = Device_Status.STARTUP
CURRENT_NUMBER = int(sys.argv[1])
CURRENT_R = 255
CURRENT_B = 255
CURRENT_G = 255
CURRENT_DISPLAY_ON = True
THING_NAME = "PiWithSenseHat"
SHADOW_NAME = "NumberLEDNamedShadow"
TIMEOUT = 10
JOYSTICK_TOPIC = "ipc/joystick"

ipc_client = GreengrassCoreIPCClientV2()

def on_stream_event(event: SubscriptionResponseMessage) -> None:
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

        new_number = CURRENT_NUMBER

        if msg_direction == "up":
            #increase number until 9
            new_number = min(CURRENT_NUMBER + 1, 9)
        
        if msg_direction == "down":
            #decrease number until 0
            new_number = max(CURRENT_NUMBER - 1, 0)

        if msg_direction == "left" or msg_direction == "right":
            #get random new color
            CURRENT_R = random.randint(0, 255)
            CURRENT_B = random.randint(0, 255)
            CURRENT_G = random.randint(0, 255)

        if msg_direction == "middle":
            #toggle led display on/off
            CURRENT_DISPLAY_ON = not CURRENT_DISPLAY_ON
        
        do_update_device(new_number, Device_Status.UPDATED_BY_LOCAL)

    except:
        traceback.print_exc()

def on_stream_error(error: Exception) -> bool:
    print('Received a stream error.', file=sys.stderr)
    traceback.print_exc()
    return False  # Return True to close stream, False to keep stream open.

def on_stream_closed() -> None:
    print('Subscribe to topic stream closed.')

def do_update_device(new_number, new_status):
    global CURRENT_NUMBER
    global CURRENT_STATUS

    CURRENT_NUMBER = new_number
    CURRENT_STATUS = new_status
    
    # update display
    if CURRENT_DISPLAY_ON:
        sense.show_letter(str(CURRENT_NUMBER), text_colour=[CURRENT_R,CURRENT_G,CURRENT_B])
    else:
        sense.clear()

    #report device update back to shadow
    print("update shadow back when the device is updated (by local or by shadow)...")
    report_thing_shadow_back(THING_NAME, SHADOW_NAME) 


#Get the shadow from the local IPC
def update_device_by_thing_shadow(thingName, shadowName):
    print("getting shadow document to check if we need to update device...")
    
    try:
        # retrieve the GetThingShadow response after sending the request to the IPC server
        get_shadow_result = ipc_client.get_thing_shadow(thing_name=thingName, shadow_name=shadowName)

        #convert string to json object
        shadow_json = json.loads(get_shadow_result.payload)

        # set device value by shadow, if reported number and desired number are mismatch
        if 'desired' in shadow_json['state'] and 'number' in shadow_json['state']['desired']:
            number_from_shadow = int(shadow_json['state']['desired']['number'])
            if CURRENT_NUMBER != number_from_shadow:
                do_update_device(number_from_shadow, Device_Status.UPDATED_BY_SHADOW)
                print("Device updated to match the newly fetched shadow:" + json.dumps(shadow_json))
        
    except Exception as e:
        print("Error get shadow", type(e), e)
        traceback.print_exc()
        # except ResourceNotFoundError | UnauthorizedError | ServiceError


#Set the local shadow using the IPC
def report_thing_shadow_back(thingName, shadowName):
    #create payload
    currentstate =  {
        "state":{
            "reported":{
                "status": CURRENT_STATUS.value,
                "number": CURRENT_NUMBER
            }
        }
    }

    # if the latest update was done by local joystick, we want to keep the value
    # we will have to set the value to remote shadow desired value
    # otherwise the remote shadow will keep overriding the local new values.
    if CURRENT_STATUS == Device_Status.UPDATED_BY_LOCAL:
        currentstate['state']["desired"] = {
            "number": CURRENT_NUMBER
        }

    print("New shadow to be reported:" + json.dumps(currentstate))
    payload = bytes(json.dumps(currentstate), "utf-8")

    try:
        result = ipc_client.update_thing_shadow(thing_name=thingName, shadow_name=shadowName, payload=payload)
        jsonmsg = json.loads(result.payload)
        print("Shadow updated successfully.")
        return result.payload
        
    except Exception as e:
        print("Error update shadow", type(e), e)
        traceback.print_exc()
        # except ConflictError | UnauthorizedError | ServiceError


# ------ The code exeuction begins here ------ 

# Subscription to local IPC joystick events.
_, operation = ipc_client.subscribe_to_topic(topic=JOYSTICK_TOPIC, on_stream_event=on_stream_event,
                                                on_stream_error=on_stream_error, on_stream_closed=on_stream_closed)
print('Successfully subscribed to topic: ' + JOYSTICK_TOPIC)

# First time report initial status
print("component starting, report initial status to shadow... ")
report_thing_shadow_back(THING_NAME, SHADOW_NAME)   

# Loop listening to shadow and refresh display number and color
while True:
    update_device_by_thing_shadow(THING_NAME, SHADOW_NAME)
    time.sleep(10) #cloud to device shadow sync: every 10 seconds




