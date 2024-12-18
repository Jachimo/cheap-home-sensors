# This file is executed on every boot (including wake-boot from deepsleep)


#import esp
#esp.osdebug(None)
import os, machine
import gc
#import webrepl

#os.dupterm(None, 1) # disable REPL on UART(0)

#webrepl.start()
gc.collect()
