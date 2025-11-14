#!/bin/bash
# Test script for multiregister write and read functionality

SERVER="http://172.17.254.10:5782"
INVERTER="NTCRBLR00Y"

echo "Testing multiregister write and read functionality..."
echo "======================================================"
echo ""

echo "Step 1: Writing to registers 1080-1081 with value 09000e00"
echo "  Register 1080 should get: 0900"
echo "  Register 1081 should get: 0e00"
echo ""

WRITE_RESULT=$(curl -s -X PUT "${SERVER}/inverter?command=multiregister&inverter=${INVERTER}&startregister=1080&endregister=1081&value=09000e00")
echo "Write result: $WRITE_RESULT"
echo ""

# Wait a moment for the write to complete
sleep 2

echo "Step 2: Reading back register 1080"
REG1080=$(curl -s "${SERVER}/inverter?command=register&inverter=${INVERTER}&register=1080")
echo "Register 1080: $REG1080"
echo ""

echo "Step 3: Reading back register 1081"
REG1081=$(curl -s "${SERVER}/inverter?command=register&inverter=${INVERTER}&register=1081")

echo "Register 1081: $REG1081"
echo ""
echo "======================================================"
echo "Test complete!"
