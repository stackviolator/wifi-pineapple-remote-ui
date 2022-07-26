<h1 align="center">
  <br>
  <a href="https://github.com/stackviolator/wifi-pineapple-remote-ui"><img src="img/cli.png" alt="cli"></a>
  <br>
  <br>
  <a href="https://github.com/stackviolator/wifi-pineapple-remote-ui"><img src="img/web.png" alt="web"></a>
  <br>
</h1>

# WiFi Pineapple Web Proxy
Scripts to set up proxies to access the web UI of the pineapple remotely
# Setup
# Installation
- Review installation and setup video [here](https://google.com)

## Requirements
- Python 3.10+
- `pip install -r requirements.txt`

## On the WiFi Pineapple
- These scripts will create reverse SSH proxies to allow communication from the C2 server to the pineapple
- Install the scripts located in "/for_server" to run as cron on reboot\
`crontab -e`\
`@reboot /usr/bin/python /path/to/file1`\
`@reboot /usr/bin/python /path/to/file2`

## On the server
- A server needs to be publically accessible and reachable by the pineapple
- Add the SSH public key of your attacker box and the wifi pineapple to `~/.ssh/authorized_keys`
- Add `connect_pineapple` to `/usr/bin/`

# Usage
## From the attacker
- Run the script to set up the chains
`python proxy_ui.py -ch <public server_ip> -cu <username>`
- From a browser, use a socks5 proxy to proxy traffic through `<Your Server IP>:<port>`
- Navigate to `localhost:1471`

## Youtube Video
[Hak5 WiFi Pineapple Web UI Proxy](https://www.youtube.com/watch?v=vYFBOG4tfBQ)
