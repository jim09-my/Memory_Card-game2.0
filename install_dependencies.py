import subprocess
import sys
import os

def install_dependencies():
    print("Installing dependencies for Memory Card Game...")
    
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    if not os.path.exists(requirements_file):
        print("ERROR: requirements.txt not found!")
        return False
    
    try:
        cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_file]
        print("Running command:", " ".join(cmd))
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Dependencies installed successfully!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print("Failed to install dependencies!")
        print("Error:", e)
        print("Stdout:", e.stdout)
        print("Stderr:", e.stderr)
        return False
    except Exception as e:
        print("An error occurred:", e)
        return False

if __name__ == "__main__":
    success = install_dependencies()
    if success:
        print("\nAll dependencies installed successfully!")
        print("You can now run the game using: python main.py")
    else:
        print("\nFailed to install dependencies!")
        sys.exit(1)