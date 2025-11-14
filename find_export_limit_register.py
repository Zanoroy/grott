#!/usr/bin/env python3
"""
Find Export Limit Register by Monitoring Changes

This script reads a range of registers before and after you change 
the export limit setting in the Growatt app, then shows which 
registers changed.

Usage:
1. Run this script and note the "BEFORE" values
2. Change the export limit in the Growatt app (e.g., from 5000W to 3000W)
3. Run the script again and compare - changed registers are likely candidates
"""

import requests
import json
import sys
import time
from datetime import datetime

GROTTSERVER_URL = "http://172.17.254.10:5782"
INVERTER_ID = "NTCRBLR00Y"

# Register ranges to scan for SPH inverters
# Based on documentation: Storage (SPH Type) uses 0-124, 1000-1124, 1125-1249
REGISTER_RANGES = [
    (0, 124, "Basic Settings"),
    (1000, 1124, "Storage Power Settings"),
    (1125, 1249, "Extended Storage Settings")
]

def read_register(register, format_type="dec"):
    """Read a single register"""
    url = f"{GROTTSERVER_URL}/inverter"
    params = {
        "command": "register",
        "inverter": INVERTER_ID,
        "register": register,
        "format": format_type
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("value")
        else:
            return None
    except:
        return None


def scan_registers():
    """Scan all register ranges and return values"""
    results = {}
    total_registers = sum(end - start + 1 for start, end, _ in REGISTER_RANGES)
    current = 0
    
    print(f"\n{'='*80}")
    print(f"Scanning {total_registers} registers at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    for start, end, name in REGISTER_RANGES:
        print(f"Scanning {name} (registers {start}-{end})...")
        
        for register in range(start, end + 1):
            current += 1
            
            # Read in decimal format
            value_dec = read_register(register, "dec")
            value_hex = read_register(register, "hex")
            
            if value_dec is not None:
                results[register] = {
                    "dec": value_dec,
                    "hex": value_hex
                }
                
                # Show interesting values (non-zero)
                if value_dec != 0:
                    print(f"  R{register:04d}: {value_dec:6d} (0x{value_hex})")
            
            # Progress indicator
            if current % 50 == 0:
                print(f"  Progress: {current}/{total_registers} registers scanned...")
            
            # Small delay to avoid overwhelming the inverter
            time.sleep(0.05)
        
        print()
    
    return results


def compare_scans(before_file, after_file):
    """Compare two scan results and show differences"""
    try:
        with open(before_file, 'r') as f:
            before = json.load(f)
        with open(after_file, 'r') as f:
            after = json.load(f)
    except FileNotFoundError as e:
        print(f"ERROR: Could not find file: {e.filename}")
        return
    
    print(f"\n{'='*80}")
    print("REGISTER CHANGES DETECTED")
    print(f"{'='*80}\n")
    
    changes = []
    
    # Convert string keys back to integers for comparison
    before_regs = {int(k): v for k, v in before.items()}
    after_regs = {int(k): v for k, v in after.items()}
    
    # Check for changed values
    for reg in sorted(set(before_regs.keys()) | set(after_regs.keys())):
        before_val = before_regs.get(reg, {}).get("dec", 0)
        after_val = after_regs.get(reg, {}).get("dec", 0)
        
        if before_val != after_val:
            before_hex = before_regs.get(reg, {}).get("hex", "0")
            after_hex = after_regs.get(reg, {}).get("hex", "0")
            
            changes.append({
                "register": reg,
                "before_dec": before_val,
                "after_dec": after_val,
                "before_hex": before_hex,
                "after_hex": after_hex,
                "delta": after_val - before_val
            })
    
    if not changes:
        print("No changes detected between scans!")
        print("Make sure you changed the export limit setting before the second scan.\n")
        return
    
    print(f"Found {len(changes)} changed register(s):\n")
    print(f"{'Register':<10} {'Before':<15} {'After':<15} {'Delta':<10} {'Hex Before':<12} {'Hex After':<12}")
    print(f"{'-'*80}")
    
    for change in changes:
        print(f"R{change['register']:04d}      "
              f"{change['before_dec']:<15} "
              f"{change['after_dec']:<15} "
              f"{change['delta']:<+10} "
              f"0x{change['before_hex']:<10} "
              f"0x{change['after_hex']:<10}")
    
    print(f"\n{'='*80}")
    print("LIKELY EXPORT LIMIT CANDIDATES:")
    print(f"{'='*80}\n")
    
    # Look for registers in power-related ranges
    likely_candidates = [c for c in changes if c['register'] >= 1000]
    
    if likely_candidates:
        for change in likely_candidates:
            print(f"Register {change['register']}:")
            print(f"  Changed from {change['before_dec']} to {change['after_dec']}")
            print(f"  This is likely related to your export limit change!")
            print()
    else:
        print("Check all changed registers above - they may be in different ranges\n")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        if len(sys.argv) != 4:
            print("Usage: python3 find_export_limit_register.py compare <before.json> <after.json>")
            sys.exit(1)
        compare_scans(sys.argv[2], sys.argv[3])
        return
    
    # Perform scan
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"register_scan_{timestamp}.json"
    
    print("="*80)
    print("EXPORT LIMIT REGISTER FINDER")
    print("="*80)
    print("\nThis script will scan all documented SPH registers.")
    print("\nRECOMMENDED PROCEDURE:")
    print("1. Run this script now (saves 'BEFORE' snapshot)")
    print("2. Open Growatt app and change Export Limit setting")
    print("3. Wait 30 seconds for inverter to update")
    print("4. Run this script again (saves 'AFTER' snapshot)")
    print("5. Use 'compare' mode to find which register changed\n")
    
    input("Press Enter to start scan...")
    
    results = scan_registers()
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Scan complete! Results saved to: {output_file}")
    print(f"{'='*80}\n")
    print(f"Found {len(results)} readable registers")
    print(f"Non-zero registers: {sum(1 for v in results.values() if v['dec'] != 0)}\n")
    
    print("NEXT STEPS:")
    print(f"1. Change the Export Limit in your Growatt app")
    print(f"2. Wait 30 seconds")
    print(f"3. Run this script again to get a new snapshot")
    print(f"4. Compare the two files:")
    print(f"   python3 find_export_limit_register.py compare {output_file} register_scan_XXXXXX.json\n")


if __name__ == "__main__":
    main()
