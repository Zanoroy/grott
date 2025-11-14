# MQTT Control for Grott

This guide explains how to use MQTT to read and write SPH inverter registers through Grott.

## Overview

Grott provides two MQTT-based services for interacting with your inverter:

1. **Register Monitoring** (`grott_registers_mqtt.py`) - Automatically reads and publishes register values to MQTT every 5 minutes
2. **Register Control** (`grott_mqtt_control.py`) - Listens for MQTT commands to write register values

## Prerequisites

- Grott and Grottserver running
- MQTT broker configured in `grott.ini`
- Both services installed and running (optional, can run manually)

## Reading Register Values

### Automatic Monitoring

The `grott_registers_mqtt.py` script automatically reads 40+ configuration registers and publishes them to MQTT every 5 minutes.

**Topics published to:**
```
energy/registers                          # Complete JSON with all registers
energy/registers/priority_mode            # Individual register values
energy/registers/export_limit_enabled
energy/registers/export_limit_power
energy/registers/battery_first_time1_start
... (all other registers)
```

**Example JSON payload** (published to `energy/registers`):
```json
{
  "timestamp": "2025-11-14T10:30:00",
  "inverter": "NTCRBLR00Y",
  "registers": {
    "priority_mode": {
      "name": "Priority Mode",
      "value": "Battery First",
      "unit": "",
      "register": 1044
    },
    "export_limit_enabled": {
      "name": "Export Limit Enable",
      "value": "Disabled",
      "unit": "",
      "register": 122
    },
    "export_limit_power": {
      "name": "Export Limit Power",
      "value": "100.0%",
      "unit": "%",
      "register": 123
    }
  }
}
```

**Manual read via HTTP API:**
```bash
# Read a single register (GET request)
curl "http://<server>:5782/inverter?command=register&inverter=<inverter_id>&register=<register_number>&format=dec"

# Example: Read priority mode (register 1044)
curl "http://172.17.254.10:5782/inverter?command=register&inverter=NTCRBLR00Y&register=1044&format=dec"
```

## Writing Register Values

### Via MQTT (Recommended)

The `grott_mqtt_control.py` service listens for MQTT commands and writes register values.

**Command Topic:**
```
energy/control/register/write
```

**Result Topic:**
```
energy/control/register/result
```

**Payload Format:**
```json
{
  "register": <register_number>,
  "value": <value>,
  "inverter": "<inverter_id>"  // Optional, defaults to configured inverter
}
```

### Examples

**Set Battery First Mode (register 1044 = 1):**
```bash
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":1044,"value":1}'
```

**Enable Export Limit (register 122 = 1):**
```bash
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":122,"value":1}'
```

**Set Export Limit to 0% (register 123 = 0):**
```bash
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":123,"value":0}'
```

**Set Battery First Time Schedule (9am start, register 1100):**
```bash
# Time format: (hour × 256) + minute
# 9:00 = (9 × 256) + 0 = 2304
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":1100,"value":2304}'
```

**Response Example:**
```json
{
  "success": true,
  "data": {"value": 1},
  "register": 1044,
  "value": 1,
  "timestamp": "2025-11-14T10:35:00",
  "inverter": "NTCRBLR00Y"
}
```

**Error Response Example:**
```json
{
  "success": false,
  "error": "HTTP 500",
  "register": 9999,
  "timestamp": "2025-11-14T10:35:00",
  "inverter": "NTCRBLR00Y"
}
```

### Via HTTP API (Direct)

You can also write registers directly using the HTTP API:

```bash
# Write a single register (PUT request)
curl -X PUT "http://<server>:5782/inverter?command=register&inverter=<inverter_id>&register=<register_number>&value=<value>"

# Example: Set Battery First mode
curl -X PUT "http://172.17.254.10:5782/inverter?command=register&inverter=NTCRBLR00Y&register=1044&value=1"
```

## Common Register Operations

### Priority Mode (Register 1044)

**Set Load First (0% export priority):**
```bash
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":1044,"value":0}'
```

**Set Battery First:**
```bash
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":1044,"value":1}'
```

**Set Grid First:**
```bash
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":1044,"value":2}'
```

### Export Limit Control

**Disable Grid Export (0% export limit):**
```bash
# Set limit to 0%
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":123,"value":0}'

# Enable the limit
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":122,"value":1}'
```

**Set 50% Export Limit:**
```bash
# Set limit to 50% (value = 500, divide by 10 for percentage)
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":123,"value":500}'

# Enable the limit
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":122,"value":1}'
```

**Disable Export Limit (unlimited export):**
```bash
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":122,"value":0}'
```

### Time Schedule Settings

Time values are encoded as: `(hour × 256) + minute`

**Examples:**
- 00:00 = 0
- 09:00 = 2304
- 13:00 = 3328
- 23:59 = 6143

**Set Battery First Time 1 (9am to 1pm):**
```bash
# Start at 09:00 (register 1100)
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":1100,"value":2304}'

# Stop at 13:00 (register 1101)
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":1101,"value":3328}'

# Enable the schedule (register 1102)
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 \
  -t "energy/control/register/write" \
  -m '{"register":1102,"value":1}'
```

## Installation and Setup

### Manual Execution

**Start register monitoring:**
```bash
cd /opt/grott
python3 grott_registers_mqtt.py
```

**Start MQTT control handler:**
```bash
cd /opt/grott
python3 grott_mqtt_control.py
```

### Systemd Services (Automatic Start)

**Install and enable services:**
```bash
# Copy service files
sudo cp /opt/grott/grott-mqtt-control.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable grott-mqtt-control.service
sudo systemctl start grott-mqtt-control.service

# Check status
sudo systemctl status grott-mqtt-control.service
```

## Home Assistant Integration

### Sensors (Reading Values)

Add to your `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "Inverter Priority Mode"
      state_topic: "energy/registers/priority_mode"
      value_template: "{{ value }}"
      
    - name: "Export Limit Enabled"
      state_topic: "energy/registers/export_limit_enabled"
      value_template: "{{ value }}"
      
    - name: "Export Limit Power"
      state_topic: "energy/registers/export_limit_power"
      value_template: "{{ value }}"
      unit_of_measurement: "%"
```

### Switches and Selects (Writing Values)

**Priority Mode Select:**
```yaml
input_select:
  inverter_priority_mode:
    name: Inverter Priority Mode
    options:
      - Load First
      - Battery First
      - Grid First
    initial: Battery First

automation:
  - alias: "Set Inverter Priority Mode"
    trigger:
      platform: state
      entity_id: input_select.inverter_priority_mode
    action:
      service: mqtt.publish
      data:
        topic: "energy/control/register/write"
        payload_template: >
          {% if trigger.to_state.state == "Load First" %}
            {"register":1044,"value":0}
          {% elif trigger.to_state.state == "Battery First" %}
            {"register":1044,"value":1}
          {% elif trigger.to_state.state == "Grid First" %}
            {"register":1044,"value":2}
          {% endif %}
```

**Export Limit Switch:**
```yaml
input_boolean:
  export_limit_enabled:
    name: Export Limit Enabled
    initial: off

automation:
  - alias: "Toggle Export Limit"
    trigger:
      platform: state
      entity_id: input_boolean.export_limit_enabled
    action:
      service: mqtt.publish
      data:
        topic: "energy/control/register/write"
        payload_template: '{"register":122,"value":{{ 1 if trigger.to_state.state == "on" else 0 }}}'
```

## Register Reference

See [SPH Inverter Register Control](SPH-Inverter-Register-Control.md) for a complete list of available registers.

**Key Registers:**
| Register | Name | Values | Description |
|----------|------|--------|-------------|
| 15 | LCD Language | 0-8 | 0=Italian, 1=English, 2=German, etc. |
| 122 | Export Limit Enable | 0-1 | 0=Disabled, 1=Enabled |
| 123 | Export Limit Power | 0-1000 | Percentage × 10 (0=0%, 1000=100%) |
| 1044 | Priority Mode | 0-2 | 0=Load First, 1=Battery First, 2=Grid First |
| 1060 | UPS Function | 0-1 | 0=Disabled, 1=Enabled |
| 1070 | Grid First Discharge Rate | 0-100 | Percentage |
| 1071 | Grid First Stop SOC | 0-100 | Percentage |
| 1090 | Battery First Charge Rate | 0-100 | Percentage |
| 1091 | Battery First Stop SOC | 0-100 | Percentage |
| 1092 | AC Charge Enable | 0-1 | 0=Disabled, 1=Enabled |
| 1100-1108 | Battery First Time 1-3 | Time | Start/Stop/Enable |
| 1110-1118 | Load First Time 1-3 | Time | Start/Stop/Enable |

## Troubleshooting

**Service not responding:**
```bash
# Check service status
sudo systemctl status grott-mqtt-control.service

# View logs
journalctl -u grott-mqtt-control.service -f

# Restart service
sudo systemctl restart grott-mqtt-control.service
```

**MQTT messages not received:**
```bash
# Test MQTT broker connection
mosquitto_sub -h localhost -p 1883 -u growatt -P energy123 -t "energy/#" -v

# Test publishing
mosquitto_pub -h localhost -p 1883 -u growatt -P energy123 -t "energy/control/register/write" -m '{"register":1044,"value":1}'
```

**Register write fails:**
- Ensure grottserver is running: `systemctl status grottserver.service`
- Verify inverter is online and connected to datalogger
- Check register number is correct for your inverter type
- Some registers are read-only

**Time conversion calculator:**
```python
# Convert time to register value
hour = 9
minute = 0
value = (hour * 256) + minute
print(f"{hour:02d}:{minute:02d} = {value}")  # Output: 09:00 = 2304

# Convert register value to time
value = 2304
hour = (value >> 8) & 0xFF
minute = value & 0xFF
print(f"{value} = {hour:02d}:{minute:02d}")  # Output: 2304 = 09:00
```

## Security Considerations

- MQTT credentials are stored in `grott.ini`
- Consider using MQTT over TLS for production environments
- Restrict MQTT broker access to trusted networks
- Register writes can affect inverter operation - use with caution
- Test commands on non-critical times first

## Advanced Usage

### Batch Operations with Shell Script

```bash
#!/bin/bash
# Set Battery First mode with 9am-1pm charging schedule

MQTT_HOST="localhost"
MQTT_PORT="1883"
MQTT_USER="growatt"
MQTT_PASS="energy123"
TOPIC="energy/control/register/write"

# Set Battery First mode
mosquitto_pub -h $MQTT_HOST -p $MQTT_PORT -u $MQTT_USER -P $MQTT_PASS \
  -t "$TOPIC" -m '{"register":1044,"value":1}'

sleep 1

# Set start time to 09:00 (2304)
mosquitto_pub -h $MQTT_HOST -p $MQTT_PORT -u $MQTT_USER -P $MQTT_PASS \
  -t "$TOPIC" -m '{"register":1100,"value":2304}'

sleep 1

# Set stop time to 13:00 (3328)
mosquitto_pub -h $MQTT_HOST -p $MQTT_PORT -u $MQTT_USER -P $MQTT_PASS \
  -t "$TOPIC" -m '{"register":1101,"value":3328}'

sleep 1

# Enable the schedule
mosquitto_pub -h $MQTT_HOST -p $MQTT_PORT -u $MQTT_USER -P $MQTT_PASS \
  -t "$TOPIC" -m '{"register":1102,"value":1}'

echo "Battery First mode configured for 09:00-13:00"
```

### Node-RED Integration

Import this flow to control your inverter from Node-RED:

```json
[
  {
    "id": "mqtt_write",
    "type": "mqtt out",
    "topic": "energy/control/register/write",
    "broker": "mqtt_broker",
    "name": "Write Register"
  },
  {
    "id": "mqtt_result",
    "type": "mqtt in",
    "topic": "energy/control/register/result",
    "broker": "mqtt_broker",
    "name": "Register Result"
  }
]
```

## See Also

- [SPH Inverter Register Control](SPH-Inverter-Register-Control.md) - Complete register reference
- [Grott Documentation](https://github.com/johanmeijer/grott) - Main Grott project
- [Home Assistant MQTT](https://www.home-assistant.io/integrations/mqtt/) - HA MQTT integration
