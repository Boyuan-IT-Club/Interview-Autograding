import subprocess
import sys
import os
import json
import base64
from base64 import b64encode
from Crypto.Cipher import AES

# --- Test Definitions ---
TESTS = {
    'Docker Installed Check': 25,
    'Docker Service Running Check': 25,
    'User Permissions Check': 25,
    'Container Execution Check': 25,
}

results = []
score = 0

# --- SECRET KEY ---
# 从 etc/config 文件中加载密钥
try:
    app_dir = os.path.dirname(os.path.realpath(sys.executable))
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
    """Prints a formatted summary of the test results and the final score."""
    print("\n--- AUTOGRADING FINAL REPORT ---")
    print("Results for Docker environment check:")
    for result in results:
        status = '✓ Passed' if result['passed'] else '✗ Failed'
        print(f"  - {result['name']}: {status} (+{result['points']}pts)")
    print(f"\nFinal Score: {score}/{sum(TESTS.values())} (Correctness)")
    print("----------------------------------\n")

def run_check(name, check_func, points):
    global score
    print(f"Checking {name}...")
    result = check_func()

    if result:
        score += points
        results.append({"name": name, "passed": True, "points": points})
        print(f"✓ {name}: Passed")
    else:
        results.append({"name": name, "passed": False, "points": 0})
        print(f"✗ {name}: Failed")

    return result


def check_docker_installed():
    print("  - Verifying 'docker' command exists...")
    try:
        # 'which' command finds the full path to an executable.
        subprocess.check_output(['which', 'docker'], text=True, stderr=subprocess.DEVNULL).strip()
        print("  - Passed: 'docker' command found.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  - Failed: 'docker' command not found. Is Docker installed?")
        return False

def check_docker_service_running():
    print("  - Verifying the Docker service is running...")
    try:
        subprocess.run(['docker', 'info'], check=True, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("  - Passed: Docker service is active and responding.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  - Failed: Could not connect to the Docker service.")
        print("  - Tip: Make sure the Docker daemon is started.")
        return False

def check_user_permissions():
    print("  - Verifying user permissions (no sudo required)...")
    try:
        user_groups = subprocess.check_output(['groups'], text=True).strip()
        if 'docker' in user_groups.split():
            print("  - Passed: User is correctly configured in the 'docker' group.")
            return True
        else:
            print("  - Failed: User is not in the 'docker' group.")
            print("  - Tip: Run 'sudo usermod -aG docker $USER' and then RE-OPEN your terminal.")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  - Failed: Could not determine user groups.")
        return False

def check_container_execution():
    print("  - Verifying container execution with 'hello-world'...")
    try:
        output = subprocess.check_output(['docker', 'run', 'hello-world'], text=True, stderr=subprocess.STDOUT)
        if "Hello from Docker!" in output:
            print("  - Passed: Successfully pulled and ran the 'hello-world' container.")
            return True
        else:
            print("  - Failed: 'hello-world' container ran, but output was unexpected.")
            return False
    except subprocess.CalledProcessError as e:
        print("  - Failed: Could not run the 'hello-world' container.")
        print(f"  - Error details: {e.output}")
        return False
    except FileNotFoundError:
        # 理论上不可能执行到这里，仅作为保险
        print("  - Failed: 'docker' command not found.")
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
    app_dir = os.path.dirname(os.path.realpath(sys.executable))
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

    docker_installed = run_check('Docker Installed Check', check_docker_installed, TESTS['Docker Installed Check'])

    if docker_installed:
        service_running = run_check('Docker Service Running Check', check_docker_service_running, TESTS['Docker Service Running Check'])
        if service_running:
            permissions_ok = run_check('User Permissions Check', check_user_permissions, TESTS['User Permissions Check'])
            if permissions_ok:
                run_check('Container Execution Check', check_container_execution, TESTS['Container Execution Check'])
            else:
                results.append({"name": "Container Execution Check", "passed": False, "points": 0})
                print("✗ Skipping Container Execution Check due to user permission issues.")
        else:
            results.append({"name": "User Permissions Check", "passed": False, "points": 0})
            results.append({"name": "Container Execution Check", "passed": False, "points": 0})
            print("✗ Skipping subsequent checks as Docker service is not running.")
    else:
        results.append({"name": "Docker Service Running Check", "passed": False, "points": 0})
        results.append({"name": "User Permissions Check", "passed": False, "points": 0})
        results.append({"name": "Container Execution Check", "passed": False, "points": 0})
        print("\n--- Fundamental Check Failed ---")
        print("Docker command not found. Please install Docker before proceeding.")
        print("----------------------------------\n")

    print_final_report()
    generate_and_save_report()
