# electrode-array-layout

This code generates GDS files for arrays two-electrode devices with wirebond pads, and PCB (gerber) files for a corresponding PCB which the chip can be mounted and wirebonded to, to connect it out to measurement equipment.
I've made one-off chips like this a number of times, so I decided to systematize the code a bit and publish it in case anyone else can make use of it.
It's a bit messy! I offer this mostly as a starting point for others to modify into something that suits their needs.

It uses `GDSFactory` for GDS generation, and `pcbnew` for gerber file generation (note that `pcbnew` is internal to KiCad; you will need to install KiCad to use it).
