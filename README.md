# AWS-Greengrass-JumpStart
Jumpstart of AWS greengrass

## Hardware
- Raspberry Pi 3b
- Raspberry Pi sense hat

## Software
- Raspbery Pi OS (64 bit) 
-- If it is lite, install pip
´´´bash
sudo apt install python3-pip
´´´
- Sense Hat SDK (by default installed in Pi OS) https://pythonhosted.org/sense-hat/ 
- AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html 
Note: AWS Cli only supports 64bit, to double check
```bash
root@kube-worker1:~# uname -m
aarch64
```

## Greengrass component
- aws.greengrass.Cli

Ref.
https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started.html


Deploy components
´´´bash
sudo /greengrass/v2/bin/greengrass-cli deployment create --recipeDir Components/recipes --artifactDir Components/artifacts --merge "com.example.sensehat.led=1.0.0"
´´´

List components
´´´bash
sudo /greengrass/v2/bin/greengrass-cli component list
´´´

Check logs
https://docs.aws.amazon.com/greengrass/v2/developerguide/monitor-logs.html
´´´bash
//system logs
sudo tail /greengrass/v2/logs/greengrass.log

// log of a componnet
sudo cat /greengrass/v2/logs/com.example.sensehat.joystick.log

´´´

remove component
´´´bash
sudo /greengrass/v2/bin/greengrass-cli --ggcRootPath /greengrass/v2 deployment create --remove "com.example.sensehat.joystick"
´´´

Get local debug console passwords
´´´bash
sudo /greengrass/v2/bin/greengrass-cli get-debug-password
´´´
