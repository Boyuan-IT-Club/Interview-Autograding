import json
import sys
import base64
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import os

# --- SECRET KEY ---
# 从 etc/config 文件中加载密钥
try:
    # 使用 os.path.realpath(sys.executable) 获取可执行文件的真实路径
    # 这在 PyInstaller 打包的单文件可执行文件中非常重要
    app_path = os.path.realpath(sys.executable)
    # 获取可执行文件所在的目录
    app_dir = os.path.dirname(app_path)
    # 获取项目根目录，这里假设etc文件夹在可执行文件的上一级目录
    project_root = os.path.dirname(app_dir)
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


def decrypt_report(encrypted_data_string):
    """Decrypts the report data using AES."""
    try:
        encrypted_data = json.loads(encrypted_data_string)
        nonce = b64decode(encrypted_data['nonce'])
        ciphertext = b64decode(encrypted_data['ciphertext'])
        tag = b64decode(encrypted_data['tag'])

        cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        
        return json.loads(decrypted_data.decode('utf-8'))
    except Exception as e:
        return {"error": f"Decryption failed: {e}"}

def main(file_path):
    """Reads an encrypted report from a file and decrypts it."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, "r") as f:
        encrypted_data_string = f.read()

    decrypted_result = decrypt_report(encrypted_data_string)

    if "error" in decrypted_result:
        print(f"Error: {decrypted_result['error']}")
        print("This file may have been tampered with or corrupted.")
    else:
        print("\n--- DECRYPTED REPORT ---")
        print(f"Final Score: {decrypted_result['score']}/{decrypted_result['max_score']}")
        print("Test Results:")
        for result in decrypted_result['test_results']:
            status = 'Passed' if result['passed'] else 'Failed'
            points = result['points']
            print(f"  - {result['name']}: {status} (+{points}pts)")
        print("------------------------\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Decrypts an autograding report.")
    parser.add_argument("file", help="Path to the encrypted report file.")
    
    args = parser.parse_args()
    main(args.file)