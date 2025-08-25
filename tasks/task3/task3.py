import os
import sys
import json
import base64
import subprocess
from base64 import b64encode
from Crypto.Cipher import AES

try:
    import quiz_data
except ImportError:
    print("Error: quiz_data.py not found.")
    print("Please run the build_quiz.py script first to generate it.")
    sys.exit(1)

TESTS = {
    'Directory Creation': 10,
    'File Creation': 10,
    'File Content': 15,
    'Directory Copy': 15,
}

TOTAL_OPERATIONS_SCORE = sum(TESTS.values())
TOTAL_QUIZ_SCORE = 50
TOTAL_MAX_SCORE = TOTAL_OPERATIONS_SCORE + TOTAL_QUIZ_SCORE
results = []
final_score = 0
CONTAINER_NAME = "autograding-task3"

try:
    app_dir = os.path.dirname(os.path.realpath(sys.executable))
    project_root = os.path.dirname(os.path.dirname(app_dir))
    config_path = os.path.join(project_root, 'etc', 'config')
    with open(config_path, 'r') as f:
        SECRET_KEY = base64.b64decode(f.read().strip())
    if len(SECRET_KEY) not in [16, 24, 32]:
        raise ValueError("Incorrect AES key length from config file.")
except Exception as e:
    print(f"Error loading secret key: {e}")
    sys.exit(1)

def print_final_report():
    print("\n--- AUTOGRADING FINAL REPORT ---")
    print("Results for Linux Challenge:")
    for result in results:
        status = '✓ Passed' if result.get('passed', False) else '✗ Failed'
        points_str = f"+{result.get('points', 0)}pts"
        print(f"  - {result['name']}: {status} ({points_str})")
    print(f"\nFinal Score: {final_score}/{TOTAL_MAX_SCORE} (Correctness)")
    print("----------------------------------\n")

def run_docker_command(command, check_return_code=False):
    try:
        full_command = ["docker", "exec", CONTAINER_NAME] + command
        process = subprocess.run(full_command, capture_output=True, text=True, check=False)

        if check_return_code:
            return process.returncode == 0
        if process.returncode != 0:
            return process.stderr.strip()
        return process.stdout.strip()
    except FileNotFoundError:
        print("Error: 'docker' command not found. Is Docker installed and in your PATH?")
        sys.exit(1)

def start_container():
    try:
        print(f"--> Checking container '{CONTAINER_NAME}' status...")
        inspect_cmd = ['docker', 'inspect', '-f', '{{.State.Status}}', CONTAINER_NAME]
        status_proc = subprocess.run(inspect_cmd, capture_output=True, text=True)

        if status_proc.returncode != 0:
             print(f"✗ Error: Container '{CONTAINER_NAME}' not found.")
             print("   Please complete Part 1 of the task first by running 'docker run...'.")
             return False

        status = status_proc.stdout.strip()
        if status == 'exited':
            print(f"--> Container is stopped. Starting '{CONTAINER_NAME}'...")
            subprocess.run(["docker", "start", CONTAINER_NAME], check=True, capture_output=True)
            print(f"✓ Container started successfully.")
        elif status == 'running':
            print(f"✓ Container is already running.")
        else:
            print(f"✗ Unknown container status: {status}")
            return False
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"✗ Failed to start or check container. Error: {e}")
        return False

def check_operations():
    global final_score
    print("\n--- Checking Part 1: File System Operations (inside Docker) ---")

    if run_docker_command(["test", "-d", "/challenge"], check_return_code=True):
        results.append({"name": "Directory Creation", "passed": True, "points": TESTS['Directory Creation']})
        final_score += TESTS['Directory Creation']
        print("✓ Passed: Directory Creation")
    else:
        results.append({"name": "Directory Creation", "passed": False, "points": 0})
        print("✗ Failed: Directory Creation")

    if run_docker_command(["test", "-f", "/challenge/data.txt"], check_return_code=True):
        results.append({"name": "File Creation", "passed": True, "points": TESTS['File Creation']})
        final_score += TESTS['File Creation']
        print("✓ Passed: File Creation")
    else:
        results.append({"name": "File Creation", "passed": False, "points": 0})
        print("✗ Failed: File Creation")

    content_output = run_docker_command(["cat", "/challenge/data.txt"])
    if content_output == "Docker is awesome!":
        results.append({"name": "File Content", "passed": True, "points": TESTS['File Content']})
        final_score += TESTS['File Content']
        print("✓ Passed: File Content")
    else:
        results.append({"name": "File Content", "passed": False, "points": 0})
        print("✗ Failed: File Content")

    copy_output = run_docker_command(["cat", "/opt/challenge/data.txt"])
    if copy_output == "Docker is awesome!":
        results.append({"name": "Directory Copy", "passed": True, "points": TESTS['Directory Copy']})
        final_score += TESTS['Directory Copy']
        print("✓ Passed: Directory Copy")
    else:
        results.append({"name": "Directory Copy", "passed": False, "points": 0})
        print("✗ Failed: Directory Copy")

# --- Part 2: QMD Quiz Functions ---
def get_quiz_questions():
    try:
        json_bytes = base64.b64decode(quiz_data.ENCODED_DATA)
        questions = json.loads(json_bytes)
        return questions
    except Exception as e:
        print(f"Error: Could not load or parse the embedded quiz data. {e}")
        return None

def run_quiz(questions):
    global final_score
    print("\n--- Starting Part 2: Multiple Choice Quiz ---")

    correct_count = 0
    for i, q in enumerate(questions):
        print(f"\nQuestion {i+1}/{len(questions)}: {q['question']}")
        sorted_options = sorted(q['options'].items())
        for letter, text in sorted_options:
            print(f"  {letter}. {text}")

        while True:
            try:
                user_input = input("Your choice (A/B/C/D): ").upper().strip()
                if user_input in q['options']:
                    if user_input == q['answer']:
                        correct_count += 1
                    break
                else:
                    print("Invalid input. Please enter A, B, C, or D.")
            except (EOFError, KeyboardInterrupt):
                print("\nQuiz aborted. Exiting.")
                sys.exit(0)

    score_per_question = TOTAL_QUIZ_SCORE / len(questions)
    quiz_score = round(correct_count * score_per_question)
    final_score += quiz_score

    results.append({
        "name": f"Quiz ({correct_count}/{len(questions)} correct)",
        "passed": True,
        "points": quiz_score
    })
    print(f"\n--- Quiz Finished ---")
    print(f"You answered {correct_count} out of {len(questions)} questions correctly.")

def encrypt_and_save_report():
    app_dir = os.path.dirname(os.path.realpath(sys.executable))
    report_file_path = os.path.join(app_dir, "autograding_report.json")

    final_results_data = {
        "score": final_score,
        "max_score": TOTAL_MAX_SCORE,
        "test_results": results
    }

    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(json.dumps(final_results_data).encode('utf-8'))
    encrypted_data = {
        "nonce": b64encode(nonce).decode('utf-8'),
        "ciphertext": b64encode(ciphertext).decode('utf-8'),
        "tag": b64encode(tag).decode('utf-8')
    }

    with open(report_file_path, "w") as f:
        f.write(json.dumps(encrypted_data))

    print("\n--- SUBMISSION CREATED ---")
    print(f"An encrypted submission file has been saved to {report_file_path}.")
    print("Please submit this file.")

if __name__ == "__main__":
    if not start_container():
        sys.exit(1)

    check_operations()

    quiz_questions = get_quiz_questions()
    if quiz_questions:
        run_quiz(quiz_questions)
    else:
        print("Error: Embedded quiz could not be loaded. Skipping quiz.")
        results.append({"name": "Quiz", "passed": False, "points": 0})

    print_final_report()
    encrypt_and_save_report()
