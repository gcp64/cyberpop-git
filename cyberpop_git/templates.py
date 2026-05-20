"""
Cyberpop Templates Module
Implements smart filesystem scanning to detect project technologies and frameworks.
Generates highly optimized and professional .gitignore files by merging templates.
"""

import os
from pathlib import Path

# --- .gitignore Templates ---

OS_IDE_TEMPLATE = """# ==========================================
# Cyberpop Git CLI Generated .gitignore
# OS & IDE Configuration
# ==========================================

# OS Files
[Dd]esktop.ini
Thumbs.db
ehthumbs.db
.DS_Store
.AppleDouble
.LSOverride

# IDEs and Editors
.vscode/
.idea/
*.suo
*.ntvs*
*.njsproj
*.sln
*.swp
*.swo
.project
.classpath
.settings/
"""

PYTHON_TEMPLATE = """# ==========================================
# Python Development Environment
# ==========================================
__pycache__/
*.py[cod]
*$py.class
.ipynb_checkpoints

# Virtual Environments
.venv/
venv/
ENV/
env/
active/
*.venv

# Distribution & Build
dist/
build/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing & Coverage
.cache/
.pytest_cache/
.tox/
.nox/
.coverage
.coverage.*
.hypothesis/
htmlcov/
nosetests.xml
coverage.xml
*.cover
"""

NODE_TEMPLATE = """# ==========================================
# Node.js & Modern Frontend (React, Vue, Next)
# ==========================================
node_modules/
/dist/
/build/
/out/
.next/
.nuxt/
.cache/
.docusaurus/
.parcel-cache/
.turbo/

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*

# Environments & Local Configs
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.eslintcache
"""

RUST_TEMPLATE = """# ==========================================
# Rust Lang Development
# ==========================================
/target/
**/*.rs.bk
"""

GO_TEMPLATE = """# ==========================================
# Go Lang Development
# ==========================================
# Compiled binaries
bin/
pkg/

# Workspaces
go.work
go.work.sum
"""

CPP_TEMPLATE = """# ==========================================
# C / C++ Development
# ==========================================
# Compiled Object files
*.o
*.obj
*.ko
*.gch
*.pch

# Compiled Dynamic Libraries
*.so
*.dylib
*.dll

# Compiled Static Libraries
*.lai
*.la
*.a
*.lib

# Executables
*.out
*.app
"""

def detect_languages(directory_path: str = ".") -> list[str]:
    """
    Scans the directory for structural files to detect programming languages.
    Avoids entering heavy ignored directories (.git, node_modules, .venv) for speed.
    """
    detected = []
    dir_path = Path(directory_path)
    
    # Files to look for
    indicators = {
        "Python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "poetry.lock"],
        "Node/React": ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
        "Rust": ["Cargo.toml", "Cargo.lock"],
        "Go": ["go.mod", "go.sum", "main.go"],
        "C/C++": ["CMakeLists.txt", "Makefile"]
    }
    
    # Check root first for speed
    for lang, files in indicators.items():
        for filename in files:
            if (dir_path / filename).exists():
                if lang not in detected:
                    detected.append(lang)
                    
    # File extension scan in root and immediate subdirs (depth=2)
    python_found = False
    node_found = False
    rust_found = False
    go_found = False
    cpp_found = False
    
    skip_dirs = {".git", ".venv", "venv", "node_modules", "target", "build", "dist"}
    
    try:
        for entry in os.scandir(directory_path):
            if entry.is_dir() and entry.name not in skip_dirs:
                # Scan immediate subdirectory
                try:
                    for sub_entry in os.scandir(entry.path):
                        if sub_entry.is_file():
                            ext = Path(sub_entry.name).suffix.lower()
                            if ext == ".py": python_found = True
                            elif ext in [".js", ".jsx", ".ts", ".tsx"]: node_found = True
                            elif ext == ".rs": rust_found = True
                            elif ext == ".go": go_found = True
                            elif ext in [".cpp", ".hpp", ".c", ".h"]: cpp_found = True
                except Exception:
                    pass
            elif entry.is_file():
                ext = Path(entry.name).suffix.lower()
                if ext == ".py": python_found = True
                elif ext in [".js", ".jsx", ".ts", ".tsx"]: node_found = True
                elif ext == ".rs": rust_found = True
                elif ext == ".go": go_found = True
                elif ext in [".cpp", ".hpp", ".c", ".h"]: cpp_found = True
    except Exception:
        pass
        
    if python_found and "Python" not in detected: detected.append("Python")
    if node_found and "Node/React" not in detected: detected.append("Node/React")
    if rust_found and "Rust" not in detected: detected.append("Rust")
    if go_found and "Go" not in detected: detected.append("Go")
    if cpp_found and "C/C++" not in detected: detected.append("C/C++")
    
    return detected

def generate_gitignore_content(detected_langs: list[str]) -> str:
    """Merges .gitignore templates based on detected languages."""
    content = OS_IDE_TEMPLATE
    
    for lang in detected_langs:
        if lang == "Python":
            content += "\n" + PYTHON_TEMPLATE
        elif lang == "Node/React":
            content += "\n" + NODE_TEMPLATE
        elif lang == "Rust":
            content += "\n" + RUST_TEMPLATE
        elif lang == "Go":
            content += "\n" + GO_TEMPLATE
        elif lang == "C/C++":
            content += "\n" + CPP_TEMPLATE
            
    return content
