# vampirescan.py

import argparse
import threading
import socket

class NetworkScanner:
    def __init__(self, target_ip):

        # is k andr target ka ipsave hoga.
        self.target_ip = target_ip
        # Timeout fix kiya hai taky script hang naa ho.
        self.timeout = 2.0


    def scan_port(self, port):
        try:
            # Socket creation
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(self.timeout)
             
            # Connection Build and checking
            result = server.connect_ex((self.target_ip, port))

            if result == 0:
                print(f"[+] PORT {port} is OPEN!")

                # Banner grabber
                try:
                  banner = server.recv(1024)

                  # Bytes ko readable form mein convert krna. (.decode)
                  print(f"  [--->] Banner: {banner.decode('utf-8').strip()}")

                except:
                  print(f"'{port}'[--->] Open but No banner returned.")

            else:
                print("PORT is closed...")

            server.close()


        except:
             pass

    
    def start_scan(self, ports_list):

        print(f"/[*] Start scaning on {self.target_ip}")
        threads = []

        for port in ports_list:
            print(f"Scaning on {port}")
            t = threading.Thread(target = self.scan_port, args = (port,))

            threads.append(t)
            t.start()

        for t in threads:
            t.join()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Octopus Scanner v 1.2 Upgraded.")

    parser.add_argument("-t", "--target", required = True, help = "Target ip is required.")
    parser.add_argument("-p", "--ports", required = True, help = "port is required separated with commas.")
    
    args = parser.parse_args()

    try:
        ports_list = [int(p) for p in args.ports.split(",")]

    except:
        print("[!] ports must be separated with commas.")
        exit()

    scanner = NetworkScanner(args.target)
    scanner.start_scan(ports_list)
