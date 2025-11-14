#!/usr/bin/env python3
"""
Grott SPH Inverter Register to MQTT Publisher
Reads inverter configuration registers and publishes them to MQTT
Uses Grott's existing configuration and MQTT setup
"""

import requests
import json
import time
import sys
from datetime import datetime
import paho.mqtt.publish as publish

# Import Grott configuration
sys.path.insert(0, '/opt/grott')
from grottconf import Conf

# Configuration - Update these values
GROTTSERVER_URL = "http://172.17.254.10:5782"
INVERTER_ID = "NTCRBLR00Y"
MQTT_TOPIC_SUFFIX = "registers"  # Will be appended to grott's mqtt topic
POLL_INTERVAL = 300  # Seconds between updates (5 minutes)

# Register definitions
REGISTERS = {
    # Priority Mode
    "priority_mode": {
        "register": 1044,
        "name": "Priority Mode",
        "format": "dec",
        "decode": lambda v: {0: "Load First", 1: "Battery First", 2: "Grid First"}.get(v, f"Unknown({v})")
    },
    
    # Grid First Settings
    "grid_first_discharge_power_rate": {
        "register": 1070,
        "name": "Grid First Discharge Power Rate",
        "format": "dec",
        "unit": "%"
    },
    "grid_first_stop_soc": {
        "register": 1071,
        "name": "Grid First Stop SOC",
        "format": "dec",
        "unit": "%"
    },
    
    # Grid First Time Schedules
    "grid_first_time1_start": {
        "register": 1080,
        "name": "Grid First Time 1 Start",
        "format": "hex",
        "decode": "time"
    },
    "grid_first_time1_stop": {
        "register": 1081,
        "name": "Grid First Time 1 Stop",
        "format": "hex",
        "decode": "time"
    },
    "grid_first_time1_enabled": {
        "register": 1082,
        "name": "Grid First Time 1 Enabled",
        "format": "dec",
        "decode": lambda v: "On" if v == 1 else "Off"
    },
    "grid_first_time2_start": {
        "register": 1083,
        "name": "Grid First Time 2 Start",
        "format": "hex",
        "decode": "time"
    },
    "grid_first_time2_stop": {
        "register": 1084,
        "name": "Grid First Time 2 Stop",
        "format": "hex",
        "decode": "time"
    },
    "grid_first_time2_enabled": {
        "register": 1085,
        "name": "Grid First Time 2 Enabled",
        "format": "dec",
        "decode": lambda v: "On" if v == 1 else "Off"
    },
    "grid_first_time3_start": {
        "register": 1086,
        "name": "Grid First Time 3 Start",
        "format": "hex",
        "decode": "time"
    },
    "grid_first_time3_stop": {
        "register": 1087,
        "name": "Grid First Time 3 Stop",
        "format": "hex",
        "decode": "time"
    },
    "grid_first_time3_enabled": {
        "register": 1088,
        "name": "Grid First Time 3 Enabled",
        "format": "dec",
        "decode": lambda v: "On" if v == 1 else "Off"
    },
    
    # Battery First Settings
    "battery_first_charge_power_rate": {
        "register": 1090,
        "name": "Battery First Charge Power Rate",
        "format": "dec",
        "unit": "%"
    },
    "battery_first_stop_soc": {
        "register": 1091,
        "name": "Battery First Stop SOC",
        "format": "dec",
        "unit": "%"
    },
    "battery_first_ac_charge": {
        "register": 1092,
        "name": "Battery First AC Charge",
        "format": "dec",
        "decode": lambda v: "Enabled" if v == 1 else "Disabled"
    },
    
    # Battery First Time Schedules
    "battery_first_time1_start": {
        "register": 1100,
        "name": "Battery First Time 1 Start",
        "format": "hex",
        "decode": "time"
    },
    "battery_first_time1_stop": {
        "register": 1101,
        "name": "Battery First Time 1 Stop",
        "format": "hex",
        "decode": "time"
    },
    "battery_first_time1_enabled": {
        "register": 1102,
        "name": "Battery First Time 1 Enabled",
        "format": "dec",
        "decode": lambda v: "On" if v == 1 else "Off"
    },
    "battery_first_time2_start": {
        "register": 1103,
        "name": "Battery First Time 2 Start",
        "format": "hex",
        "decode": "time"
    },
    "battery_first_time2_stop": {
        "register": 1104,
        "name": "Battery First Time 2 Stop",
        "format": "hex",
        "decode": "time"
    },
    "battery_first_time2_enabled": {
        "register": 1105,
        "name": "Battery First Time 2 Enabled",
        "format": "dec",
        "decode": lambda v: "On" if v == 1 else "Off"
    },
    "battery_first_time3_start": {
        "register": 1106,
        "name": "Battery First Time 3 Start",
        "format": "hex",
        "decode": "time"
    },
    "battery_first_time3_stop": {
        "register": 1107,
        "name": "Battery First Time 3 Stop",
        "format": "hex",
        "decode": "time"
    },
    "battery_first_time3_enabled": {
        "register": 1108,
        "name": "Battery First Time 3 Enabled",
        "format": "dec",
        "decode": lambda v: "On" if v == 1 else "Off"
    },
    
    # Load First Settings
    "load_first_stop_soc": {
        "register": 1109,
        "name": "Load First Discharge Stop SOC",
        "format": "dec",
        "unit": "%",
        "note": "Unofficial - may not work on all inverters"
    },
    
    # Load First Time Schedules
    "load_first_time1_start": {
        "register": 1110,
        "name": "Load First Time 1 Start",
        "format": "hex",
        "decode": "time"
    },
    "load_first_time1_stop": {
        "register": 1111,
        "name": "Load First Time 1 Stop",
        "format": "hex",
        "decode": "time"
    },
    "load_first_time1_enabled": {
        "register": 1112,
        "name": "Load First Time 1 Enabled",
        "format": "dec",
        "decode": lambda v: "On" if v == 1 else "Off"
    },
    "load_first_time2_start": {
        "register": 1113,
        "name": "Load First Time 2 Start",
        "format": "hex",
        "decode": "time"
    },
    "load_first_time2_stop": {
        "register": 1114,
        "name": "Load First Time 2 Stop",
        "format": "hex",
        "decode": "time"
    },
    "load_first_time2_enabled": {
        "register": 1115,
        "name": "Load First Time 2 Enabled",
        "format": "dec",
        "decode": lambda v: "On" if v == 1 else "Off"
    },
    "load_first_time3_start": {
        "register": 1116,
        "name": "Load First Time 3 Start",
        "format": "hex",
        "decode": "time"
    },
    "load_first_time3_stop": {
        "register": 1117,
        "name": "Load First Time 3 Stop",
        "format": "hex",
        "decode": "time"
    },
    "load_first_time3_enabled": {
        "register": 1118,
        "name": "Load First Time 3 Enabled",
        "format": "dec",
        "decode": lambda v: "On" if v == 1 else "Off"
    },
    
    # UPS Settings
    "ups_function": {
        "register": 1060,
        "name": "UPS Function",
        "format": "dec",
        "decode": lambda v: "Enabled" if v == 1 else "Disabled"
    },
    "ups_voltage": {
        "register": 1061,
        "name": "UPS Voltage",
        "format": "dec",
        "decode": lambda v: {0: "230V", 1: "208V", 2: "240V"}.get(v, f"Unknown({v})")
    },
    "ups_frequency": {
        "register": 1062,
        "name": "UPS Frequency",
        "format": "dec",
        "decode": lambda v: "50Hz" if v == 0 else "60Hz" if v == 1 else f"Unknown({v})"
    },
    
    # Language
    "lcd_language": {
        "register": 15,
        "name": "LCD Language",
        "format": "dec",
        "decode": lambda v: {0: "Italian", 1: "English", 2: "German", 3: "Spanish", 
                            4: "French", 5: "Chinese", 6: "Polish", 7: "Portuguese", 
                            8: "Hungarian"}.get(v, f"Unknown({v})")
    },
    
    # Export Limit Control
    "export_limit_enabled": {
        "register": 122,
        "name": "Export Limit Enable",
        "format": "dec",
        "decode": lambda v: "Enabled" if v == 1 else "Disabled"
    },
    "export_limit_power": {
        "register": 123,
        "name": "Export Limit Power",
        "format": "dec",
        "unit": "%",
        "decode": lambda v: f"{v/10:.1f}%" if v > 0 else "0%"
    },
    
    # NOTE: The following registers are not yet identified in the documentation
    # You may need to find these register numbers from Growatt documentation
    # or by experimenting with your inverter
    #
    # "inverter_on_off": {
    #     "register": UNKNOWN,
    #     "name": "Inverter On/Off",
    #     "format": "dec"
    # },
    # "off_grid_enable": {
    #     "register": UNKNOWN,
    #     "name": "Off-Grid Enable",
    #     "format": "dec"
    # },
    # "winter_mode": {
    #     "register": UNKNOWN,
    #     "name": "Winter Mode",
    #     "format": "dec"
    # },
}


def decode_time(hex_value):
    """Convert hex time value to HH:MM format"""
    try:
        if isinstance(hex_value, str):
            int_value = int(hex_value, 16)
        else:
            int_value = hex_value
        hour = (int_value >> 8) & 0xFF
        minute = int_value & 0xFF
        return f"{hour:02d}:{minute:02d}"
    except:
        return "Invalid"


def read_register(register, format_type="dec"):
    """Read a single register from the inverter"""
    url = f"{GROTTSERVER_URL}/inverter"
    params = {
        "command": "register",
        "inverter": INVERTER_ID,
        "register": register,
        "format": format_type
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("value")
        else:
            print(f"ERROR: Failed to read register {register}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"ERROR: Failed to read register {register}: {e}")
        return None


def read_all_registers():
    """Read all defined registers and return as dictionary"""
    results = {}
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Reading registers from inverter {INVERTER_ID}...")
    
    for key, config in REGISTERS.items():
        register = config["register"]
        format_type = config.get("format", "dec")
        
        # Read the register
        raw_value = read_register(register, format_type)
        
        if raw_value is not None:
            # Decode the value if decoder is specified
            if "decode" in config:
                if config["decode"] == "time":
                    decoded_value = decode_time(raw_value)
                elif callable(config["decode"]):
                    try:
                        if format_type == "hex":
                            decoded_value = config["decode"](int(raw_value, 16))
                        else:
                            decoded_value = config["decode"](raw_value)
                    except:
                        decoded_value = raw_value
                else:
                    decoded_value = raw_value
            else:
                decoded_value = raw_value
            
            # Store both raw and decoded values
            results[key] = {
                "name": config["name"],
                "register": register,
                "raw_value": raw_value,
                "value": decoded_value,
                "unit": config.get("unit", "")
            }
            
            print(f"  {config['name']:40s} (R{register:04d}): {decoded_value} {config.get('unit', '')}")
        else:
            print(f"  {config['name']:40s} (R{register:04d}): FAILED TO READ")
            results[key] = {
                "name": config["name"],
                "register": register,
                "raw_value": None,
                "value": None,
                "error": "Failed to read"
            }
        
        # Small delay to avoid overwhelming the inverter
        time.sleep(0.1)
    
    return results


def publish_to_mqtt(conf, data):
    """Publish register data to MQTT using Grott's MQTT configuration"""
    
    # Build MQTT topic (same pattern as Grott)
    if conf.mqttinverterintopic:
        mqtttopic = f"{conf.mqtttopic}/{INVERTER_ID}/{MQTT_TOPIC_SUFFIX}"
    else:
        mqtttopic = f"{conf.mqtttopic}/{MQTT_TOPIC_SUFFIX}"
    
    # Prepare complete JSON payload
    payload = {
        "timestamp": datetime.now().isoformat(),
        "inverter": INVERTER_ID,
        "registers": {}
    }
    
    for key, value in data.items():
        payload["registers"][key] = {
            "name": value["name"],
            "value": value["value"],
            "unit": value.get("unit", ""),
            "register": value["register"]
        }
    
    jsonmsg = json.dumps(payload)
    
    # Publish using Grott's method
    try:
        publish.single(
            mqtttopic, 
            payload=jsonmsg, 
            qos=0, 
            retain=conf.mqttretain, 
            hostname=conf.mqttip,
            port=conf.mqttport, 
            client_id=conf.inverterid, 
            keepalive=60, 
            auth=conf.pubauth
        )
        print(f"\nPublished complete register set to {mqtttopic}")
        
        # Also publish individual values for easier access
        for key, value in data.items():
            if value["value"] is not None:
                topic = f"{mqtttopic}/{key}"
                try:
                    publish.single(
                        topic, 
                        payload=str(value["value"]), 
                        qos=0, 
                        retain=conf.mqttretain, 
                        hostname=conf.mqttip,
                        port=conf.mqttport, 
                        client_id=conf.inverterid, 
                        keepalive=60, 
                        auth=conf.pubauth
                    )
                except:
                    pass  # Continue even if individual publish fails
                    
    except TimeoutError:
        print(f"ERROR: MQTT connection timeout")
    except ConnectionRefusedError:
        print(f"ERROR: MQTT connection refused by broker")
    except Exception as error:
        print(f"ERROR: MQTT publish failed: {error}")


def main():
    """Main loop"""
    print("="*80)
    print("Grott SPH Inverter Register to MQTT Publisher")
    print("="*80)
    
    # Load Grott configuration
    print("Loading Grott configuration from grott.ini...")
    try:
        conf = Conf("2.8.3")  # Version number
        print(f"Grottserver: {GROTTSERVER_URL}")
        print(f"Inverter ID: {INVERTER_ID}")
        print(f"MQTT Broker: {conf.mqttip}:{conf.mqttport}")
        print(f"MQTT Topic:  {conf.mqtttopic}/{MQTT_TOPIC_SUFFIX}")
        print(f"MQTT Auth:   {'Enabled' if conf.mqttauth else 'Disabled'}")
        print(f"MQTT Retain: {'Enabled' if conf.mqttretain else 'Disabled'}")
        print(f"Poll Interval: {POLL_INTERVAL} seconds")
        print("="*80)
    except Exception as e:
        print(f"ERROR: Failed to load Grott configuration: {e}")
        print("Make sure grott.ini is in the current directory or /opt/grott/")
        sys.exit(1)
    
    # Check if MQTT is disabled
    if conf.nomqtt:
        print("ERROR: MQTT is disabled in grott.ini")
        print("Please enable MQTT in the configuration file")
        sys.exit(1)
    
    try:
        while True:
            # Read all registers
            register_data = read_all_registers()
            
            # Publish to MQTT
            publish_to_mqtt(conf, register_data)
            
            # Wait before next poll
            print(f"\nWaiting {POLL_INTERVAL} seconds until next poll...")
            print("Press Ctrl+C to exit\n")
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
