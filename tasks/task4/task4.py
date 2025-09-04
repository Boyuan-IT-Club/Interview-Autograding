import os
import sys
import json
import base64
import subprocess
import zipfile
from pathlib import Path
from Crypto.Cipher import AES

TESTS = {
    'make_all_creates_zip': 30,
    'zip_contains_all_files': 40,
    'make_clean_works': 30,
}
results = []
final_score = 0
TASK_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = TASK_DIR / "output_images"
ZIP_FILE = TASK_DIR / "processed_images.zip"
INPUT_DIR = TASK_DIR / "input_images"

# --- SECRET KEY ---
try:
    project_root = TASK_DIR.parent.parent
    config_path = project_root / 'etc' / 'config'
    with open(config_path, 'r') as f:
        SECRET_KEY = base64.b64decode(f.read().strip())
    if len(SECRET_KEY) not in [16, 24, 32]:
        raise ValueError("Incorrect AES key length from config file.")
except Exception as e:
    print(f"Error loading secret key: {e}")
    sys.exit(1)

def run_command(command, cwd=TASK_DIR):
    """Runs a command and returns its return code and output."""
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
    """Records a test result and updates the score."""
    global final_score
    status = "✓ Passed" if passed else "✗ Failed"
    print(f"  - {name}: {status}")
    if passed:
        final_score += points
    results.append({"name": name, "passed": passed, "points": points if passed else 0})

def print_final_report():
    """Prints the final grading report."""
    print("\n--- AUTOGRADING FINAL REPORT ---")
    print("Results for Makefile Automation Challenge:")
    for result in results:
        status = '✓ Passed' if result['passed'] else '✗ Failed'
        points_str = f"+{result['points']}pts"
        print(f"  - {result['name']}: {status} ({points_str})")
    print(f"\nFinal Score: {final_score}/{sum(TESTS.values())} (Correctness)")
    print("----------------------------------\n")

def encrypt_report(report_data):
    """Encrypts data using AES-EAX mode."""
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
    """Generates, encrypts, and saves the final report."""
    report_file_path = TASK_DIR / "autograding_report.json"
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
    if not (TASK_DIR / "Makefile").exists():
        print("✗ Error: `Makefile` not found in the `task4` directory.")
        print("  Please rename `starter_makefile` to `Makefile` and complete it.")
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

    zip_created = ZIP_FILE.exists()
    check_test('make_all_creates_zip', zip_created, TESTS['make_all_creates_zip'])

    if zip_created:
        try:
            expected_files = {p.stem + ".png" for p in INPUT_DIR.glob("*.jpg")}
            with zipfile.ZipFile(ZIP_FILE, 'r') as zf:
                found_files = {Path(f).name for f in zf.namelist()}
            found_basenames = {Path(f).name for f in found_files}

            files_match = (expected_files == found_basenames)
            check_test('zip_contains_all_files', files_match, TESTS['zip_contains_all_files'])
            if not files_match:
                print(f"    - Expected in zip: {sorted(list(expected_files))}")
                print(f"    - Found in zip:    {sorted(list(found_basenames))}")

        except Exception as e:
            check_test('zip_contains_all_files', False, TESTS['zip_contains_all_files'])
            print(f"    - Error reading zip file: {e}")
    else:
        check_test('zip_contains_all_files', False, TESTS['zip_contains_all_files'])

    print("\n--> Running `make clean` to test cleanup...")
    run_command("make clean")

    clean_ok = not OUTPUT_DIR.exists() and not ZIP_FILE.exists()
    check_test('make_clean_works', clean_ok, TESTS['make_clean_works'])
    if not clean_ok:
        if OUTPUT_DIR.exists():
            print("    - `output_images` directory was not removed.")
        if ZIP_FILE.exists():
            print(f"    - `{ZIP_FILE.name}` was not removed.")

    print_final_report()
    save_report()
