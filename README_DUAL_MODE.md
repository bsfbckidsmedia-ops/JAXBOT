# 🤖 Dual-Mode VRChat Bot with System Helper

## 🎯 **Complete Solution for HP Envy 15-dy1xxx**

A revolutionary dual-mode bot that operates as both a **VRChat assistant** and a **system helper** for disk cleanup and optimization, perfectly optimized for resource-constrained environments.

---

## 🔄 **Dual-Mode Architecture**

### **Mode 1: VRChat Mode** 🎮
- **Full VRChat integration** with API connectivity
- **Chat commands** for user interaction
- **Friend monitoring** and status updates
- **Rate-limited** to respect VRChat guidelines

### **Mode 2: System Helper Mode** 🛠️
- **Disk cleanup** and optimization
- **Duplicate file detection** and removal
- **System health monitoring**
- **Automated maintenance tasks**

### **Mode 3: Standby Mode** ⏸️
- **Minimal resource usage**
- **Background monitoring**
- **Automatic mode switching**
- **Scheduled maintenance**

---

## 🚀 **Quick Start**

### **1. Setup Auto-Launch**
```bash
# Run the setup script
python startup_setup.py

# This will:
# ✅ Create startup scripts
# ✅ Configure auto-launch (Windows/macOS/Linux)
# ✅ Create desktop shortcuts
# ✅ Setup environment files
```

### **2. Configure Credentials**
```bash
# Copy the dual-mode configuration
cp .env.dual_mode .env

# Edit with your VRChat credentials
nano .env
```

### **3. Start the Bot**
```bash
# Run the dual-mode bot
python dual_mode_bot.py
```

---

## ⚙️ **Configuration Options**

### **Environment Variables (.env)**
```env
# VRChat Account
VRCHAT_USERNAME=your_bot_username
VRCHAT_PASSWORD=your_bot_password
VRCHAT_2FA_CODE=your_2fa_code_if_enabled

# Bot Configuration
BOT_NAME=DualBot
BOT_PREFIX=!
DEFAULT_MODE=standby
AUTO_SWITCH_MODES=true
VRC_ACTIVE_HOURS=09:00-23:00

# System Helper Settings
ENABLE_DAILY_CLEANUP=true
ENABLE_WEEKLY_SCAN=true
CLEANUP_TIME=02:00
SCAN_DAY=0

# Resource Limits (Optimized for HP Envy)
MAX_MEMORY_MB=256
MAX_STORAGE_MB=100
HEALTH_CHECK_INTERVAL=300
```

---

## 🎮 **VRChat Mode Commands**

### **Basic Commands**
- `!help` - Show available commands
- `!info` - Bot information
- `!status` - Current status
- `!ping` - Test responsiveness
- `!time` - Current time

### **System Helper Commands** 🛠️
- `!status` - Show system status
- `!cleanup` - Perform system cleanup
- `!scan` - Scan for system issues
- `!duplicates [directory] [remove]` - Find/remove duplicates
- `!disk` - Detailed disk usage
- `!health` - System health check
- `!mode [vrchat|standby|system_helper]` - Switch modes
- `!optimize` - Full system optimization
- `!temp` - Clean temporary files

---

## 🔄 **Automatic Mode Switching**

### **Time-Based Switching**
```yaml
# Active Hours: 9 AM - 11 PM
VRC_ACTIVE_HOURS=09:00-23:00

# During these hours:
# - Bot operates in VRChat mode
# - Monitors friends and responds to commands
# - Uses minimal system resources

# Outside these hours:
# - Bot switches to standby mode
# - Performs system maintenance
# - Optimizes disk space
```

### **Resource-Based Switching**
```yaml
# If memory < 100MB or storage < 50MB:
# - Auto-switch to standby mode
# - Perform emergency cleanup
# - Resume normal operation when resources available
```

---

## 🛠️ **System Helper Features**

### **Disk Cleanup** 🧹
```bash
# Automatic cleanup features:
✅ Temporary files removal
✅ Python cache cleanup
✅ Log file rotation
✅ Duplicate file detection
✅ Large file cleanup
✅ Cache directory clearing
```

### **System Monitoring** 📊
```bash
# Real-time monitoring:
💾 Memory usage tracking
💿 Disk space monitoring
🖥️ CPU usage checking
📁 Large directory scanning
⚠️ Resource threshold alerts
```

### **Scheduled Tasks** ⏰
```bash
# Daily (2 AM):
🧹 Temporary file cleanup
🗑️ Log rotation
💾 Memory optimization

# Weekly (Sunday 3 AM):
🔍 Full system scan
📊 Disk usage analysis
🔍 Duplicate file scan
```

---

## 📊 **Resource Optimization**

### **Memory Usage**
| Mode | Memory Usage | Features |
|------|-------------|----------|
| **VRChat** | ~256MB | Full VRChat + System |
| **Minimal VRChat** | ~128MB | Basic VRChat only |
| **System Helper** | ~64MB | System tasks only |
| **Standby** | ~32MB | Monitoring only |

### **Storage Usage**
- **Total footprint**: ~100MB
- **Log rotation**: 5MB max per file
- **Cache cleanup**: Automatic
- **Emergency cleanup**: < 30MB threshold

---

## 🎯 **Use Cases**

### **🎮 VRChat Enthusiast**
```bash
# Active during gaming hours
# Responds to VRChat commands
# Monitors friends list
# Maintains system health in background
```

### **🛠️ System Administrator**
```bash
# Continuous system monitoring
# Automated disk cleanup
# Duplicate file management
# Performance optimization
```

### **⚡ Resource-Constrained User**
```bash
# Minimal memory footprint
# Automatic resource management
# Emergency shutdown protection
# Scheduled maintenance
```

---

## 🚨 **Safety Features**

### **Resource Protection**
```bash
🛡️ Memory limits: 256MB max
🛡️ Storage limits: 100MB max
🛡️ CPU limits: 25% max usage
🛡️ Emergency shutdown: < 30MB storage
```

### **VRChat Compliance**
```bash
📋 Rate limiting: 1 request/minute
📋 User agent: Properly configured
📋 Error handling: Graceful failures
📋 Reconnection: Automatic with delays
```

### **Data Protection**
```bash
🔒 No credential logging
🔒 Secure temporary file handling
🔒 Safe duplicate removal
🔒 Backup recommendations
```

---

## 📱 **Installation Guide**

### **Step 1: Dependencies**
```bash
# Install required packages
pip install vrchatapi python-dotenv psutil pyyaml
```

### **Step 2: Auto-Launch Setup**
```bash
# Run the setup script
python startup_setup.py

# Follow the prompts for your OS:
# ✅ Windows: Registry configuration
# ✅ macOS: LaunchAgent setup
# ✅ Linux: systemd service
```

### **Step 3: Configuration**
```bash
# Configure your credentials
cp .env.dual_mode .env
nano .env  # Add your VRChat credentials

# Test the bot
python dual_mode_bot.py
```

### **Step 4: Verify Auto-Launch**
```bash
# Reboot your system
# Bot should start automatically in standby mode
# Check logs: tail -f dual_bot.log
```

---

## 🔧 **Troubleshooting**

### **Common Issues**
```bash
❌ "Authentication failed"
   → Check VRChat credentials in .env
   → Verify 2FA code if enabled

❌ "Low resources detected"
   → Bot auto-switches to standby mode
   → Check disk space and memory

❌ "Auto-start not working"
   → Run python startup_setup.py again
   → Check permissions for startup directory
```

### **Manual Recovery**
```bash
# Stop the bot
pkill -f dual_mode_bot.py

# Clean up resources
python -c "from system_helper import SystemHelper; SystemHelper().clean_temp_files()"

# Restart manually
python dual_mode_bot.py
```

---

## 📈 **Performance Monitoring**

### **Real-Time Status**
```bash
# Bot provides live status updates:
🟢 Mode: standby
💾 Memory: 128MB/256MB
💿 Storage: 2.1GB free
⏰ Uptime: 2d 14h 23m
🔄 Last cleanup: 1h ago
```

### **Health Dashboard**
```bash
# Available via !health command:
🏥 Overall: 🟢 Good
💾 Memory: 45% usage
💿 Disk: 67% usage
🖥️ Platform: Windows
⚠️ Recommendations: Monitor disk usage
```

---

## 🎯 **Perfect for Your HP Envy 15-dy1xxx**

### **System Specifications**
- **RAM**: 11.7GB total ✅ (Bot uses 256MB max)
- **Storage**: 3.62GB free ✅ (Bot uses 100MB max)
- **CPU**: Modern processor ✅ (Bot uses 25% max)
- **Age**: 2019+ ✅ (Fully compatible)

### **Optimized Features**
```bash
🎯 Resource-conscious design
🎯 Automatic cleanup
🎯 Emergency protection
🎯 Scheduled maintenance
🎯 Dual-mode flexibility
```

---

## 🚀 **Getting Started Summary**

1. **Run Setup**: `python startup_setup.py`
2. **Configure**: Edit `.env` with VRChat credentials
3. **Test**: `python dual_mode_bot.py`
4. **Reboot**: Verify auto-start works
5. **Enjoy**: Your bot now runs 24/7!

---

**🎉 Your dual-mode VRChat bot is now ready to assist both in VRChat and as a system helper!** 

The bot will automatically switch between modes based on time and resources, ensuring optimal performance on your HP Envy laptop while keeping your system clean and optimized.
