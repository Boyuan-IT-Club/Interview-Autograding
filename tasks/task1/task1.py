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
    'Environment Check': 50,
    'Git Check': 25,
    'Python3 Check': 25,
}

results = []
score = 0
current_os = platform.system()

# --- SECRET KEY ---
# 从 etc/config 文件中加载密钥
try:
    app_path = os.path.realpath(sys.executable)
    app_dir = os.path.dirname(app_path)
    project_root = os.path.dirname(os.path.dirname(app_dir))
    config_path = os.path.join(project_root, 'etc', 'config')
    
    with open(config_path, 'r') as f:
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
    
    if isinstance(result, tuple):
        passed, points_earned = result
        if passed:
            score += points_earned
            results.append({"name": name, "passed": True, "points": points_earned})
            print(f"✓ {name}: Passed (+{points_earned}pts)")
        else:
            results.append({"name": name, "passed": False, "points": 0})
            print(f"✗ {name}: Failed (+0pts)")
        return passed
    else:
        if result:
            score += points
            results.append({"name": name, "passed": True, "points": points})
            print(f"✓ {name}: Passed")
        else:
            results.append({"name": name, "passed": False, "points": 0})
            print(f"✗ {name}: Failed")
        return result

def check_environment():
    """Checks the OS and WSL version."""
    print(f"  - Detected OS: {current_os}")
    
    # Check for Linux environments
    if current_os == 'Linux':
        try:
            # Check for WSL environment first by reading /proc/version
            with open('/proc/version', 'r') as f:
                version_info = f.read().strip()
            
            if "Microsoft" in version_info or "microsoft-standard" in version_info:
                if "WSL2" in version_info:
                    print("  - Detected: WSL2 environment.")
                    return True, TESTS['Environment Check']
                else:
                    points_earned = TESTS['Environment Check'] / 2
                    print(f"  - Detected: WSL1 environment. Partial points awarded (+{points_earned}pts).")
                    return True, points_earned
            else:
                print("  - Detected: Native Linux environment.")
                return True, TESTS['Environment Check']
        except Exception:
            # If reading /proc/version fails, assume it's native Linux as a fallback
            print("  - Detected: Native Linux environment (Error reading /proc/version).")
            return True, TESTS['Environment Check']
    # Check for macOS
    elif current_os == 'Darwin':
        print("  - Detected OS: macOS.")
        return True, TESTS['Environment Check']
    # Check for Windows
    elif current_os == 'Windows':
        print("  - Detected OS: Windows. Please run the script inside a Linux/WSL2 or macOS terminal.")
        return False, 0
    # Check for other OS
    else:
        print("  - Detected OS: Unknown. Please run the script inside a Linux/WSL2 or macOS terminal.")
        return False, 0

        

def check_git():
    """Verifies the 'git' command is installed."""
    try:
        git_version_output = subprocess.check_output(['git', '--version'], text=True)
        print(f"  - Passed: Git is installed. {git_version_output.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  - Failed: 'git' command not found. Please install Git.")
        return False
    except Exception as e:
        print(f"  - An error occurred: {e}")
        return False

def check_python3_exists():
    """Verifies the 'python3' command is installed."""
    try:
        python3_path = subprocess.check_output(['which', 'python3'], text=True).strip()
        print(f"  - Passed: 'python3' command found at {python3_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  - Failed: 'python3' command not found. Please install Python 3.")
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
    
    run_check('Environment Check', check_environment, TESTS['Environment Check'])
    run_check('Git Check', check_git, TESTS['Git Check'])
    run_check('Python3 Check', check_python3_exists, TESTS['Python3 Check'])
    
    generate_and_save_report()
