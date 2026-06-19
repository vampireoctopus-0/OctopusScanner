# vampirescan.py

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
                  print(f"  [--->] Open but No banner returned.")

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
    print("="*30)
    print("     VampireScanner v1.0")
    print("="*30)

    target_ip = input("Enter target IP: ")

    # common ports list [FTP, SSH, HTTP, HTTPS, Netcat]
    common_ports = [21, 22, 83, 443, 4444, 403, 23, 24, 55, 4567, 3245, 5421, 345, 101, 2323]


    scanner = NetworkScanner(target_ip)

    scanner.start_scan(common_ports)
    