# PurpleRelay v0.1.0
PurpleRelay is a Linux application to relay and route messages from Pidgin/Finch to Discord.

# Requirements
* Python 3.6+
* Linux

# Installing
1. Install the dependencies. If using Ubuntu/Debian, otherwise see [PyGObject install guide.](https://pygobject.readthedocs.io/en/latest/devguide/dev_environ.html#devenv)
    ```
    sudo apt-get install -y python3-venv python3-wheel python3-dev
    sudo apt-get install -y libgirepository1.0-dev build-essential \
      libbz2-dev libreadline-dev libssl-dev zlib1g-dev libsqlite3-dev wget \
      curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libcairo2-dev
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
4. Make a [Discord application/bot](https://discordapp.com/developers/applications/) and set token in **default-config.ini**. Make sure to rename the file to **config.ini**.
    ```
    nano default-config.ini
    mv default-config.ini config.ini
    ```
5. Rename **routes-example.json** to **routes.json** and add in your channel message routing.
    ```
    nano routes-example.json
    mv routes-example.json routes.json
    ```
6. Ensure Pidgin or Finch is running and start the bot.
    ```
    ```