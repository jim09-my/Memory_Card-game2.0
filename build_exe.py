import os
import sys
import subprocess
import shutil

def build_executable():
    """Build the executable using PyInstaller"""
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',  # Single executable file
        '--windowed',  # No console window
        '--name', 'MemoryCardGame',  # Executable name
        '--icon', 'NONE',  # No icon for now
        '--add-data', 'assets;assets',  # Include assets folder
        '--add-data', 'data;data',  # Include data folder
        '--hidden-import', 'PIL._tkinter_finder',
        'main.py'
    ]
    
    print("Building executable...")
    print("Command:", ' '.join(cmd))
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Build successful!")
        print(result.stdout)
        
        # Copy the executable to project root
        dist_dir = os.path.join(project_dir, 'dist')
        exe_file = os.path.join(dist_dir, 'MemoryCardGame.exe')
        if os.path.exists(exe_file):
            shutil.copy2(exe_file, project_dir)
            print(f"Executable copied to: {os.path.join(project_dir, 'MemoryCardGame.exe')}")
        else:
            print("Executable not found in dist folder")
            
    except subprocess.CalledProcessError as e:
        print("Build failed!")
        print("Error:", e)
        print("Stdout:", e.stdout)
        print("Stderr:", e.stderr)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == '__main__':
    build_executable()