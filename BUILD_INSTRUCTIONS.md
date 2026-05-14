# 🏗️ Build VRChat Bot Executable

## 📋 Prerequisites

- Python 3.7 or higher
- Windows operating system (for .exe creation)
- Administrative privileges (recommended)

## 🚀 Quick Build

### **Step 1: Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# Or install PyInstaller manually
pip install pyinstaller>=5.0.0
```

### **Step 2: Build the Executable**
```bash
# Run the build script
python build_exe.py
```

This will:
- ✅ Check dependencies
- ✅ Build the .exe file
- ✅ Create a portable package
- ✅ Test the executable

### **Step 3: Test the Launcher**
```bash
# Run the built executable
dist/VRChatBotLauncher.exe
```

## 📦 Build Results

After successful build, you'll get:

### **Executable File**
- **Location**: `dist/VRChatBotLauncher.exe`
- **Size**: ~20-30 MB
- **Type**: Standalone Windows executable

### **Portable Package**
- **Location**: `VRChatBot_Portable/`
- **Contents**:
  - `VRChatBotLauncher.exe` - Main launcher
  - `START_BAT_HERE.bat` - Quick startup script
  - `.env.dual_mode` - Configuration template
  - All Python scripts (for advanced users)
  - `README_PORTABLE.md` - User guide

## 🎮 Using the Executable

### **First Time Setup**
1. **Copy configuration file**:
   ```
   copy .env.dual_mode .env
   ```

2. **Edit credentials**:
   - Open `.env` in Notepad
   - Add your VRChat username and password
   - Save the file

3. **Run the launcher**:
   - Double-click `VRChatBotLauncher.exe`
   - Choose your mode with number keys:
     - **Press 1** for VRChat Mode
     - **Press 2** for Standby Mode
     - **Press 3** for System Helper Mode
     - **Press 4** for Minimal VRChat

### **Mode Selection**

| Mode | Description | Use Case |
|------|-------------|----------|
| **1 - VRChat Mode** | Full VRChat integration with system helper | Active VRChat usage |
| **2 - Standby Mode** | Minimal resource usage with monitoring | Background operation |
| **3 - System Helper** | Disk cleanup and optimization only | System maintenance |
| **4 - Minimal VRChat** | Lightweight VRChat for low resources | Resource-constrained systems |

## 🔧 Advanced Build Options

### **Custom Build Command**
```bash
# Manual PyInstaller command
pyinstaller --clean --onefile --add-data ".env.example;." --add-data "config.yaml;." launcher.py
```

### **Build Without Console**
```bash
# For GUI-only version
pyinstaller --clean --onefile --windowed --add-data ".env.example;." launcher.py
```

### **Include Additional Files**
```bash
# Add more data files
pyinstaller --clean --onefile --add-data "*.yaml;." --add-data "*.md;." launcher.py
```

## 🐛 Troubleshooting

### **Build Issues**

**❌ "PyInstaller not found"**
```bash
pip install pyinstaller
```

**❌ "ModuleNotFoundError"**
```bash
# Add missing modules to hiddenimports in build_exe.py
```

**❌ "Antivirus detection"**
- The .exe may be flagged by some antivirus software
- Add an exception in your antivirus settings
- This is a false positive due to PyInstaller

**❌ "Missing DLL files"**
- Install Microsoft Visual C++ Redistributable
- Use `--noconfirm` flag with PyInstaller

### **Runtime Issues**

**❌ "Cannot find .env file"**
- Ensure `.env` is in the same directory as the .exe
- Copy from `.env.dual_mode` and edit it

**❌ "VRChat authentication failed"**
- Check your credentials in `.env`
- Verify 2FA code if enabled
- Ensure internet connection is working

**❌ "Bot won't start"**
- Check `launcher.log` for error messages
- Try running as administrator
- Verify all Python scripts are present

## 📊 Build Specifications

### **Included Components**
- ✅ Main launcher with GUI and CLI
- ✅ All bot modes (VRChat, Standby, System Helper, Minimal)
- ✅ Configuration files and templates
- ✅ Documentation and README files
- ✅ Error handling and logging

### **Excluded Components**
- ❌ Development dependencies (pytest, black, etc.)
- ❌ Heavy libraries (numpy, matplotlib, etc.)
- ❌ Debug symbols and source maps
- ❌ Unused Python modules

### **Optimizations**
- ✅ UPX compression for smaller size
- ✅ Excluded unnecessary modules
- ✅ Single-file distribution
- ✅ Minimal dependencies

## 🎯 Distribution

### **For End Users**
1. Send the `VRChatBot_Portable/` folder
2. Instructions: Copy `.env.dual_mode` to `.env` and add credentials
3. Run `VRChatBotLauncher.exe`

### **For Advanced Users**
1. Send just `VRChatBotLauncher.exe`
2. Provide Python scripts separately if needed
3. Users can modify scripts for custom behavior

### **System Requirements**
- **OS**: Windows 7 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 500MB free space
- **Network**: Internet connection for VRChat features

## 🔄 Updates and Maintenance

### **Updating the Bot**
1. Build new executable with updated scripts
2. Replace the old .exe file
3. Users keep their `.env` configuration

### **Version Management**
- Include version number in executable name
- Maintain changelog for updates
- Test thoroughly before distribution

---

**🎉 Your VRChat Bot executable is ready for distribution!**
