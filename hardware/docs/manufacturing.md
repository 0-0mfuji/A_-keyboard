# Routing and fabrication

Supported: soldered MX / Choc v1, XIAO RP2040, XIAO nRF52840 / nRF52840 Plus, and SEIBOKU.
RP2040 uses fitted 2.54 mm headers; nRF52840 uses surface mounting including underside pads.
For LiPo use only the nRF52840 integrated charger; see README.md for battery requirements.
SEIBOKU requires a mating 2x04 2.54 mm socket and spacers. Check lens and case clearance.
Keep copper, battery, metal and the case clear of the nRF52840 antenna; add a keepout in KiCad.
Hot-swap and automatic routing are not included.

1. Review the schematic, selected parts, diode polarity and module orientation.
2. Review the case, USB cable access, mounting points and stabilizers. When enabled,
   mounting and MX stabilizer holes are emitted as NPTH footprints and are excluded
   from the circuit BOM. Dwgs.User outlines are layout envelopes, not exact keycap geometry.
3. Route all airwires using the supplied netclass; review current-dependent power widths.
4. Refill any copper zones you add. Run ERC and DRC with schematic parity enabled.
   Resolve all errors and review warnings; the application does not waive DRC violations.
5. Export Gerbers for F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS and Edge.Cuts,
   plus Excellon drill files (plated and non-plated holes). Exclude Dwgs.User/Eco2.User.
6. Inspect the Gerber/drill files in a viewer and JLCPCB's upload preview before ordering.
   Confirm the board dimensions, holes, layers, thickness and order options.

This is a bare PCB workflow. The ZIP includes a grouped generic BOM plus review-only
assembly-bom.csv and hand-assembly.csv. Assembly requires separately validated sourcing,
MPN/LCSC selection and component positions; no manufacturing package is generated here.
Fabrication guide: https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-7

See footprint-sources.json and licenses/ for fixed library provenance and adaptations.
Choc v1 is a community library; MX/diode are KiCad official and XIAO is Seeed supplied.
SEIBOKU carrier geometry is adapted from snize under CERN-OHL-P-2.0.
No physical hardware test has been performed. Manufacturing files must be generated
from your final routed board, not this unrouted initial placement.
