#!/bin/bash
pushd ~/shared_memory_can
source ~/.local/pipx/venvs/cpython/bin/activate

export UAVCAN__NODE__ID=42                           # Set the local node-ID 42 (anonymous by default)
export UAVCAN__CAN__IFACE="socketcan:can2"           # Use CAN can2 as transport layer
export UAVCAN__CAN__INSTANCE=2
export UAVCAN__CAN__BITRATE="500000"         # 500kbits
export UAVCAN__CAN__MTU=8               # Maximum Transmission Unit (largest package size for socketcana single frame) CAN FD
export UAVCAN__DIAGNOSTIC__SEVERITY=2
export CYPHAL_PATH=/home/amazon/.dsdl
export PYTHONPATH=/home/amazon/.dsdl:/home/amazon/.local/pipx/venvs:$PYTHONPATH
export CAN_FD=0

python3 ~/shared_memory_can/main.py
