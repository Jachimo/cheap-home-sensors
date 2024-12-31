# This file is executed on every boot (including wake-boot from deepsleep)

import machine
import esp
import gc
import micropython

# Better OOM error reporting
micropython.alloc_emergency_exception_buf(100)
# Turn off vendor OS debugging messages
esp.osdebug(None)
# Set to 80MHz mode (default)
machine.freq(80000000)
# Enable garbage collection
gc.collect()
