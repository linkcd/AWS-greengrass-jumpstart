# AWS-Greengrass-JumpStart
This repo is a jumpstart demo of AWS greengrass. It has 2 customized components to demostrate 
- Local communication via IPC between components
- Device to cloud communication via MQTT
- Cloud to device communication via device shadow

## Component overview
### 1. com.example.sensehat.joystick
This component send the joystick events (move up/down/left/right, press/hold/release) to local IPC and IoTCore
The IPC and IoTCore topic can be found in the [recipe](./Components/recipes/com.example.sensehat.joystick-1.0.0.json)

### 2. com.example.sensehat.led
This component does the following:
- Maintain a number (0-9) and display it on LED
- When received joystick events via IPC
  - Joystick up/down: increse/decrese the number
  - Joystick left/right: change LED display to a random color
  - Joystick press down: toggle LED number display on/off
- Have a IoT Core Shadow, so AWS IoT Core can update the value of the number remotely.
The IPC and IoTCore topic, shadown name etc can be found in the [recipe](./Components/recipes/com.example.sensehat.led-1.0.0.json)

## Hardware
- Raspberry Pi 3b
- Raspberry Pi [Sense Hat](https://www.raspberrypi.com/products/sense-hat/)

## Software
- Raspbery Pi OS (64 bit) 
- Sense Hat SDK 

If you are using the Pi OS lite version, remember to install needed packages
```bash
sudo apt update
sudo apt install python3-pip
sudo apt install git
sudo apt install sense-hat #need reboot
```

## Install Greengrass software
Follow the steps in https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started.html

As a part of the installtion, create an IAM user with minimal permission (the role json can be found in [minimal-greengrass-policy-for-device.json](./PolicyDocuments/minimal-greengrass-policy-for-device.json)). You can deactive the key/secret after the device is provisioned.  

## Deploy Greengrass components
- aws.greengrass.Cli
- aws.greengrass.ShadowManager
- aws.greengrass.LocalDebugConsole

## Develop your own components
### Setup development environment
1. Install VS Code with Remote SSH extension
2. In Remote SSH extension, enable ports forwarding for 1441 and 1442. Ensure it is set to HTTPS (not http by default). This is for access Greengrass LocalDebugConsole from your development laptop.

Check the development tips in the appendix

## Appendix
### Useful commands
You can run in on Pi via VS Code remote SSH terminal. For deployment, 

#### Deploy a component
```bash
# ensure your terminal is at the root of this repo, that has folder Components
sudo /greengrass/v2/bin/greengrass-cli deployment create --recipeDir Components/recipes --artifactDir Components/artifacts --merge "com.example.sensehat.led=1.0.0"
```

#### Remove a component
```bash
sudo /greengrass/v2/bin/greengrass-cli --ggcRootPath /greengrass/v2 deployment create --remove "com.example.sensehat.led"
```

#### List components
```bash
sudo /greengrass/v2/bin/greengrass-cli component list
```

#### Check logs for troubleshooting
The log file structure is at https://docs.aws.amazon.com/greengrass/v2/developerguide/monitor-logs.html
```bash
#greengrass system logs
sudo tail /greengrass/v2/logs/greengrass.log

# log of a componnet
sudo cat /greengrass/v2/logs/com.example.sensehat.joystick.log
```

#### Use local debug console
After you deployed the aws.greengrass.LocalDebugConsole component and enabled 1441 and 1442 port forwarding, you can access the console https://localhost:1441/ from you local laptop

1. Get access password (user name is "debug")
```bash
sudo /greengrass/v2/bin/greengrass-cli get-debug-password
```

2. The console is using a self-signed https certificate, use firefox to bypass the warning (Edge cannot bypass)

#### More tips/references:
1. [Greengrass workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/5ecc2416-f956-4273-b729-d0d30556013f/en-US)
2. [Tips/troubleshooting from the workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/5ecc2416-f956-4273-b729-d0d30556013f/en-US/chapter13-tips-troubleshoot)
3. [AWS IoT Youtube channel](https://www.youtube.com/c/AWSIoTChannel)
4. [AWSomeIoT Youtube channel](https://www.youtube.com/@awsomeiot1448)
5. [AWS Greengrass tutorials](https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html)