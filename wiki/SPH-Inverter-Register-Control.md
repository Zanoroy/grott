# SPH Inverter Register Control via Grott API

This guide explains how to read and write registers on Growatt SPH (Storage SPH Type) inverters using the Grott HTTP API.

## Available Register Ranges for SPH Inverters

**Read (Function Code 03):** 0-124, 1000-1124  
**Write (Function Code 04):** 0-124, 1000-1124, 1125-1249

## Important Registers

### Basic Settings (0-124)
| Register | Name | Description | Access | Values | Unit |
|----------|------|-------------|--------|--------|------|
| 15 | LCD Language | Display language | R/W | 0=Italian, 1=English, 2=German, 3=Spanish, 4=French, 5=Chinese, 6=Polish, 7=Portuguese, 8=Hungarian | - |

### Storage Control (1000-1249)
| Register | Name | Description | Access | Values | Unit |
|----------|------|-------------|--------|--------|------|
| 1044 | Priority Mode | Load/Battery/Grid First | R/W | 0=Load First, 1=Battery First, 2=Grid First | - |
| 1060 | UPS Function | Enable/Disable UPS mode | R/W | 0=Disable, 1=Enable | - |
| 1061 | UPS Voltage | UPS output voltage | R/W | 0=230V, 1=208V, 2=240V | - |
| 1062 | UPS Frequency | UPS output frequency | R/W | 0=50Hz, 1=60Hz | - |
| 1070 | Grid First Discharge Power Rate | Discharge rate in Grid First mode | R/W | 0-100 | % |
| 1071 | Grid First Stop SOC | Stop discharge SOC in Grid First | R/W | 0-100 | % |
| 1090 | Battery First Charge Power Rate | Charge rate in Battery First mode | R/W | 0-100 | % |
| 1091 | Battery First Stop SOC | Stop charge SOC in Battery First | R/W | 0-100 | % |
| 1092 | AC Charge Switch | Enable AC charging in Battery First | R/W | 0=Disable, 1=Enable | - |

### Grid First Time Schedules (1080-1088)
| Register | Name | Description | Access | Format |
|----------|------|-------------|--------|--------|
| 1080 | Grid First Start Time 1 | Time slot 1 start | R/W | HH:MM (hex) |
| 1081 | Grid First Stop Time 1 | Time slot 1 end | R/W | HH:MM (hex) |
| 1082 | Grid First Switch 1 | Time slot 1 enable | R/W | 0=Off, 1=On |
| 1083 | Grid First Start Time 2 | Time slot 2 start | R/W | HH:MM (hex) |
| 1084 | Grid First Stop Time 2 | Time slot 2 end | R/W | HH:MM (hex) |
| 1085 | Grid First Switch 2 | Time slot 2 enable | R/W | 0=Off, 1=On |
| 1086 | Grid First Start Time 3 | Time slot 3 start | R/W | HH:MM (hex) |
| 1087 | Grid First Stop Time 3 | Time slot 3 end | R/W | HH:MM (hex) |
| 1088 | Grid First Switch 3 | Time slot 3 enable | R/W | 0=Off, 1=On |

### Battery First Time Schedules (1100-1108)
| Register | Name | Description | Access | Format |
|----------|------|-------------|--------|--------|
| 1100 | Battery First Start Time 1 | Time slot 1 start | R/W | HH:MM (hex) |
| 1101 | Battery First Stop Time 1 | Time slot 1 end | R/W | HH:MM (hex) |
| 1102 | Battery First Switch 1 | Time slot 1 enable | R/W | 0=Off, 1=On |
| 1103 | Battery First Start Time 2 | Time slot 2 start | R/W | HH:MM (hex) |
| 1104 | Battery First Stop Time 2 | Time slot 2 end | R/W | HH:MM (hex) |
| 1105 | Battery First Switch 2 | Time slot 2 enable | R/W | 0=Off, 1=On |
| 1106 | Battery First Start Time 3 | Time slot 3 start | R/W | HH:MM (hex) |
| 1107 | Battery First Stop Time 3 | Time slot 3 end | R/W | HH:MM (hex) |
| 1108 | Battery First Switch 3 | Time slot 3 enable | R/W | 0=Off, 1=On |

### Load First Time Schedules (1110-1118)
| Register | Name | Description | Access | Format |
|----------|------|-------------|--------|--------|
| 1110 | Load First Start Time 1 | Time slot 1 start | R/W | HH:MM (hex) |
| 1111 | Load First Stop Time 1 | Time slot 1 end | R/W | HH:MM (hex) |
| 1112 | Load First Switch 1 | Time slot 1 enable | R/W | 0=Off, 1=On |
| 1113 | Load First Start Time 2 | Time slot 2 start | R/W | HH:MM (hex) |
| 1114 | Load First Stop Time 2 | Time slot 2 end | R/W | HH:MM (hex) |
| 1115 | Load First Switch 2 | Time slot 2 enable | R/W | 0=Off, 1=On |
| 1116 | Load First Start Time 3 | Time slot 3 start | R/W | HH:MM (hex) |
| 1117 | Load First Stop Time 3 | Time slot 3 end | R/W | HH:MM (hex) |
| 1118 | Load First Switch 3 | Time slot 3 enable | R/W | 0=Off, 1=On |

## API Endpoints

The Grott HTTP server (default port 5782) provides REST API endpoints for register access.

### Reading Registers

**Single Register (GET):**
```
http://<server>:5782/inverter?command=register&inverter=<INVERTER_ID>&register=<REG_NUM>&format=<FORMAT>
```

**Parameters:**
- `command=register` - Read a single register
- `inverter=<INVERTER_ID>` - Your inverter serial number (e.g., NTCRBLR00Y)
- `register=<REG_NUM>` - Register number (0-4095)
- `format=<FORMAT>` - Response format: `dec` (decimal), `hex` (hexadecimal), or `text` (ASCII text)

**Examples:**
```bash
# Read priority mode (decimal)
curl "http://172.17.254.10:5782/inverter?command=register&inverter=NTCRBLR00Y&register=1044&format=dec"
# Returns: {"value": 0}  (0=Load First, 1=Battery First, 2=Grid First)

# Read battery first start time 1 (hex)
curl "http://172.17.254.10:5782/inverter?command=register&inverter=NTCRBLR00Y&register=1100&format=hex"
# Returns: {"value": "0900"}  (09:00 AM)

# Read battery first switch 1 (decimal)
curl "http://172.17.254.10:5782/inverter?command=register&inverter=NTCRBLR00Y&register=1102&format=dec"
# Returns: {"value": 1}  (1=Enabled, 0=Disabled)
```

### Writing Registers

#### Single Register (PUT)

**Syntax:**
```
curl -X PUT "http://<server>:5782/inverter?command=register&inverter=<INVERTER_ID>&register=<REG_NUM>&value=<VALUE>"
```

**Parameters:**
- `command=register` - Write a single register
- `inverter=<INVERTER_ID>` - Your inverter serial number
- `register=<REG_NUM>` - Register number to write
- `value=<VALUE>` - Decimal value to write

**Examples:**
```bash
# Set priority mode to Battery First (value=1)
curl -X PUT "http://172.17.254.10:5782/inverter?command=register&inverter=NTCRBLR00Y&register=1044&value=1"

# Enable battery first time slot 1
curl -X PUT "http://172.17.254.10:5782/inverter?command=register&inverter=NTCRBLR00Y&register=1102&value=1"

# Set battery first start time to 9:00 AM (0x0900 = 2304 decimal)
curl -X PUT "http://172.17.254.10:5782/inverter?command=register&inverter=NTCRBLR00Y&register=1100&value=2304"

# Set battery first stop time to 17:00 (0x1100 = 4352 decimal)
curl -X PUT "http://172.17.254.10:5782/inverter?command=register&inverter=NTCRBLR00Y&register=1101&value=4352"
```

#### Multiple Registers (PUT)

**Syntax:**
```
curl -X PUT "http://<server>:5782/inverter?command=multiregister&inverter=<INVERTER_ID>&startregister=<START>&endregister=<END>&value=<HEX_VALUE>"
```

**Parameters:**
- `command=multiregister` - Write multiple consecutive registers
- `inverter=<INVERTER_ID>` - Your inverter serial number
- `startregister=<START>` - First register number
- `endregister=<END>` - Last register number
- `value=<HEX_VALUE>` - Concatenated hex values (4 hex digits per register)

**Example - Set Battery First Time Slot 1:**
```bash
# Set registers 1100-1102 (start time, stop time, enable switch)
# 1100: 09:00 = 0x0900
# 1101: 17:00 = 0x1100  
# 1102: Enable = 0x0001
curl -X PUT "http://172.17.254.10:5782/inverter?command=multiregister&inverter=NTCRBLR00Y&startregister=1100&endregister=1102&value=090011000001"
```

**Example - Set all 3 Battery First Time Slots:**
```bash
# Set registers 1100-1108 (all 3 time slots)
# Slot 1: 09:00-17:00 Enabled (0x0900 0x1100 0x0001)
# Slot 2: 00:00-00:00 Disabled (0x0000 0x0000 0x0000)
# Slot 3: 00:00-00:00 Disabled (0x0000 0x0000 0x0000)
curl -X PUT "http://172.17.254.10:5782/inverter?command=multiregister&inverter=NTCRBLR00Y&startregister=1100&endregister=1108&value=090011000001000000000000000000000000"
```

## Time Value Conversion

Time values are stored as 16-bit integers with the format:
- **High byte (bits 15-8):** Hour (0-23)
- **Low byte (bits 7-0):** Minute (0-59)

### Converting Time to Hex/Decimal

**Formula:** `value = (hour × 256) + minute`

**Common Time Conversions:**

| Time | Hex Value | Decimal Value | Calculation |
|------|-----------|---------------|-------------|
| 00:00 | 0x0000 | 0 | (0 × 256) + 0 |
| 06:00 | 0x0600 | 1536 | (6 × 256) + 0 |
| 06:30 | 0x061e | 1566 | (6 × 256) + 30 |
| 09:00 | 0x0900 | 2304 | (9 × 256) + 0 |
| 10:00 | 0x0a00 | 2560 | (10 × 256) + 0 |
| 12:00 | 0x0c00 | 3072 | (12 × 256) + 0 |
| 13:00 | 0x0d00 | 3328 | (13 × 256) + 0 |
| 14:30 | 0x0e1e | 3614 | (14 × 256) + 30 |
| 17:00 | 0x1100 | 4352 | (17 × 256) + 0 |
| 22:00 | 0x1600 | 5632 | (22 × 256) + 0 |
| 23:59 | 0x173b | 5947 | (23 × 256) + 59 |

### Converting Hex Response to Time

When reading time registers with `format=hex`, convert back to time:

**Example:** Response `{"value": "0e1e"}`
- High byte: `0e` = 14 (hour)
- Low byte: `1e` = 30 (minute)
- **Time: 14:30** (2:30 PM)

**Python conversion:**
```python
hex_value = "0e1e"
int_value = int(hex_value, 16)
hour = int_value >> 8        # High byte
minute = int_value & 0xFF    # Low byte
print(f"{hour:02d}:{minute:02d}")  # Output: 14:30
```

**Bash conversion:**
```bash
# Read and convert
hex_value=$(curl -s "http://172.17.254.10:5782/inverter?command=register&inverter=NTCRBLR00Y&register=1100&format=hex" | jq -r '.value')
dec_value=$((16#$hex_value))
hour=$((dec_value / 256))
minute=$((dec_value % 256))
echo "Time: $(printf '%02d:%02d' $hour $minute)"
```

## Complete Examples

### Example 1: Configure Battery First Mode with Time Schedule

```bash
INVERTER="NTCRBLR00Y"
SERVER="http://172.17.254.10:5782"

# Step 1: Set priority mode to Battery First
curl -X PUT "$SERVER/inverter?command=register&inverter=$INVERTER&register=1044&value=1"

# Step 2: Set Battery First time slot 1 (09:00-17:00, enabled)
curl -X PUT "$SERVER/inverter?command=multiregister&inverter=$INVERTER&startregister=1100&endregister=1102&value=090011000001"

# Step 3: Set charge power rate to 50%
curl -X PUT "$SERVER/inverter?command=register&inverter=$INVERTER&register=1090&value=50"

# Step 4: Set stop SOC to 100%
curl -X PUT "$SERVER/inverter?command=register&inverter=$INVERTER&register=1091&value=100"

# Step 5: Enable AC charging
curl -X PUT "$SERVER/inverter?command=register&inverter=$INVERTER&register=1092&value=1"
```

### Example 2: Read All Battery First Settings

```bash
INVERTER="NTCRBLR00Y"
SERVER="http://172.17.254.10:5782"

echo "Priority Mode:"
curl -s "$SERVER/inverter?command=register&inverter=$INVERTER&register=1044&format=dec"

echo -e "\nBattery First Time Slot 1:"
echo -n "Start: "
curl -s "$SERVER/inverter?command=register&inverter=$INVERTER&register=1100&format=hex"
echo -n "Stop: "
curl -s "$SERVER/inverter?command=register&inverter=$INVERTER&register=1101&format=hex"
echo -n "Enabled: "
curl -s "$SERVER/inverter?command=register&inverter=$INVERTER&register=1102&format=dec"

echo -e "\nCharge Power Rate:"
curl -s "$SERVER/inverter?command=register&inverter=$INVERTER&register=1090&format=dec"

echo -e "\nStop SOC:"
curl -s "$SERVER/inverter?command=register&inverter=$INVERTER&register=1091&format=dec"
```

### Example 3: Set Multiple Time Schedules at Once

```bash
# Configure all 3 Load First time slots:
# Slot 1: 00:00-06:00 Enabled
# Slot 2: 16:00-22:00 Enabled  
# Slot 3: Disabled

# Calculate hex values:
# Slot 1: 0x0000 (00:00), 0x0600 (06:00), 0x0001 (enabled)
# Slot 2: 0x1000 (16:00), 0x1600 (22:00), 0x0001 (enabled)
# Slot 3: 0x0000, 0x0000, 0x0000 (disabled)

curl -X PUT "http://172.17.254.10:5782/inverter?command=multiregister&inverter=NTCRBLR00Y&startregister=1110&endregister=1118&value=000006000001100016000001000000000000"
```

## Important Notes

1. **Communication Timing:** The inverter must be actively communicating with the Grott server for write commands to work. Reads/writes may timeout if the datalogger isn't sending data.

2. **Response Times:** After sending a write command, wait a few seconds before reading the register back to verify the change.

3. **Mode Changes:** When changing between Load First/Battery First/Grid First modes, ensure the corresponding time schedules are properly configured.

4. **Register Persistence:** Register changes are typically saved to the inverter's non-volatile memory and persist after power cycles.

5. **Safety:** Always verify critical settings (like SOC limits and charge rates) after making changes. Incorrect settings could damage your battery.

## Troubleshooting

**"no or invalid response received"**
- The datalogger isn't currently connected or communication timeout occurred
- Wait for the next data transmission from the inverter and try again
- Check that your inverter ID is correct using the `/inverters` endpoint

**"register parameter is required"**
- Make sure to include the `&register=<NUM>` parameter for single register reads

**Empty response "{}"**
- The register hasn't been queried yet or the cache is empty
- Try a fresh read request

**Connection reset**
- Missing required parameters or server error
- Check all parameters are properly URL encoded
- Verify the server is running: `curl http://<server>:5782/info`

## Getting Your Inverter ID

```bash
# List all connected inverters
curl "http://172.17.254.10:5782/inverters"
```

Returns:
```json
{
  "count": 1,
  "inverters": [
    {
      "inverter_id": "NTCRBLR00Y",
      "datalogger_id": "NAC5A480NL",
      "inverterno": "50",
      "power": 0
    }
  ]
}
```

## Additional Resources

- [Grott Documentation](https://github.com/johanmeijer/grott)
- [Register Documentation](../documentatie/registers.md)
- Growatt-Inverter-Modbus-RTU-Protocol-II-V1-24-English.pdf (for complete register list)

## Disclaimer

Modifying inverter registers can affect your system's operation and potentially void your warranty. Use at your own risk. Always test changes carefully and monitor your system closely after making modifications.
