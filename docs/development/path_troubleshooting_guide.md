# Python PATH Troubleshooting Guide
**Created: August 31, 2025**

## 🚨 Issue: Python/Pip PATH Errors in WSL

### Problem Description
Users are experiencing PATH errors when trying to run Python and pip commands in WSL (Windows Subsystem for Linux):

```bash
fish: Unknown command. A component of '/mnt/c/Program Files/PostgreSQL/16/bin/psql.exe/pip' is not a directory. Check your $PATH.
```

### Root Cause Analysis
The issue occurs when:
1. PostgreSQL binaries are in PATH before Python binaries
2. WSL shell (fish/bash) is trying to execute pip/python from wrong location
3. PATH environment variable has conflicting entries

### Immediate Solutions

#### Solution 1: Check and Fix PATH Order
```bash
# Check current PATH
echo $PATH

# Find Python installations
which python3
which pip3

# If not found, locate Python
find /usr -name python3 2>/dev/null
find /mnt/c -name python.exe 2>/dev/null

# Add Python to PATH (temporary fix)
export PATH="/usr/bin:/mnt/c/Python312:/mnt/c/Python312/Scripts:$PATH"
```

#### Solution 2: Use Full Path Commands
```bash
# Instead of 'pip install'
/usr/bin/python3 -m pip install speech_recognition pyttsx3 pyaudio

# Instead of 'python voice_interface.py'
/usr/bin/python3 voice_interface.py
```

#### Solution 3: Create Aliases (Quick Fix)
```bash
# Add to ~/.bashrc or ~/.fishrc
alias python='/usr/bin/python3'
alias pip='/usr/bin/python3 -m pip'
alias python3='/usr/bin/python3'
alias pip3='/usr/bin/python3 -m pip3'
```

### Permanent Fixes

#### Fix 1: Update Shell Configuration
**For Bash (.bashrc):**
```bash
echo 'export PATH="/usr/bin:/usr/local/bin:$PATH"' >> ~/.bashrc
echo 'alias python="/usr/bin/python3"' >> ~/.bashrc
echo 'alias pip="/usr/bin/python3 -m pip"' >> ~/.bashrc
source ~/.bashrc
```

**For Fish (.fishrc):**
```fish
echo 'set -x PATH /usr/bin /usr/local/bin $PATH' >> ~/.config/fish/config.fish
echo 'alias python="/usr/bin/python3"' >> ~/.config/fish/config.fish
echo 'alias pip="/usr/bin/python3 -m pip"' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

#### Fix 2: Install Python System-Wide
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

#### Fix 3: Use Windows Python from WSL
```bash
# Add Windows Python to PATH
export PATH="/mnt/c/Python312:/mnt/c/Python312/Scripts:$PATH"

# Create aliases
alias python='/mnt/c/Python312/python.exe'
alias pip='/mnt/c/Python312/Scripts/pip.exe'
```

### Package Installation Commands

#### For Speech Recognition Project
```bash
# Using system Python
python3 -m pip install speech_recognition pyttsx3 pyaudio

# Using Windows Python
/mnt/c/Python312/python.exe -m pip install speech_recognition pyttsx3 pyaudio

# Using pip3 directly
pip3 install speech_recognition pyttsx3 pyaudio
```

### Verification Steps

#### Test Python Installation
```bash
# Check Python version
python3 --version

# Test pip
python3 -m pip --version

# Test package installation
python3 -c "import speech_recognition; print('Speech recognition installed')"
python3 -c "import pyttsx3; print('pyttsx3 installed')"
```

#### Test Voice Interface Script
```bash
# Run the script
python3 voice_interface.py

# Or with full path
/usr/bin/python3 voice_interface.py
```

### Prevention Measures

#### 1. Environment Setup Script
Create a setup script for future use:

```bash
#!/bin/bash
# setup_python_env.sh

# Fix PATH
export PATH="/usr/bin:/usr/local/bin:$PATH"

# Install required packages
python3 -m pip install --user speech_recognition pyttsx3 pyaudio

# Create aliases
echo 'alias python="/usr/bin/python3"' >> ~/.bashrc
echo 'alias pip="/usr/bin/python3 -m pip"' >> ~/.bashrc

echo "Python environment setup complete!"
```

#### 2. Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv myenv

# Activate
source myenv/bin/activate

# Install packages
pip install speech_recognition pyttsx3 pyaudio

# Run script
python voice_interface.py
```

### Common Error Patterns & Solutions

#### Error: "pip: command not found"
**Solution:**
```bash
# Install pip
sudo apt install python3-pip

# Or use python module
python3 -m ensurepip --upgrade
```

#### Error: "python: command not found"
**Solution:**
```bash
# Install python
sudo apt install python3

# Create symlink
sudo ln -s /usr/bin/python3 /usr/bin/python
```

#### Error: "ModuleNotFoundError"
**Solution:**
```bash
# Install in user directory
python3 -m pip install --user package_name

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install package_name
```

### Documentation Updates Needed

#### Files to Update:
- `docs/development/development.md` - Add PATH troubleshooting section
- `docs/development/setup_guide.md` - Create comprehensive setup guide
- `README.md` - Add environment setup instructions

#### Related Issues:
- WSL PATH configuration
- Python package management
- Development environment consistency
- Cross-platform compatibility

### Next Steps for Development Team

1. **Immediate**: Update development documentation with PATH fixes
2. **Short-term**: Create automated environment setup scripts
3. **Long-term**: Implement containerized development environment (Docker)
4. **Testing**: Add PATH validation to CI/CD pipeline

---

**Status**: ✅ Documented and ready for implementation
**Priority**: High (blocks development workflow)
**Assignee**: Development team
**Timeline**: Complete within 24 hours

### Current Status (August 31, 2025)

#### ✅ **What We've Accomplished**
- **Issue Identified**: PATH conflicts between PostgreSQL and Python binaries in WSL
- **Root Cause**: Shell trying to execute pip/python from `/mnt/c/Program Files/PostgreSQL/16/bin/psql.exe/`
- **Documentation**: Created comprehensive troubleshooting guide
- **Python Location**: Confirmed Python3 available at `/usr/bin/python3`
- **Requirements File**: Created `requirements.txt` for speech recognition packages

#### 🔄 **Current Blockers**
- **Pip Installation**: System pip not available (permission issues with apt)
- **Package Installation**: Cannot install speech_recognition, pyttsx3, pyaudio
- **WSL Environment**: Limited permissions for system package installation

#### 💡 **Immediate Solutions Available**

**Option 1: Use Windows Python (if available)**
```bash
# Find Windows Python installation
find /mnt/c -name "python.exe" -type f 2>/dev/null

# Use Windows pip
/mnt/c/Python312/python.exe -m pip install speech_recognition pyttsx3 pyaudio
```

**Option 2: Manual Package Download**
```bash
# Download packages manually
python3 -c "
import urllib.request
import zipfile
import os

# Download speech_recognition
url = 'https://files.pythonhosted.org/packages/0e/7a/4f9e0c0a93b31a76f3e9e8c7d6e5f4a3b2c1d0e9f8a7/speech_recognition-3.10.0-py2.py3-none-any.whl'
urllib.request.urlretrieve(url, 'speech_recognition.whl')
"
```

**Option 3: Use Alternative Package Manager**
```bash
# If conda is available
conda install speech_recognition pyttsx3 pyaudio

# Or use pip with --user flag when pip becomes available
python3 -m pip install --user speech_recognition pyttsx3 pyaudio
```

#### 📋 **Next Steps for Resolution**

1. **Immediate**: Try Windows Python installation
2. **Short-term**: Install pip manually using urllib method
3. **Alternative**: Use conda or miniconda for package management
4. **Documentation**: Update this guide with successful resolution method

#### 🔧 **Commands to Try**

```bash
# Test current Python
/usr/bin/python3 --version

# Try to run voice interface (may work without pip if packages pre-installed)
/usr/bin/python3 voice_interface.py

# Check for existing installations
python3 -c "import sys; print(sys.path)"

# Alternative installation methods
python3 -c "import urllib.request; exec(urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py').read())"
```

---

**Status**: 🔄 In Progress - PATH issue documented, multiple solutions identified
**Next Action**: Test Windows Python or manual pip installation
**Timeline**: Resolution expected within 1 hour</content>
<parameter name="filePath">e:\Polymath Universata\Projects\Nimo\docs\development\path_troubleshooting_guide.md