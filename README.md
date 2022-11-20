# AWS-Greengrass-JumpStart
Jumpstart of AWS greengrass

## Hardware
- Raspberry Pi 3b
- Raspberry Pi sense hat

## Software
- Raspbery Pi OS (64 bit)
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