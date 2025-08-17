import platform
import subprocess
import sys
import os
import hashlib
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
import base64

# --- Test Definitions ---
TESTS = {
    'Linux Check': 20,
    'WSL2 Check': 30,
    'Python3 Check': 25,
    'Python Alias Check': 25,
}

results = []
score = 0

# --- SECRET KEY ---
# 从 etc/config 文件中加载密钥
try:
    # 使用 os.path.realpath(sys.executable) 获取可执行文件的真实路径
    # 这在 PyInstaller 打包的单文件可执行文件中非常重要
    app_path = os.path.realpath(sys.executable)
    # 获取可执行文件所在的目录
    app_dir = os.path.dirname(app_path)
    # 获取项目根目录，这里假设etc文件夹在可执行文件的上两级目录
    project_root = os.path.dirname(os.path.dirname(app_dir))
    config_path = os.path.join(project_root, 'etc', 'config')
    
    with open(config_path, 'r') as f:
        # 读取文件内容，去除首尾空白，然后进行 Base64 解码
        SECRET_KEY = base64.b64decode(f.read().strip())
    if len(SECRET_KEY) not in [16, 24, 32]:
        raise ValueError("Incorrect AES key length from config file.")
except FileNotFoundError:
    print("Error: 'etc/config' file not found. Please ensure it exists.")
    sys.exit(1)
except Exception as e:
    print(f"Error loading secret key: {e}")
    sys.exit(1)


# --- Helper function for printing reports ---
def print_final_report():
    print("\n--- AUTOGRADING FINAL REPORT ---")
    print("Results for environment check:")
    for result in results:
        status = '✓ Passed' if result['passed'] else '✗ Failed'
        print(f"  - {result['name']}: {status} (+{result['points']}pts)")
    print(f"\nFinal Score: {score}/{sum(TESTS.values())} (Correctness)")
    print("----------------------------------\n")

def run_check(name, check_func, points):
    global score
    print(f"Checking for {name}...")
    result = check_func()
    
    if result:
        score += points
        results.append({"name": name, "passed": True, "points": points})
        print(f"✓ {name}: Passed")
    else:
        results.append({"name": name, "passed": False, "points": 0})
        print(f"✗ {name}: Failed")
    
    return result

def check_is_linux():
    system_name = platform.system()
    print(f"  - Detected OS: {system_name}")
    return system_name == 'Linux'

def check_wsl2():
    try:
        with open('/proc/version', 'r') as f:
            version_info = f.read().strip()
        
        if "microsoft-standard-WSL2" in version_info:
            print("  - Passed: Detected 'microsoft-standard-WSL2' in /proc/version.")
            return True
        else:
            print("  - Failed: '/proc/version' does not contain expected keywords.")
            return False
    except Exception as e:
        print(f"  - An error occurred: {e}")
        return False

def check_python3_exists():
    print("  - Verifying 'python3' command exists...")
    try:
        subprocess.check_output(['which', 'python3'], text=True).strip()
        print("  - Passed: 'python3' command found.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  - Failed: 'python3' command not found.")
        return False

def check_python_alias():
    print("  - Verifying 'python' command is correctly aliased...")
    try:
        python_path = subprocess.check_output(['which', 'python'], text=True).strip()
        print(f"  - Passed: 'python' command found at {python_path}")
        
        is_symlink_to_py3 = os.path.islink(python_path) and 'python3' in os.readlink(python_path)
        is_direct_py3 = 'python3' in python_path and not os.path.islink(python_path)

        if is_direct_py3 or is_symlink_to_py3:
            print("  - Passed: 'python' is correctly aliased to 'python3'.")
            return True
        else:
            print("  - Failed: 'python' does not point to 'python3'.")
            return False

    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  - Failed: 'python' command not found.")
        return False
    except Exception as e:
        print(f"  - An error occurred during check: {e}")
        return False

def encrypt_report(report_data):
    try:
        cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(json.dumps(report_data).encode('utf-8'))
        
        encrypted_data = {
            "nonce": b64encode(nonce).decode('utf-8'),
            "ciphertext": b64encode(ciphertext).decode('utf-8'),
            "tag": b64encode(tag).decode('utf-8')
        }
        return json.dumps(encrypted_data)
    except Exception as e:
        return f"Encryption failed: {e}"

def generate_and_save_report():
    """Generates an encrypted report and saves it to the same directory as the executable."""
    # 获取可执行文件所在的目录
    app_dir = os.path.dirname(os.path.realpath(sys.executable))
    # 拼接完整的报告文件路径
    report_file_path = os.path.join(app_dir, "autograding_report.json")
    
    final_results = {
        "score": score,
        "max_score": sum(TESTS.values()),
        "test_results": results
    }
    
    encrypted_report = encrypt_report(final_results)

    with open(report_file_path, "w") as f:
        f.write(encrypted_report)
    
    print("\n--- SUBMISSION CREATED ---")
    print(f"An encrypted submission file has been saved to {report_file_path}.")
    print("Please submit this file.")

if __name__ == "__main__":
    print("--- Running Autograder ---")
    
    is_linux = run_check('Linux Check', check_is_linux, TESTS['Linux Check'])
    if is_linux:
        run_check('WSL2 Check', check_wsl2, TESTS['WSL2 Check'])
        python3_exists = run_check('Python3 Check', check_python3_exists, TESTS['Python3 Check'])
        if python3_exists:
            run_check('Python Alias Check', check_python_alias, TESTS['Python Alias Check'])
        else:
            results.append({"name": "Python Alias Check", "passed": False, "points": 0})
            print("✗ Skipping Python Alias Check as python3 not found.")
    else:
        results.append({"name": "WSL2 Check", "passed": False, "points": 0})
        results.append({"name": "Python3 Check", "passed": False, "points": 0})
        results.append({"name": "Python Alias Check", "passed": False, "points": 0})
        print("\n--- Environment Mismatch ---")
        print("This autograding script is intended for Linux/WSL2 environments.")
        print("Please ensure you are running this from a WSL2 terminal.")
        print("----------------------------\n")

    print_final_report()
    generate_and_save_report()