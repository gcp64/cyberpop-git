"""
Cyberpop Build Automation Script
Automates the PyInstaller packaging process to compile a clean,
lightweight standalone Windows (.exe) executable from the Python sources.
Automatically installs PyInstaller in the venv if missing and applies optimizations.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Cyberpunk-style print helpers for python command line execution (fallback if rich isn't loaded in build host yet)
def print_cyan(text): print(f"\033[96m{text}\033[0m")
def print_magenta(text): print(f"\033[95m{text}\033[0m")
def print_green(text): print(f"\033[92m{text}\033[0m")
def print_red(text): print(f"\033[91m{text}\033[0m")
def print_yellow(text): print(f"\033[93m{text}\033[0m")

def check_venv() -> Path:
    """Verifies that we are running inside the correct directory and returns python executable in venv."""
    current_dir = Path(".").resolve()
    python_exe = current_dir / ".venv" / "Scripts" / "python.exe"
    
    if not python_exe.exists():
        # Fallback to sys.executable if .venv not found (e.g. system python)
        print_yellow("⚠️ Local virtual environment .venv not found in current directory. Falling back to active system python.")
        return Path(sys.executable)
        
    return python_exe

def check_dependencies(python_exe: Path):
    """Checks and installs required packages (PyInstaller, PyArmor) in the virtual environment."""
    pip_exe = python_exe.parent / "pip.exe"
    if not pip_exe.exists():
        pip_exe = Path("pip")
        
    for pkg in ["PyInstaller", "pyarmor"]:
        print_cyan(f"🔍 Checking {pkg} presence...")
        import_name = "pyarmor" if pkg == "pyarmor" else pkg
        try:
            subprocess.run([str(python_exe), "-c", f"import {import_name}"], check=True, capture_output=True)
            print_green(f"✔ {pkg} is already installed inside environment.")
        except subprocess.CalledProcessError:
            print_yellow(f"⚡ {pkg} is missing. Initializing automatic installation in virtual environment...")
            try:
                subprocess.run([str(pip_exe), "install", pkg.lower()], check=True)
                print_green(f"✔ {pkg} successfully installed!")
            except Exception as e:
                print_red(f"🗲 Failed to install {pkg}: {str(e)}")
                sys.exit(1)

def run_build(python_exe: Path):
    """Executes the optimized and obfuscated PyInstaller build process."""
    pyinstaller_exe = python_exe.parent / "pyinstaller.exe"
    if not pyinstaller_exe.exists():
        pyinstaller_exe = Path("pyinstaller")
        
    pyarmor_exe = python_exe.parent / "pyarmor.exe"
    if not pyarmor_exe.exists():
        pyarmor_exe = Path("pyarmor")
        
    entry_point = Path("cyberpop_git") / "main.py"
    if not entry_point.exists():
        print_red("🗲 Error: Entry point 'cyberpop_git/main.py' not found! Make sure you run from project root.")
        sys.exit(1)

    print_magenta("\n" + "="*60)
    print_magenta("👾 CYBERPOP CLI SECURE COMPILATION PROTOCOL ACTIVATED 👾")
    print_magenta("="*60 + "\n")
    
    # 1. Run PyArmor Obfuscation
    print_magenta("🔐 Activating PyArmor Obfuscation Layer...")
    obf_dir = Path("dist") / "obf"
    if obf_dir.exists():
        shutil.rmtree(obf_dir)
        
    cyberpop_git_dir = Path("cyberpop_git")
    files_to_obfuscate = [
        cyberpop_git_dir / "main.py",
        cyberpop_git_dir / "ui.py",
        cyberpop_git_dir / "config.py",
        cyberpop_git_dir / "git_manager.py",
        cyberpop_git_dir / "ai_service.py",
        cyberpop_git_dir / "templates.py",
        cyberpop_git_dir / "__init__.py"
    ]
    
    obf_package_dir = obf_dir / "cyberpop_git"
    pyarmor_cmd = [
        str(pyarmor_exe),
        "gen",
        "-O", str(obf_package_dir)
    ] + [str(f) for f in files_to_obfuscate]
    
    print_cyan(f"🚀 Running obfuscation: {' '.join(pyarmor_cmd)}")
    try:
        subprocess.run(pyarmor_cmd, check=True)
        print_green("✔ Source files successfully obfuscated into dist/obf/cyberpop_git")
    except subprocess.CalledProcessError as e:
        print_red(f"🗲 PyArmor obfuscation failed. Exit code: {e.returncode}")
        sys.exit(1)
        
    # 2. Run PyInstaller on the obfuscated entry point
    excludes = [
        "tkinter", "tcl", "tk", "unittest", "pydoc", "pdb", "sqlite3",
        "distutils", "setuptools",
        "multiprocessing", "concurrent", "socketserver", "xmlrpc", "dbm", "msilib",
        "ensurepip", "idlelib", "lib2to3", "pydoc_data", "zoneinfo", "difflib"
    ]
    
    obf_entry_point = obf_package_dir / "main.py"
    build_cmd = [
        str(pyinstaller_exe),
        "--onefile",
        "--name=cyberpop-git",
        "--clean",
        "--icon=cyberpop_git/icon.ico",
        "--paths", "dist/obf",
        "--paths", "dist/obf/cyberpop_git",
        "--hidden-import=cyberpop_git.ui",
        "--hidden-import=cyberpop_git.config",
        "--hidden-import=cyberpop_git.git_manager",
        "--hidden-import=cyberpop_git.ai_service",
        "--hidden-import=cyberpop_git.templates",
        "--hidden-import=cyberpop_git.__init__",
        "--hidden-import=pyarmor_runtime_000000",
        "--hidden-import=rich",
        "--hidden-import=requests",
        "--hidden-import=certifi",
        "--hidden-import=cryptography",
        "--hidden-import=arabic_reshaper",
        "--hidden-import=bidi",
        "--hidden-import=bidi.algorithm",
        "--hidden-import=urllib3",
        "--hidden-import=uuid",
        "--hidden-import=winreg",
        "--hidden-import=json",
        "--hidden-import=hashlib",
        "--hidden-import=base64",
        "--hidden-import=sys",
        "--hidden-import=os",
        "--hidden-import=shutil",
        "--hidden-import=subprocess",
        "--hidden-import=argparse",
        "--hidden-import=traceback",
        "--hidden-import=hmac",
        "--hidden-import=pathlib"
    ]
    
    # Add exclusions
    for mod in excludes:
        build_cmd.extend(["--exclude-module", mod])
        
    # Add obfuscated target entry point
    build_cmd.append(str(obf_entry_point))
    
    print_cyan(f"\n🚀 Running compilation: {' '.join(build_cmd)}")
    
    try:
        subprocess.run(build_cmd, check=True)
        
        # Clean build artifacts to leave workspace pristine
        print_cyan("\n🧹 Cleaning intermediate compilation artifacts...")
        spec_file = Path("cyberpop-git.spec")
        build_folder = Path("build")
        
        if spec_file.exists():
            os.remove(spec_file)
        if build_folder.exists():
            shutil.rmtree(build_folder)
        if obf_dir.exists():
            shutil.rmtree(obf_dir)
            
        exe_path = Path("dist") / "cyberpop-git.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print_green("\n" + "#"*60)
            print_green("🌟 COMPILATION COMPLETED SUCCESSFULLY! 🌟")
            print_green(f"  Target Executable: {exe_path.resolve()}")
            print_green(f"  Obfuscated and Secure: YES (PyArmor AES + Hardware Fingerprint)")
            print_green(f"  Optimized Size: {size_mb:.2f} MB (Extremely compact!)")
            print_green("#"*60 + "\n")
        else:
            print_red("🗲 Output file was not found inside 'dist/' directory.")
            
    except subprocess.CalledProcessError as e:
        print_red(f"\n🗲 PyInstaller compilation failed. Exit code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print_red(f"\n🗲 Unexpected build failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform == "win32":
        os.system("color")
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
        
    python_path = check_venv()
    check_dependencies(python_path)
    run_build(python_path)
