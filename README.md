# MQTT Sky Remote


### Introduction

I've recently been working on my Home Automation system and wanted to integrate my Sky (UK Satellite Television) box. They kindly provide a basic method of sending commands over TCP to a listening port.

MQTT appears to have become the defacto standard for home automation stuff so I chose to use MQTT to interface with the Sky Box. 

All contributions and feedback are much appreciated.

### Features

* Subscribes to an MQTT broker and sends the appropriate command over IP
* Supports multiple Sky HD and Sky Q set top boxes
* Supports all known remote control commands
* Supports username and password MQTT login
* Supports MQTT over TLS.

### Caveats

* I'm using the Python twisted framework and it adds a layer of abstraction between what's going on and whats being logged, which I'm not very happy with
* Use at your own risk

### Installation

    git clone
    
### Configuration

Copy the configuration example to mqtt-sky-remote.cfg-

    cp mqtt-sky-remote-EXAMPLE.cfg mqtt-sky-remote.cfg
    
Edit the file-
    nano mqtt-sky-remote.cfg

It should be self explanatory. Any section below 'MQTT' is considered to be a Sky Box- 

    [GLOBAL]
    FILE: /tmp/mqtt-sky-remote.log
    HANDLERS: console-timed,file-timed
    LEVEL: DEBUG
    NAME: mqtt-sky-remote
    LOG_TWISTED: False
    
    [MQTT]
    HOST: 10.0.130.242
    PORT: 1883
    USERNAME: username
    PASSWORD: password
    TLS: False
    CERTS: ./certs
    
    [LOUNGE_TV]
    HOST: 10.0.130.133
    SKY_Q: True
    
    [BEDROOM_TV]
    HOST: 10.0.130.134
    SKY_Q: False
    
### Usage

Start MQTT Sky Remote-

    python mqtt-sky-remote.py

Send a command using your MQTT publisher of choice with the following topic-

   sky/[NAME OF BOX]/send

The message body should be one of the supported commands listed below.

### Supported Commands

The following Remote Commands are supported-

    power
    select
    backup
    dismiss
    channelup
    channeldown
    interactive
    sidebar
    help
    services
    search
    tvguide
    home
    i
    text
    up
    down
    left
    right
    red
    green
    yellow
    blue
    0
    1
    2
    3
    4
    5
    6
    7
    8
    9
    play
    pause
    stop
    record
    fastforward
    rewind
    boxoffice
    sky

### Licence

This project is licensed under the [Creative Commons CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) licence.

You are free to share and adapt the code as required, however you *must* give appropriate credit and indicate what changes have been made. You must also distribute your adaptation under the same license. Commercial use is prohibited.

**N.B: Sky may have other licenses covering the usage of their Remote over IP Protocol, please honor them!**

### Acknowledgments

  A big thanks goes to [dalhundal](https://github.com/dalhundal) who created the excellent [sky-remote](https://github.com/dalhundal/sky-remote) tool written in NodeJS, which I studied to learn more about the Sky Remote protocol.
