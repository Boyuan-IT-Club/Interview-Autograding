import sys
import subprocess
import os

# 定义所有任务的列表，你可以根据需要在这里添加或删除任务。
ALL_TASKS = ['task1']

def run_task_grader(task_name):
    """
    Runs the specific task's grading script.
    
    Args:
        task_name (str): The name of the task (e.g., 'task1').
    """
    # Get the directory where this script is located
    # This is reliable even when packed with PyInstaller
    grade_script_dir = os.path.dirname(os.path.realpath(sys.executable))
    
    # Construct the path to the specific task's executable
    # Assumes task executables are structured as: tasks/taskN/taskN
    task_script_path = os.path.join(grade_script_dir, task_name, task_name)
    
    # Check if the task executable exists
    if not os.path.exists(task_script_path):
        print(f"Error: Task executable not found for '{task_name}'.")
        print(f"Expected path: {task_script_path}")
        sys.exit(1)
        
    print(f"\n--- Running grader for {task_name} ---")
    
    try:
        # Execute the task executable and capture its output
        result = subprocess.run(
            [task_script_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the grader for {task_name}:")
        print(e.stderr)
        sys.exit(1)

def main():
    """
    Main function to parse arguments and run the grader.
    """
    # 如果没有提供参数，则打印使用说明
    if len(sys.argv) == 1:
        print("Usage: ./grade [-a | task_name1 task_name2 ...]")
        print("Example: ./grade task1 task3")
        print("To run all tasks: ./grade -a")
        sys.exit(1)
    elif len(sys.argv) > 1:
        args = sys.argv[1:]
        if args[0] == '-a':
            # Run all tasks if '-a' flag is provided
            print("Running all tasks...")
            for task in ALL_TASKS:
                run_task_grader(task)
            print("\n--- All tasks completed ---")
        else:
            # Run multiple specific tasks
            for task_name in args:
                if task_name not in ALL_TASKS:
                    print(f"Error: Unknown task '{task_name}'.")
                    print("Available tasks are: " + ", ".join(ALL_TASKS))
                    sys.exit(1)
                run_task_grader(task_name)
    else:
        # This part of the code is unreachable due to the first if statement, but it's good practice to have a general else
        print("Usage: ./grade [-a | task_name1 task_name2 ...]")
        print("Example: ./grade task1 task3")
        print("To run all tasks: ./grade -a")
        sys.exit(1)

if __name__ == "__main__":
    main()
