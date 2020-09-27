# PurpleRelay v0.10.0
[![](https://img.shields.io/docker/pulls/nathanls/purplerelay.svg)](https://hub.docker.com/r/nathanls/purplerelay)
[![](https://img.shields.io/github/license/Nathan-LS/PurpleRelay.svg)](https://github.com/Nathan-LS/PurpleRelay/blob/master/LICENSE)
[![](https://img.shields.io/discord/379777846144532480.svg)](https://discord.gg/Np3FCUn) 

PurpleRelay relays and routes messages from [Pidgin/Finch](https://www.pidgin.im/) to [Discord](https://discord.com/) utilizing [D-BUS](https://www.freedesktop.org/wiki/Software/dbus/) for IPC(inter-process communication). 

PurpleRelay is configured through a ```routes.json``` file to filter incoming messages received through Pidgin using regular expressions that are then relayed to specified Discord channels. 
Any instant messaging / chat account that Pidgin supports or through [plugins](https://www.pidgin.im/plugins/) should theoretically be capable of being relayed to Discord.

Relaying is simple to set up and there is even a [Docker image](https://hub.docker.com/r/nathanls/purplerelay) available utilizing Finch for a headless GUI-less setup. 

## Table of contents
- [Table of contents](#table-of-contents)
- [Relay Configuration](#relay-configuration)
  * [Reference](#reference)
  * [Example](#example)
- [Docker](#docker)
  * [Quick reference](#quick-reference)
  * [Start an instance](#start-an-instance)
  * [Where to Store Data](#where-to-store-data)
  * [Docker Stack and Compose](#docker-stack-and-compose)
- [Running from source](#running-from-source)
  * [Requirements](#requirements)
  * [Installing dependencies and running](#installing-dependencies-and-running)

## Relay Configuration
All possible configuration for the bot is done in the ```routes.json``` file. There is a provided ```routes-example.json``` in this repo for a simple setup.

### Reference
- **config**: (dict) - Core config key-value pairs
    - **token**: (string, required) - The Discord bot token from [Discord developers](https://discordapp.com/developers/applications/) that will be used to join and send messages to relay target channels.
    - **max_dbus_reconnect**: (integer, default: 5) - The maximum number of D-BUS reconnection attempts to make in the event of a lost IPC connection to Pidgin/Finch before exiting with code 1. Set to ```0``` to disable and infinitely retry reconnecting to Pidgin/Finch. 
    - **bot_status**: (bool, default: true) - Change the bot status color indicator for D-BUS errors or chat disconnects and set the activity indicator to display currently connected/total enabled Pidgin/Finch accounts. Setting this to ```false``` will disable updating the status indicator and activity so the bot will always appear as online(green).
- **routes**: (list, default: []) - A list containing multiple relay route dictionaries. A relay route dictionary defines a set of regex rules for input messages that can then be routed to multiple Discord targets channels.
    - *route dictionary definition*
        - **name**: (string, default: "relay_ID") - The identifier name used in logging and the console. This is simply an internal identifier and isn't relayed.
        - **src**: (string) - The service type of the source Pidgin/Finch account (ex: IRC, XMPP). This does nothing at the moment but may be implemented in the future for chat source specific overrides and handling.
        - **filter_input_account**: (string, default: .*) - The account input filter regex. A Pidgin/Finch message must match this and all other input regex filters to be relayed to targets. Regex DOTALL flag is enabled.
        - **filter_input_sender**: (string, default: .*) - The sender input filter regex. A Pidgin/Finch message must match this and all other input regex filters to be relayed to targets. Regex DOTALL flag is enabled.
        - **filter_input_conversation**: (string, default: .*) - The conversation input filter regex. A Pidgin/Finch message must match this and all other input regex filters to be relayed to targets. Regex DOTALL flag is enabled.
        - **filter_input_message**: (string, default: .*) - The message input filter regex. A Pidgin/Finch message must match this and all other input regex filters to be relayed to targets. Regex DOTALL flag is enabled.
        - **filter_input_flags**: (string, default: .*) - The flags input filter regex. A Pidgin/Finch message must match this and all other input regex filters to be relayed to targets. Regex DOTALL flag is enabled.
        - **targets**: (list, default: []) - A list containing multiple relay target dictionaries. 
            - *relay target dictionary definition*
                - **name**: (string, default: "route_ID") - The identifier name used in logging and the console. This is simply an internal identifier and isn't relayed.
                - **channel_id**: (integer, required) - The target Discord channel ID.
                - **title**: (string, default: "") - The title prefixed to a relayed message. This title is included in the relayed message and can be anything.
                - **embed**: (bool, default: true) - Post message to this target as a Discord embed instead of plaintext.
                - **embed_color**: (integer, default: 4659341) - The color of a Discord embed (if embed=true).
                - **timestamp**: (bool, default: true) - Display the timestamp of the source message prefixed to relayed messages.
                - **mention**: (string, default: "") - The mention prefixed to relayed messages. Examples: "@here", "@everyone", "@group"
                - **strip_mention**: (bool, default: false) - Strips "@here" and "@everyone" from source messages before relaying the message. This option does not conflict with the "mention" setting for targets.
                - **spam_control_seconds**: (integer, default: false) - Do not relay a message if the same content has be successfully relayed in this many seconds ago. Setting this to ```0``` disables spam control and duplicate messages can be relayed. 
- **logger**: (dict) - Logger configuration
    - **log_purple_messages**: (bool, default: true) - Logs all messages received by Pidgin/Finch into ./logs/purpleChat/. Includes time, account, sender, conversation, flags, message_raw/html, message text. Useful for building and testing input regex filters.
    - **log_routed_messages**: (bool, default: true) - Logs the message content and relay target channel id if the message was successfully relayed to ./logs/relayRoutes/
    - **days_delete_after**: (integer, default: 5) - Delete logs after this many days.

### Example
```
{
  "config": {
    "token": "",
    "max_dbus_reconnect": 5,
    "bot_status": true
  },
  "routes": [
    {
      "name": "RelayName",
      "src": "IRC",
      "filter_input_account": ".*",
      "filter_input_sender": ".*",
      "filter_input_conversation": ".*",
      "filter_input_message": ".*",
      "filter_input_flags": ".*",
      "targets": [
        {
          "name": "InternalRouteName",
          "channel_id": 123,
          "title": "Relay",
          "embed": true,
          "embed_color": 4659341,
          "timestamp": true,
          "mention": "@here",
          "strip_mention": true,
          "spam_control_seconds": 0
        }
      ]
    }
  ],
  "logger": {
      "log_purple_messages": true,
      "log_routed_messages": true,
      "days_delete_after": 5
  }
}
```

## Docker
The Docker variant of PurpleRelay uses Finch to provide a GUI-less connection to chat services for relaying to Discord.
### Supported tags and ```Dockerfile``` links
* [```stable```](https://github.com/Nathan-LS/PurpleRelay/blob/master/Dockerfile)
* [```development```](https://github.com/Nathan-LS/PurpleRelay/blob/development/Dockerfile)

### Quick reference
* **Where to get help:**

    [Discord support server](https://discord.gg/Np3FCUn)
* **Where to file issues:**
    
    [https://github.com/Nathan-LS/PurpleRelay/issues](https://github.com/Nathan-LS/PurpleRelay/issues)

### Start an instance
This image uses a single Docker volume to persist the Finch config, logs, and ```routes.json```. See [volumes](https://docs.docker.com/storage/volumes/) for information about Docker volumes.

See this [guide](https://developer.pidgin.im/wiki/Using%20Finch) for using Finch.
1. Create a named Docker volume.
    ```
   docker volume create relayvol
   ```
2. Find the volume's mountpoint
    ```
   docker volume inspect relayvol | grep "Mountpoint"
   ```
3. Place the configured ```routes.json``` file into the root of the volume's mountpoint.
4. Start PurpleRelay with the volume.
    ```
    docker run -it -v relayvol:/app --name myrelay nathanls/purplerelay
    ```
5. Finch is started in the background on the container as a [screen](https://www.gnu.org/software/screen/screen.html) session named ```finch```. 
You will need to exec into the container to initially sign into the chat accounts with Finch from another terminal session. 
If a volume is mounted at ```/app``` on the container the Finch config will persist across restarts.
You can also manually edit files within the Pidgin/Finch config directory which would be located at ```/app/.purple``` on the container and volume.
    ```
    docker exec -it myrelay screen -r finch
    ```
### Where to Store Data
Persist data through mounting named volumes to the ```/app``` directory within the container. 

### Docker Stack and Compose
Example ```stack.yml``` for ```PurpleRelay```:
```text
version: '3.7'
services:
  purple:
    image: nathanls/purplerelay:stable
    deploy:
      restart_policy:
        condition: any
    volumes:
      - relayvol:/app
    networks:
      - purple-network

volumes:
  relayvol:

networks:
  purple-network:
    driver: overlay
```

## Running from source
### Requirements
* An operating system currently utilizing D-Bus (most Linux distributions)
* System packages for [PyGObject](https://pygobject.readthedocs.io/en/latest/getting_started.html)
* Python 3.7+ with packages from ```requirements.txt```

### Installing dependencies and running
This section outlines the process for manually installing dependencies and running the application on [Fedora](https://getfedora.org/) if you choose not to utilize the Docker image of PurpleRelay.

Note: Package names and commands may differ between Linux distros. 
1. Install Python3
    ```
   dnf install -y python38
   ```
2. Install the PyGObject dependencies. See [PyGObject install guide](https://pygobject.readthedocs.io/en/latest/getting_started.html)
    ```
    dnf install -y gcc gobject-introspection-devel cairo-devel pkg-config python3-devel gtk3
    ```
2. Clone and make a virtualenv
    ```
    mkdir ~/relay
    cd ~/relay
    git clone https://github.com/Nathan-LS/PurpleRelay.git
    cd PurpleRelay
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install requirements
    ```
    pip3 install -r requirements.txt
    ```
4. Rename **routes-example.json** to **routes.json** and add in your channel message routing.
See [Relay Configuration](#relay-configuration) for information on configuration definitions.
    ```
    mv routes-example.json routes.json
    nano routes.json
    ```
5. Make a [Discord application/bot](https://discordapp.com/developers/applications/) and copy the token to ```config->token``` in the ```routes.json``` file. 
See the [relay-configuration](#relay-configuration) on this document for config reference.

6. Ensure Pidgin or Finch is running and start the bot.
    ```
    ./venv/bin/python3 ./PurpleRelay
    ```
