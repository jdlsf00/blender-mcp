# Fabex Workshop Toolkit

This toolkit generates three reusable resource types for Blender/Fabex workflows:

1. Fabex preset scripts for machines, tools, and operations.
2. Parametric SVG and Blender script templates for rings, bezels, pendants, studs, and tray molds.
3. Direct G-code for simple pockets and profile jobs.

## Usage

```powershell
python .\fabex_workshop\toolkit.py bootstrap-all
python .\fabex_workshop\toolkit.py install-presets
python .\fabex_workshop\toolkit.py bootstrap-and-install
python .\fabex_workshop\toolkit.py presets
python .\fabex_workshop\toolkit.py templates
python .\fabex_workshop\toolkit.py gcode
python .\fabex_workshop\toolkit.py full-batch
```

Generated files are written to `fabex_workshop\output` by default.

## What It Generates

### Presets

- `cam_machines\Genmitsu_4040_PRO_GRBL.py`
- `cam_cutters\flat_6.00mm_4F.py`
- `cam_cutters\flat_3.00mm_2F.py`
- `cam_cutters\ball_0.50mm_tapered.py`
- `cam_operations\Pocket_Roughing_4040_PRO.py`
- `cam_operations\Pocket_Finishing_4040_PRO.py`
- `cam_operations\Profile_Cutout_4040_PRO.py`

These are loadable from Blender's text editor with `Alt+P`.

`install-presets` copies them directly into your active Fabex preset folders.

### Templates

- `ring_band_blank.svg`
- `ring_band_blank.py`
- `tray_mold.svg`
- `tray_mold.py`
- `signet_blank.svg`
- `signet_blank.py`
- `bezel_pocket.svg`
- `bezel_pocket.py`
- `pendant_blank.svg`
- `pendant_blank.py`
- `oval_bezel_pocket.svg`
- `oval_bezel_pocket.py`
- `stud_earring_blank.svg`
- `stud_earring_blank.py`
- `coin_blank.svg`
- `coin_blank.py`
- `round_bezel_pocket.svg`
- `round_bezel_pocket.py`
- `bangle_blank.svg`
- `bangle_blank.py`
- `dogtag_blank.svg`
- `dogtag_blank.py`
- `cuff_blank.svg`
- `cuff_blank.py`
- `gallery_ring.svg`
- `gallery_ring.py`
- `basket_pendant.svg`
- `basket_pendant.py`
- `pierced_bezel_ring.svg`
- `pierced_bezel_ring.py`
- `hoop_earring.svg`
- `hoop_earring.py`
- `toggle_bracelet_blank.svg`
- `toggle_bracelet_blank.py`
- `index.html`

The `.svg` files are useful as importable outlines. The `.py` files create simple parametric geometry directly in Blender.

`index.html` gives you a one-page preview of every generated SVG template.

### Direct G-code

- `rectangular_pocket.nc`
- `circular_pocket.nc`
- `ring_band_profile.nc`

These bypass Fabex for simple, fully defined jobs.

The direct G-code layer now includes:

- material presets for hardwood, wax, and brass
- entry ramps instead of straight plunges
- finish passes for cleaner walls
- tabs on ring/band outer profiles

### Full Batch Profiles

- `machine_profiles\genmitsu_4040_pro_makita_rt0701c.json`
- `machine_profiles\genmitsu_4040_pro_makita_bits.json`
- `full_batch\fabex_operation_stacks\*_fabex_stack.json`
- `full_batch\machine_gcode_profiles\*_genmitsu4040_makita_profile.json`
- `full_batch\full_batch_summary.json`

This layer creates per-family Fabex operation stacks and machine-specific G-code profile presets for all template families.
