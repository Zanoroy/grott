# Welcome to Grott - The Growatt Inverter Monitor

Grott allows you to intercept, parse, and forward metrics from your Growatt inverter without relying on Growatt's cloud servers.

## 📚 Documentation

- **[Statement of Use and Limitations](https://github.com/johanmeijer/grott/wiki/@Statement-of-use-and-limitations)** - Important disclaimer and usage terms
- **[First Time Installation Guide](https://github.com/johanmeijer/grott/wiki/@-First-time-installation)** - Quick start guide for new users
- **[Grottserver](https://github.com/johanmeijer/grott/wiki/Grottserver)** - Emulate Growatt servers locally (no internet connection needed)
- **[SPH Inverter Register Control](SPH-Inverter-Register-Control.md)** - Control SPH inverter settings

## 🚀 Quick Start

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/johanmeijer/grott.git

# Navigate to the grott directory
cd grott
```

### 2. Configure Grott

Edit the `grott.ini` configuration file to match your setup:

```bash
nano grott.ini
```

Key settings to review:
- **MQTT settings** - Configure your MQTT broker details
- **Mode settings** - Choose proxy or sniff mode
- **Output settings** - Enable InfluxDB, PVOutput, etc. as needed

### 3. Install as a Linux Service

#### Option A: Using Grott Only (No Local Server)

If you want to forward data to Growatt's cloud servers (proxy mode), use only the `grott.service`:

1. **Edit the service file** to remove server dependency:
   ```bash
   nano grott.service
   ```
   
   Comment out or remove these lines:
   ```ini
   #After=grottserver.service
   #Requires=grottserver.service
   ```

2. **Copy the service file:**
   ```bash
   sudo cp grott.service /etc/systemd/system/
   ```

3. **Reload systemd, enable and start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable grott.service
   sudo systemctl start grott.service
   ```

4. **Check the service status:**
   ```bash
   sudo systemctl status grott.service
   ```

#### Option B: Using Grott with Grottserver (Local Server)

If you want to run Grottserver locally (emulating Growatt servers), you need both services:

1. **Install Grottserver service first:**
   ```bash
   sudo cp grottserver.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable grottserver.service
   sudo systemctl start grottserver.service
   ```

2. **Verify Grottserver is running:**
   ```bash
   sudo systemctl status grottserver.service
   ```

3. **Install Grott service** (which depends on Grottserver):
   ```bash
   sudo cp grott.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable grott.service
   sudo systemctl start grott.service
   ```

4. **Check both services:**
   ```bash
   sudo systemctl status grott.service
   sudo systemctl status grottserver.service
   ```

### 4. Configure Your ShineWIFI/ShineLAN

Configure your inverter's WiFi or LAN module to send data to your Grott server instead of Growatt's servers. See the [Wiki](https://github.com/johanmeijer/grott/wiki/Rerouting-Growatt-Wifi-TCPIP-data-via-your-Grott-Server) for detailed instructions.

## 📋 Service Management Commands

```bash
# View service logs
sudo journalctl -u grott.service -f
sudo journalctl -u grottserver.service -f

# Restart a service
sudo systemctl restart grott.service
sudo systemctl restart grottserver.service

# Stop a service
sudo systemctl stop grott.service
sudo systemctl stop grottserver.service

# Disable a service from starting on boot
sudo systemctl disable grott.service
sudo systemctl disable grottserver.service
```

## 🔧 Service File Customization

### Working Directory
By default, the service files use `/opt/grott/` as the working directory. If you cloned Grott to a different location, update this line in both service files:

```ini
WorkingDirectory=/your/custom/path/
ExecStart=-/usr/bin/python3 -u /your/custom/path/grott.py -v
```

### User Permissions
The services run as `root` by default. For better security, you can create a dedicated user:

```bash
sudo useradd -r -s /bin/false grott
```

Then update the service files:
```ini
User=grott
```

## 🐳 Alternative: Docker Installation

Grott also supports Docker. See the [Docker Support Wiki](https://github.com/johanmeijer/grott/wiki/Docker-support) for details.

```bash
cd docker
docker-compose up -d
```

## 🆘 Troubleshooting

### Service won't start
- Check logs: `sudo journalctl -u grott.service -n 50`
- Verify Python path: `which python3`
- Check file permissions: `ls -l /opt/grott/grott.py`

### No data received
- Verify ShineWIFI/ShineLAN is configured to send data to Grott
- Check firewall settings (ports 5279 for Grott, 5280 for Grottserver)
- Review `grott.ini` settings

### Dependencies between services
If Grott starts before Grottserver is ready:
- Verify the `After=grottserver.service` and `Requires=grottserver.service` lines are present in `grott.service`
- Run `sudo systemctl daemon-reload` after any service file changes

## 💡 Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/johanmeijer/grott/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/johanmeijer/grott/discussions)
- **Wiki**: [Browse all documentation](https://github.com/johanmeijer/grott/wiki)

## 💰 Support the Project

If you find Grott useful, consider supporting the developer:

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate?business=RQFS46F9JTESQ&item_name=Grott+&currency_code=EUR)

---

**Version**: 2.8.3+ | **License**: See repository | **Maintainer**: johanmeijer
