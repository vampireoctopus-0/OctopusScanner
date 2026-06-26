# scanner.py

import socket
import threading
import logging
import argparse

class NetworkScanner:
    def __init__(self, target_ip, logger):
        self.target_ip = target_ip
        self.logger = logger
        self.timeout = 2.0
        self.result = []


    @staticmethod
    def make_logger(output_path: str | None):
        logger = logging.getLogger("scanner")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        # For avoid if script re run in rear cases
        logger.handlers = []

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # terminal Handler
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        # Filehandler if -0 is provided

        if output_path:
            fh = logging.FileHandler(output_path, mode="w", encoding="utf-8")
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        return logger
    

    def start_scan(self, port_list):
        threads = []
        self.logger.info("[*]Start scanning on target:%s", self.target_ip)

        for port in port_list:
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()


    def scan_port(self, port: int):
        server = None
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(self.timeout)

            output = server.connect_ex((self.target_ip, port))
            if output == 0:
                self.logger.info("[*] PORT %s IS OPEN:",port)
                self.logger.info("[*] Start grabbing banners.")

                # Adaptive banner grabbing
                try:
                    # pehle chup kr k 1 sec k liye recv pr bethna aur dekhna kia port khud data throw kr rha hai ya nai.
                    server.settimeout(1.0)
                    banner = server.recv(2048)
                    banner_text = banner.decode("utf-8", errors="replace").strip()
                    self.logger.info("[--->][*] PORT %s Banner (Direct): %s", port, banner_text)
                
                except socket.timeout:
                    # step 2 agr 1 sec tk koi data recv pr khud se nai ata us case mein http request ka raw packets generate kr k through karyn gye.
                    self.logger.info("[*]Port %s not given a data. HTTP request is now sending on port.", port)

                    try:
                        server.settimeout(self.timeout)
                        http_request = f"GET / HTTP/1.1\nHost: {self.target_ip}\r\n\r\n"
                        server.sendall(http_request.encode('utf-8'))
                        
                        banner = server.recv(2048)
                        banner_text = banner.decode("uft-8", errors="replace").strip()
                        self.logger.info("[--->[*] Port %s Banner (HTTP probe): %s", port, banner_text)

                    except Exception:
                        self.logger.info("[!] port Open %s: But refused to talk altogether.", port)
                
                except Exception:
                    self.logger.info("[!] PORT %s, Banner grab failed during raw connection", port)

            else:
                self.logger.info("[!] %s: PORT IS CLOSED", port)
        
        except Exception:
            pass
        finally:
            if server:
                try:
                    server.close()
                except Exception:
                    pass




if __name__ == "__main__":
    print("="*30)
    parser = argparse.ArgumentParser(description = "OCTOPUS SCANNER v1.4")
    print("="*30)

    parser.add_argument("-t","--target",required=True,help="Must be give target server.")
    parser.add_argument("-p","--ports",required=True,help="Ports must be seperated with commas.")
    parser.add_argument(
        "-o","--output",
        nargs="?",
        const="scan_output.log",
        default=None,
        help="Optional: save output to file. Usage: -o OR -o filename.txt"
        )

    args = parser.parse_args()

    try:
        port_list = [int(p.strip()) for p in args.ports.split(",") if p.strip()]
        if not port_list:
            raise ValueError
    except Exception:
        print("[!] PORTS MuST BE SEPERATED WITH COMMAS.")
        raise SystemExit(1)
    
    logger = NetworkScanner.make_logger(args.output)
    scanner = NetworkScanner(args.target, logger)
    scanner.start_scan(port_list)
