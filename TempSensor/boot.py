# This file is executed on every boot (including wake-boot from deepsleep)

import machine
import esp
import gc

# Turn off vendor OS debugging messages
esp.osdebug(None)
# Set to 80MHz mode (default)
machine.freq(80000000)
# Enable garbage collection
gc.collect()

