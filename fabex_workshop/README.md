# Fabex Workshop Toolkit

This toolkit generates three reusable resource types for Blender/Fabex workflows:

1. Fabex preset scripts for machines, tools, and operations.
2. Parametric SVG and Blender script templates for rings, bezels, pendants, studs, and tray molds.
3. Direct G-code for simple pockets and profile jobs.
4. Parametric mold-job bundles for coin, dogtag, and domino workflows.

## Usage

```powershell
python .\fabex_workshop\toolkit.py bootstrap-all
python .\fabex_workshop\toolkit.py install-presets
python .\fabex_workshop\toolkit.py bootstrap-and-install
python .\fabex_workshop\toolkit.py presets
python .\fabex_workshop\toolkit.py templates
python .\fabex_workshop\toolkit.py gcode
python .\fabex_workshop\toolkit.py full-batch
python .\fabex_workshop\toolkit.py mold-job --mold-type coin --job-name coin_38mm --diameter-mm 38 --thickness-mm 3.2
python .\fabex_workshop\toolkit.py mold-job --mold-type dogtag --job-name dogtag_30x52 --width-mm 30 --height-mm 52 --thickness-mm 2.5 --use-gn
python .\fabex_workshop\toolkit.py mold-job --mold-type domino --job-name domino_50x25 --width-mm 50 --height-mm 25 --thickness-mm 4.0 --corner-radius-mm 2.2
python .\fabex_workshop\toolkit.py mold-cam --job-name domino_50x25
python .\fabex_workshop\toolkit.py mold-cam --job-name domino_50x25 --run-blender
python .\fabex_workshop\toolkit.py mold-cam --job-name domino_50x25 --run-blender --strict-cam
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

### Where To Find Jewelry Templates In Blender

Jewelry templates are not shown in the Fabex machine/cutter/operation preset dropdowns.

Use either workflow:

1. Open `fabex_workshop\output\templates\index.html` to browse families and pick a template.
2. In Blender, open the paired `*.py` template script in the Text Editor and run it with `Alt+P`.
3. Or import the paired `*.svg` outline for profile-based workflows.

Fabex dropdowns are only for:

- machine presets (`cam_machines`)
- cutter presets (`cam_cutters`)
- operation presets (`cam_operations`)

### Geometry Nodes (Optional Enhancement)

The following template scripts now include optional Geometry Nodes enhancement blocks:

- `ring_band_blank.py`
- `bezel_pocket.py`
- `pendant_blank.py`

Each script defines:

- `USE_GEOMETRY_NODES = True`

Set that flag to `False` if you want pure mesh/boolean output only.
Fabex/CAM flows remain compatible either way.

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

### Mold Job Bundles (Phase 2 + Phase 3 Unified)

`mold-job` is the programmable bridge from manual setup to automation. For each mold job, it writes a dedicated package to:

- `output\mold_jobs\<job_name>\<job_name>_mold.py`
- `output\mold_jobs\<job_name>\<job_name>_fabex_stack.json`
- `output\mold_jobs\<job_name>\<job_name>_machine_profile.json`
- `output\mold_jobs\<job_name>\<job_name>_roughing.nc`
- `output\mold_jobs\<job_name>\<job_name>_manifest.json`

Recommended manual-to-automation loop:

1. Generate one mold job with explicit dimensions (`mold-job`).
2. Open the generated `*_mold.py` in Blender and run with `Alt+P`.
3. Confirm cavity dimensions and orientation manually.
4. Load the generated Fabex stack/profile JSON values as CAM defaults.
5. Validate a shallow/air pass from `*_roughing.nc`.
6. Once validated, reuse command arguments to regenerate consistent jobs quickly.

GN is optional in mold scripts (`--use-gn`). Keep GN off for strict dimensional repeatability and turn it on when you want smoother parametric shaping before CAM.

### No-Click CAM Batch From Mold JSON

`mold-cam` consumes an existing mold job manifest and creates automated Fabex CAM batch assets in the same job folder:

- `<job_name>_cam_batch.py` (Blender background CAM script)
- `<job_name>_run_cam_batch.ps1` (runner script)

When run in Blender background, the CAM batch script will:

1. enable Fabex
2. build the mold geometry from the generated mold script
3. create all CAM operations from the generated stack JSON
4. calculate toolpaths and export per-operation G-code files
5. write `cam_output\<job_name>_cam_report.json`

This is the scripted path toward full automation. Manual work can stay focused on fixturing, zeroing, and first-pass validation.

If Fabex path calculation/export fails for a given operation, the batch script now writes fallback G-code files from the generated roughing baseline and records that status in the CAM report. This keeps the pipeline usable while you tune Fabex-specific runtime issues.

Use `--strict-cam` to disable fallback and fail-fast on any CAM operation error.
