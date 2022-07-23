import os
import time
import argparse
import textwrap
import re
import sys
import subprocess


class Proxy:
    def __init__(self):
        self.local_host = self.get_ip_from_interface(args.interface)
        self.local_port = args.local_port
        self.local_user = "gorilla"
        self.remote_host = args.remote_host
        self.remote_port = args.remote_port
        self.remote_user = args.remote_user
        self.ports = self.get_ports()
        self.key = args.key

    def get_ip_from_interface(self, interface):
        try:
            # Shamelessly stolen code
            ipv4 = re.search(re.compile(r'(?<=inet )(.*)(?=\/)', re.M),
                             os.popen(f'ip addr show {interface}').read()).groups()[0]
        except Exception:
            print("[-] Invalid interface")
            sys.exit(1)

        return ipv4

    def get_ports(self):
        ports = {
            "ssh": None,
            "web": None
        }

        x = subprocess.check_output("ssh pi 'ls ~/ssh_tunnels'",
                                    shell=True, text=True)
        x = x.split()

        for port in x:
            if "ssh" in port:
                ports["ssh"] = port[:-4]
            elif "web" in port:
                ports["web"] = port[:-4]
            else:
                print("No web or ssh port found")
                sys.exit(1)
        return ports

    def to_pineapple(self):

        # SSH payload in a not very complex at all format
        # Thanks PEP8
        ssh_port = self.ports["ssh"]
        # Use ssh to send a remote command setting up a dynamic SOCKS5 proxy
        payload = f"ssh -i {self.key} -p {self.remote_port} pi@{self.remote_host}"
        # Create dynamic proxy on all interfaces
        payload += f" 'ssh -D 0.0.0.0:9001 -fNT -p {ssh_port} "
        payload += f"{self.remote_user}@localhost'"

        # Check if remote host is set
        if self.remote_host is None:
            print("[-] Remote host is needed")
            sys.exit(1)

        os.system(payload)

        print(f"[*] SSH Proxy created on {self.remote_host}:9001")

    def to_pi(self):
        pass

    def run(self):
        self.to_pineapple()

    def kill_ports(self):
        payload = f"ssh -i {self.key} -p {self.remote_port}"
        payload += f" pi@{self.remote_host}"
        payload += ' "ps aux | grep ssh | grep 9001"'

        ports = subprocess.check_output(payload,
                                        shell=True, text=True).split('\n')

        for port in ports:
            if "grep" in port:
                ports.remove(port)

        for port in ports:
            port = port[9:15]
            if port != '':
                payload = f"ssh -i {self.key} -p {self.remote_port}"
                payload += f" pi@{self.remote_host}"
                payload += f" 'kill {port}'"
                os.system(payload)

    def cleanup(self):
        print("[*] Closing old SSH prox(ies)...")
        self.kill_ports()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Tool to proxy a remote WiFi Pineapple web interface to a local port',
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''Example:
    python proxy_ui.py -rh 108.52.54.142 -i eth0'''))

    parser.add_argument('-i', '--interface', nargs="?", default="lo",
                        help='Specify the interface to use')
    parser.add_argument('-rh', '--remote-host',
                        help='Specify the interface to use')
    parser.add_argument('-rp', '--remote-port', nargs="?", default="2022",
                        help='Specify the port of the Pineapple interface')
    parser.add_argument('-ru', '--remote-user', nargs="?", default="root",
                        help='Specify the user on the Pineapple')
    parser.add_argument('-lp', '--local-port', nargs="?", default="9001",
                        help='Specify the port to proxy traffic to')
    parser.add_argument('-k', '--key', nargs="?", default="~/.ssh/id_rsa",
                        help='Specify the SSH private key file')

    args = parser.parse_args()

    p = Proxy()

    # Clean old proxies and create a new one
    p.cleanup()
    print("")
    print("[*] Starting proxy")
    p.run()

    # Wait for a KeyboardInterrupt to quit
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("")
            print("[*] User quit")
            p.cleanup()
            sys.exit(0)
