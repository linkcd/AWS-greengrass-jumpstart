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

topic = "pihat/joystick"

from sense_hat import SenseHat
sense = SenseHat()

CURRENT_NUMBER = int(sys.argv[1])
CURRENT_R = 255
CURRENT_B = 255
CURRENT_G = 255
CURRENT_DISPLAY_ON = True

#         

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


try:
    ipc_client = awsiot.greengrasscoreipc.connect()

    request = SubscribeToTopicRequest()
    request.topic = topic
    handler = StreamHandler()
    operation = ipc_client.new_subscribe_to_topic(handler)
    future = operation.activate(request)
    
    try:
        future.result(TIMEOUT)
        print('Successfully subscribed to topic: ' + topic)
    except concurrent.futures.TimeoutError as e:
        print('Timeout occurred while subscribing to topic: ' + topic, file=sys.stderr)
        raise e
    except UnauthorizedError as e:
        print('Unauthorized error while subscribing to topic: ' + topic, file=sys.stderr)
        raise e
    except Exception as e:
        print('Exception while subscribing to topic: ' + topic, file=sys.stderr)
        raise e

    # Keep the main thread alive, or the process will exit.
    try:
        while True:
            if CURRENT_DISPLAY_ON:
                sense.show_letter(str(CURRENT_NUMBER), text_colour=[CURRENT_R,CURRENT_G,CURRENT_B])
            else:
                sense.clear()
            #time.sleep(10)
            pass
    except InterruptedError:
        print('Subscribe interrupted.')
except Exception:
    print('Exception occurred when using IPC.', file=sys.stderr)
    traceback.print_exc()
    exit(1)