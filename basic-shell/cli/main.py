import json
import sys

def validate(file_path):
    try:
        with open(file_path) as f:
            data = json.load(f)
        print("✅ Valid JSON")
    except Exception as e:
        print("❌ Invalid:", e)

if __name__ == "__main__":
    command = sys.argv[1]
    path = sys.argv[2]

    if command == "validate":
        validate(path)