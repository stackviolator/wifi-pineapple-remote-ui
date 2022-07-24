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
        self.socks_port = args.socks_port
        self.c2_user = args.c2_user
        self.c2_host = args.c2_host
        self.c2_port = args.c2_port
        self.pineapple_user = args.pineapple_user
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

        x = subprocess.check_output(f"ssh -p {self.c2_port} {self.c2_user}@{self.c2_host} 'ls ~/ssh_tunnels'",
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
        try:
            self.cleanup()
        except Exception:
            print("[-] Could not clean old prox(ies)")

        # SSH payload in a not very complex at all format
        # Thanks PEP8
        ssh_port = self.ports["ssh"]
        # Use ssh to send a remote command setting up a dynamic SOCKS5 proxy
        payload = f"ssh -i {self.key} -p {self.c2_port} {self.c2_user}@{self.c2_host}"
        # Create dynamic proxy on all interfaces
        payload += f" 'ssh -D 0.0.0.0:{self.socks_port} -fNT -p {ssh_port} "
        payload += f"{self.pineapple_user}@localhost'"

        # Check if remote host is set
        if self.c2_host is None:
            print("[-] C2 host is needed")
            sys.exit(1)

        if self.c2_user is None:
            print("[-] C2 user is needed")
            sys.exit(1)

        os.system(payload)

    def run(self):
        try:
            self.to_pineapple()
            print(f"[*] SSH Proxy created on {self.c2_host}:9001")
        except Exception:
            print("[-] Proxy failed to start")

    def kill_ports(self):
        payload = f"ssh -i {self.key} -p {self.c2_port}"
        payload += f" {c2_user}@{self.c2_host}"
        payload += ' "ps aux | grep ssh | grep 9001"'

        ports = subprocess.check_output(payload,
                                        shell=True, text=True).split('\n')

        for port in ports:
            if "grep" in port:
                ports.remove(port)

        for port in ports:
            port = port[9:15]
            if port != '':
                payload = f"ssh -i {self.key} -p {self.c2_port}"
                payload += f" {c2_user}@{self.c2_host}"
                payload += f" 'kill {port}'"
                os.system(payload)

    def cleanup(self):
        print("[*] Closing old SSH prox(ies)...")
        self.kill_ports()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Tool to proxy a remote WiFi Pineapple web interface to a local port',
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''Example:
    python proxy_ui.py -ch 108.52.54.142 -cu pi -i eth0'''))

    parser.add_argument('-i', '--interface', nargs="?", default="lo",
                        help='Specify the interface to use')
    parser.add_argument('-ch', '--c2-host',
                        help='Specify the IP of the C2 server')
    parser.add_argument('-cp', '--c2-port', nargs="?", default="2022",
                        help='Specify the public SSH port of the C2 server')
    parser.add_argument('-cu', '--c2-user', nargs="?",
                        help='Specify the user on the the C2 server')
    parser.add_argument('-pu', '--pineapple-user', nargs="?", default="root",
                        help='Specify the user on the WiFi Pineapple')
    parser.add_argument('-sp', '--socks-port', nargs="?", default="9001",
                        help='Specify the port to open a SOCKS5 proxy on')
    parser.add_argument('-k', '--key', nargs="?", default="~/.ssh/id_rsa",
                        help='Specify the SSH private key file')

    args = parser.parse_args()

    p = Proxy()
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
