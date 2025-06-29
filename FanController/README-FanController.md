# FanController

**Work in Progress!**

> MicroPython code for making a common HEPA filter (or other device with a 
> multi-speed fan with separate motor taps) into a 'smart' device that can be
> controlled remotely as part of a home automation system.

## Background

The inspiration for this project was the relatively high cost and general lack
of options for off-the-shelf 'smart' HEPA filters, and the very low cost and
wide availability of basic 3- or 4-speed filters at my local Goodwill.

## Goals

Goals included both the ability to turn the fan on/off and change speed
remotely from the HA system, but also to retain the ability to (temporarily) 
override the HA system and force the fan on or off with physical buttons.

Also, I wanted to integrate a temperature sensor, because why the hell not.

Future iterations may add some sort of air-quality sensor, or perhaps just a
pair of pressure sensors located on the 'high' and 'low' sides of the fan, to
aid in determining when the HEPA filters need to be changed.

