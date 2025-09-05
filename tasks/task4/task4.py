import os
import sys
import json
import base64
import subprocess
import zipfile
from Crypto.Cipher import AES

TESTS = {
    'make_all_creates_zip': 30,
    'zip_contains_all_files': 40,
    'make_clean_works': 30,
}
results = []
final_score = 0

if getattr(sys, 'frozen', False):
    TASK_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    # for: `python task4.py'
    TASK_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(TASK_DIR, "output_images")
ZIP_FILE = os.path.join(TASK_DIR, "processed_images.zip")
INPUT_DIR = os.path.join(TASK_DIR, "input_images")

config_path = ""
try:
    project_root = os.path.dirname(os.path.dirname(TASK_DIR))
    config_path = os.path.join(project_root, 'etc', 'config')

    with open(config_path, 'r') as f:
        SECRET_KEY = base64.b64decode(f.read().strip())

    if len(SECRET_KEY) not in [16, 24, 32]:
        raise ValueError("Incorrect AES key length from config file.")

except Exception as e:
    print(f"Error loading secret key from '{config_path}': {e}")
    sys.exit(1)

def run_command(command, cwd=TASK_DIR):
    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True,
            check=False
        )
        return process.returncode == 0, process.stdout, process.stderr
    except Exception as e:
        return False, "", str(e)

def check_test(name, passed, points):
    global final_score
    status = "✓ Passed" if passed else "✗ Failed"
    print(f"  - {name}: {status}")
    if passed:
        final_score += points

    results.append({
        "name": name,
        "passed": passed,
        "points": points
    })

def print_final_report():
    print("\n--- AUTOGRADING FINAL REPORT ---")
    print("Results for Makefile Automation Challenge:")
    for result in results:
        status = '✓ Passed' if result['passed'] else '✗ Failed'
        earned_points = result['points'] if result['passed'] else 0
        points_str = f"+{earned_points}pts"
        print(f"  - {result['name']}: {status} ({points_str})")
    print(f"\nFinal Score: {final_score}/{sum(TESTS.values())} (Correctness)")
    print("----------------------------------\n")

def encrypt_report(report_data):
    try:
        cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(json.dumps(report_data).encode('utf-8'))

        encrypted_data = {
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "tag": base64.b64encode(tag).decode('utf-8')
        }
        return json.dumps(encrypted_data)
    except Exception as e:
        return json.dumps({"error": f"Encryption failed: {e}"})


def save_report():
    report_file_path = os.path.join(TASK_DIR, "autograding_report.json")
    final_results_data = {
        "score": final_score,
        "max_score": sum(TESTS.values()),
        "test_results": results
    }

    encrypted_report = encrypt_report(final_results_data)

    with open(report_file_path, "w") as f:
        f.write(encrypted_report)

    print("\n--- SUBMISSION CREATED ---")
    print(f"An encrypted submission file has been saved to {report_file_path}.")
    print("Please submit this file.")

if __name__ == "__main__":
    makefile_path = os.path.join(TASK_DIR, "Makefile")
    starter_makefile_path = os.path.join(TASK_DIR, "starter_makefile")
    if not os.path.exists(makefile_path) and os.path.exists(starter_makefile_path):
        print("✗ Error: `Makefile` not found in the `task4` directory.")
        print("  Please rename `starter_makefile` to `Makefile` and complete it.")
        sys.exit(1)
    elif not os.path.exists(makefile_path):
        print("✗ Error: `Makefile` or `starter_makefile` not found.")
        sys.exit(1)


    print("--- Running Makefile Checks ---")

    print("\n--> Running `make clean` to ensure a fresh start...")
    run_command("make clean")

    print("\n--> Running `make` to execute the pipeline...")
    success, stdout, stderr = run_command("make")
    if not success:
        print("✗ `make` command failed.")
        print("--- STDOUT ---")
        print(stdout)
        print("--- STDERR ---")
        print(stderr)

    zip_created = os.path.exists(ZIP_FILE)
    check_test('make_all_creates_zip', zip_created, TESTS['make_all_creates_zip'])

    if zip_created:
        try:
            expected_files = {
                os.path.splitext(f)[0] + ".png"
                for f in os.listdir(INPUT_DIR) if f.lower().endswith(".jpg")
            }
            with zipfile.ZipFile(ZIP_FILE, 'r') as zf:
                found_files = {os.path.basename(f) for f in zf.namelist() if not f.endswith('/')}

            files_match = (expected_files == found_files)
            check_test('zip_contains_all_files', files_match, TESTS['zip_contains_all_files'])
            if not files_match:
                print(f"    - Expected in zip: {sorted(list(expected_files))}")
                print(f"    - Found in zip:    {sorted(list(found_files))}")

        except Exception as e:
            check_test('zip_contains_all_files', False, TESTS['zip_contains_all_files'])
            print(f"    - Error reading zip file: {e}")
    else:
        check_test('zip_contains_all_files', False, TESTS['zip_contains_all_files'])

    print("\n--> Running `make clean` to test cleanup...")
    run_command("make clean")

    clean_ok = not os.path.exists(OUTPUT_DIR) and not os.path.exists(ZIP_FILE)
    check_test('make_clean_works', clean_ok, TESTS['make_clean_works'])
    if not clean_ok:
        if os.path.exists(OUTPUT_DIR):
            print("    - `output_images` directory was not removed.")
        if os.path.exists(ZIP_FILE):
            print(f"    - `{os.path.basename(ZIP_FILE)}` was not removed.")

    print_final_report()
    save_report()
