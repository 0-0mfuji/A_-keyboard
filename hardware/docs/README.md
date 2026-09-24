# Keyboard Hardware CAD

Editable KiCad 9+ initial design. Hardware has not been tested. Route the PCB and review ERC/DRC before fabrication.

Plus SMD module: 17 allocatable GPIOs including D11-D13 and D17-D19. D14/D15 (NFC), D16 (battery ADC), charging and debug pins are reserved. BAT+ is pad 28; GND pads are 13/27/29. USB, regulation and 1S LiPo charging are integrated. Solder additional small castellations and underside pads; standard 1x7 headers do not connect them. Keep copper and metal clear of the antenna.

USB powers the module and its onboard charger. Use a protected 3.7 V nominal / 4.2 V maximum 1S LiPo rated for at least 100 mA charging. No LiFePO4 or primary cells. P0.13 selects approximately 50/100 mA; firmware must configure charging. VBUS is unavailable on battery. Battery protection is not supplied by the charger.

External PMW3610 SEIBOKU connection point. The header can be placed without a separate sensor item; it connects MCU SPI/SDIO, MOTION, and NCS signals. Pin 1=3V3, 2=GND, 3/4=NC, 5=SCLK, 6=SDIO, 7=MOTION, 8=NCS.

Diodes: 1N4148W, SOD-123. Pin 1 = cathode K = ROW. Pin 2 = anode A = switch. Matrix direction: COL2ROW. Diodes are on the back; the silkscreen bar marks K.

PCB outline: auto-tight, 1 mm margin, R1 mm, copper-to-edge rule 0.5 mm. Generated Edge.Cuts follows the key and component envelope. Mounting NPTH holes: 3 generated. Stabilizer NPTH holes: 6. RGB: SK6812MINI-E, 59 LEDs. Review case, keycap, USB cable, antenna, battery and stabilizer access separately. Dwgs.User shows KLE key envelopes; those lines are not copper, silkscreen or board cuts.

Derived from KLE-NG; this is an independent, unofficial application.
