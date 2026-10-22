import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: write_helper.py <filepath>")
        sys.exit(1)
    target = sys.argv[1]
    os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
    content = sys.stdin.read()
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully wrote {len(content)} bytes to {target}")

if __name__ == "__main__":
    main()
