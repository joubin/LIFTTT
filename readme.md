# LIFTTT
LIFTTT is a local (and simple implementation of If this then that)

## Why

Homekit is not as feature rich as what can be done with If this then that (IFTTT). But its has the benefit of being completely local to my network.
None of my IoT devices can talk to the internet. As a result, I cannot use IFTTT. 

Local If This Then That (LIFTTT) allows me to program modules to act on my IoT devices. 

## Install

Requires Python 3.6+. 

 

### Create a venv
I recommend running this in a [virtual environment](https://docs.python.org/3/library/venv.html) (venv).

```bash
virtualenv -p `which python3.6` venv
```

### Activate the enviroment
```bash
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration
Provide a basic configuration

```buildoutcfg
[DEFAULT]
auth_code = 335-28-246
log_file = /var/log/homebridge.log
port = 33425
server = pi

[Wemo Mini]
type = auto_off
auto_off = 30s
on_off_regex = \[(.*)\] \[(.*)\] (.*)\ - Set state: (Off|On)


```

Replace WeMo Mini with the name of the Switch, Appliance or any other item. Currently the auto_off module is the only implementations. Feel free to contribute and add other modules.

## Run it
With the appropriate enviorment active, run the shell
```bash
python Main.py
``` 

## Create a service

### Create a command for this service

```bash
cd /usr/local/bin
touch lifttt
```

#### Script
```bash
#!/bin/bash
DIR=/var/homebridge/LIFTTT/
sleep 60
python3.6 "$DIR"Main.py
```

#### init.d
```bash
### BEGIN INIT INFO
# Provides: Homebridge
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

dir="/var/homebridge/LIFTTT" # where the repo was pulled to
cmd="DEBUG=* /usr/local/bin/lifttt" # change the directory where the script was made
user="homebridge" # if running as a different user

# Do not change below this line
name=`basename $0`
pid_file="/var/run/$name.pid"
stdout_log="/var/log/$name.log"
stderr_log="/var/log/$name.err"

get_pid() {
    cat "$pid_file"
}

is_running() {
    echo `get_pid`
    [ -f "$pid_file" ] && ps -p `get_pid` > /dev/null 2>&1
}

case "$1" in
    start)
    if is_running; then
        echo "Already started"
    else
        echo "Starting $name"
        cd "$dir"
        if [ -z "$user" ]; then
            sudo $cmd >> "$stdout_log" 2>> "$stderr_log" &
        else
            sudo -u "$user" $cmd >> "$stdout_log" 2>> "$stderr_log" &
        fi
        echo $! > "$pid_file"
        if ! is_running; then
            echo "Unable to start, see $stdout_log and $stderr_log"
            exit 1
        fi
    fi
    ;;
    stop)
    if is_running; then
        echo -n "Stopping $name.."
        kill -9 `get_pid`
        for i in 1 2 3 4 5 6 7 8 9 10
        # for i in `seq 10`
        do
            if ! is_running; then
                break
            fi

            echo -n "."
            sleep 1
        done
        echo

        if is_running; then
            echo "Not stopped; may still be shutting down or shutdown may have failed"
            exit 1
        else
            echo "Stopped"
            if [ -f "$pid_file" ]; then
                rm "$pid_file"
            fi
        fi
    else
        echo "Not running"
    fi
    ;;
    restart)
    $0 stop
    if is_running; then
        echo "Unable to stop, will not attempt to start"
        exit 1
    fi
    $0 start
    ;;
    status)
    if is_running; then
        echo "Running"
    else
        echo "Stopped"
        exit 1
    fi
    ;;
    *)
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac

exit 0

```

### Add to startup items

```bash
update-rc.d lifttt defaults 99
```


