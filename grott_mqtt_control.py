#!/usr/bin/env python3
"""
Grott MQTT Control Handler
Subscribes to MQTT commands to write inverter registers
Publishes results back to MQTT

Usage:
  Publish to: energy/control/register/write
  Payload: {"register": 1044, "value": 1}
  
  Or for specific inverter:
  Publish to: energy/NTCRBLR00Y/control/register/write
  Payload: {"register": 1044, "value": 1}
  
Response published to: energy/control/register/result or energy/{inverter_id}/control/register/result
"""

import paho.mqtt.client as mqtt
import json
import sys
import requests
import time
from datetime import datetime

# Import Grott configuration
sys.path.insert(0, '/opt/grott')
from grottconf import Conf

# Configuration
GROTTSERVER_URL = "http://172.17.254.10:5782"
INVERTER_ID = "NTCRBLR00Y"

# Global configuration object
conf = None


def write_register(inverter_id, register, value):
    """Write a register value to the inverter"""
    url = f"{GROTTSERVER_URL}/inverter"
    params = {
        "command": "register",
        "inverter": inverter_id,
        "register": register,
        "value": value
    }
    
    try:
        response = requests.put(url, params=params, timeout=10)
        if response.status_code == 200:
            try:
                data = response.json()
                return {"success": True, "data": data, "register": register, "value": value}
            except:
                return {"success": True, "message": "Register written successfully", "register": register, "value": value}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}", "register": register}
    except Exception as e:
        return {"success": False, "error": str(e), "register": register}


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connected to MQTT broker")
        
        # Subscribe to control topics
        if conf.mqttinverterintopic:
            # Subscribe to inverter-specific topic
            topic = f"{conf.mqtttopic}/{INVERTER_ID}/control/register/write"
            client.subscribe(topic)
            print(f"  Subscribed to: {topic}")
        
        # Subscribe to general control topic
        topic = f"{conf.mqtttopic}/control/register/write"
        client.subscribe(topic)
        print(f"  Subscribed to: {topic}")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    """Callback when message is received"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{timestamp}] Received MQTT message:")
    print(f"  Topic: {msg.topic}")
    print(f"  Payload: {msg.payload.decode()}")
    
    try:
        # Parse JSON payload
        data = json.loads(msg.payload.decode())
        
        # Extract parameters
        register = data.get("register")
        value = data.get("value")
        inverter = data.get("inverter", INVERTER_ID)
        
        if register is None or value is None:
            error_msg = {"success": False, "error": "Missing 'register' or 'value' in payload"}
            print(f"  ERROR: {error_msg['error']}")
            publish_result(client, inverter, error_msg)
            return
        
        print(f"  Writing register {register} = {value} to inverter {inverter}")
        
        # Write the register
        result = write_register(inverter, register, value)
        
        # Publish result
        publish_result(client, inverter, result)
        
        if result["success"]:
            print(f"  SUCCESS: Register {register} written successfully")
        else:
            print(f"  ERROR: {result.get('error', 'Unknown error')}")
            
    except json.JSONDecodeError as e:
        error_msg = {"success": False, "error": f"Invalid JSON: {str(e)}"}
        print(f"  ERROR: {error_msg['error']}")
        publish_result(client, INVERTER_ID, error_msg)
    except Exception as e:
        error_msg = {"success": False, "error": f"Exception: {str(e)}"}
        print(f"  ERROR: {error_msg['error']}")
        publish_result(client, INVERTER_ID, error_msg)


def publish_result(client, inverter_id, result):
    """Publish result back to MQTT"""
    # Add timestamp
    result["timestamp"] = datetime.now().isoformat()
    result["inverter"] = inverter_id
    
    # Build result topic
    if conf.mqttinverterintopic:
        topic = f"{conf.mqtttopic}/{inverter_id}/control/register/result"
    else:
        topic = f"{conf.mqtttopic}/control/register/result"
    
    # Publish
    payload = json.dumps(result)
    client.publish(topic, payload, qos=0, retain=False)
    print(f"  Published result to: {topic}")


def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    if rc != 0:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Unexpected disconnect, return code {rc}")
        print("  Attempting to reconnect...")


def main():
    """Main loop"""
    global conf
    
    print("="*80)
    print("Grott MQTT Control Handler")
    print("="*80)
    
    # Load Grott configuration
    print("Loading Grott configuration from grott.ini...")
    try:
        conf = Conf("2.8.3")
        print(f"Grottserver: {GROTTSERVER_URL}")
        print(f"Inverter ID: {INVERTER_ID}")
        print(f"MQTT Broker: {conf.mqttip}:{conf.mqttport}")
        print(f"MQTT Topic:  {conf.mqtttopic}")
        print(f"MQTT Auth:   {'Enabled' if conf.mqttauth else 'Disabled'}")
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
    
    # Create MQTT client
    client = mqtt.Client(client_id=f"{conf.inverterid}_control")
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Set authentication if enabled
    if conf.mqttauth:
        client.username_pw_set(conf.mqtt_user, conf.mqtt_pass)
    
    # Connect to MQTT broker
    try:
        print(f"\nConnecting to MQTT broker {conf.mqttip}:{conf.mqttport}...")
        client.connect(conf.mqttip, conf.mqttport, 60)
    except Exception as e:
        print(f"ERROR: Failed to connect to MQTT broker: {e}")
        sys.exit(1)
    
    # Start MQTT loop
    print("\nListening for MQTT control commands...")
    print("Press Ctrl+C to exit\n")
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        client.disconnect()
        sys.exit(0)


if __name__ == "__main__":
    main()
