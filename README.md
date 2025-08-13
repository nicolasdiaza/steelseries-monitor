# 🎮 Arctic Monitor

**Real-time system monitoring for SteelSeries OLED displays**

![Arctic Monitor](https://img.shields.io/badge/Arctic-Monitor-blue) ![Python](https://img.shields.io/badge/Python-3.7+-green) ![SteelSeries](https://img.shields.io/badge/SteelSeries-GameSense-orange) ![Windows](https://img.shields.io/badge/Windows-10/11-blue)

A lightweight system monitor that displays **CPU, GPU, RAM, and disk information** directly on your **SteelSeries Arctic Nova Pro Wireless** OLED screen using the GameSense SDK.

## ✨ Features

- 🖥️ **Real-time monitoring**: CPU usage, temperature, GPU stats, RAM usage
- 💾 **Disk information**: Storage usage and free space
- ⌨️ **Global hotkeys**: Control without leaving your game
- 🎮 **GameSense integration**: Native SteelSeries OLED support
- 🔄 **Dual modes**: Hardware stats + Disk info
- ⚡ **Low resource usage**: Minimal system impact
- 🎯 **Plug & play**: Single executable, no installation needed

## 🎯 Controls

| Hotkey | Action |
|--------|---------|
| `Ctrl + F9` | Toggle monitor ON/OFF (instant) |
| `F10` (hold 3s) | Switch between Hardware/Disk mode |

## 📋 Requirements

### Hardware
- **SteelSeries Arctic Nova Pro Wireless** headset
- **Windows 10/11** PC

### Software  
- **SteelSeries GG** (Engine) - must be running
- **LibreHardwareMonitor** - running as Administrator
- **Administrator privileges** - for hardware access

## 🚀 Quick Start

### Option 1: Download Executable (Recommended)
1. Go to [Releases](../../releases)
2. Download `Arctic-Monitor.exe`
3. **Right-click** → **Run as Administrator**
4. Monitor starts automatically!

### Option 2: Build from Source
```bash
git clone https://github.com/YOUR-USERNAME/arctic-monitor.git
cd arctic-monitor
pip install -r requirements.txt
python main.py
```

## 🛠️ Building

To create your own executable:

```bash
# Install dependencies
pip install -r requirements.txt

# Build executable  
build.bat
```

The executable will be created in `dist/Arctic-Monitor.exe`

## 📊 Display Modes

### 🔧 Hardware Mode (updates every 2s)
```
CPU ⇾ 45%🌡65°C
GPU ⇾ 78%🌡72°C  
RAM ⇾ 12.3/32GB
```

### 💽 Disk Mode (updates every 5s)
```
DISK C: 67%
Used: 250GB
Free: 125GB
```

## 🔧 Setup Requirements

### 1. SteelSeries GG
- Download from [SteelSeries website](https://steelseries.com/gg)
- Must be **running** for OLED communication

### 2. LibreHardwareMonitor  
- Download from [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor)
- **Run as Administrator** for temperature sensors
- Keep running in background

### 3. Arctic Nova Pro Wireless
- Connect via **2.4GHz dongle** or **Bluetooth**
- Verify OLED is working in SteelSeries GG

## 🎮 Usage

1. **Start prerequisites**: SteelSeries GG + LibreHardwareMonitor (as Admin)
2. **Run Arctic Monitor** as Administrator
3. **Check OLED**: System info should appear on headset display
4. **Use hotkeys**:
   - `Ctrl+F9` to toggle ON/OFF
   - `F10` (hold 3s) to switch modes

## 🐛 Troubleshooting

### ❌ "No display on OLED"
- ✅ Verify SteelSeries GG is running
- ✅ Check Arctic Nova Pro is connected
- ✅ Run Arctic Monitor as Administrator

### ❌ "Temperature shows 0°C"
- ✅ Run LibreHardwareMonitor as Administrator
- ✅ Check LHM detects your CPU/GPU sensors
- ✅ Some systems may not support temperature monitoring

### ❌ "Hotkeys not working"
- ✅ Run as Administrator
- ✅ Check no other apps are using same hotkeys
- ✅ Install: `pip install keyboard`

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the project
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SteelSeries** for GameSense SDK
- **LibreHardwareMonitor** team for hardware monitoring
- **Community contributors** and testers

## 📞 Support

Having issues?

1. Check [Troubleshooting](#-troubleshooting) section
2. Verify all [Requirements](#-requirements) are met
3. Check [Issues](../../issues) for similar problems
4. Create new issue with detailed information

---

⭐ **Star this repo if Arctic Monitor helps you!**

Made with ❤️ for the SteelSeries Arctic community