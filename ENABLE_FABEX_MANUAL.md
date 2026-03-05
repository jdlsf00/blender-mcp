# 🔧 Fabex CNC Addon - Manual Enablement Required

## ✅ Installation Status: COMPLETE

**Fabex v1.0.68** is installed at:

```
C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org\fabex\
```

**Module name**: `bl_ext.blender_org.fabex`

---

## ⚠️ Why You Don't See It

Blender 4.5 uses a **new Extensions system** (not the old Add-ons system). Extensions require:

1. Manual enablement through the Extensions panel
2. User interaction (cannot be fully automated via scripts)

---

## 📋 Step-by-Step: Enable Fabex

### Method 1: Through Extensions Panel (Recommended)

1. **Open Blender** (not background mode - open the full GUI)

2. **Open Extensions Panel**:

   - Top menu: **Edit** → **Preferences** (or press `Ctrl+,`)
   - Look at the left sidebar
   - Click **Get Extensions** (NOT "Add-ons")

3. **Find Fabex**:

   - You should see an "Installed" section or local extensions
   - Look for **"Fabex CNC (formerly BlenderCAM)"**
   - Or use the search box and type: `Fabex` or `CNC`

4. **Enable It**:

   - Find the checkbox or toggle button next to Fabex
   - Click to enable it
   - You should see: ✓ Fabex CNC

5. **Close Preferences**:

   - Preferences will auto-save
   - Close the Preferences window

6. **Verify**:
   - Open any Blender file (or create new scene)
   - Press `N` key to show right sidebar
   - Look for **"Fabex CNC"** tab at the top of the sidebar
   - If you see it: ✅ Success!

---

### Method 2: Alternative Locations to Check

If you don't see it in Extensions panel, try:

**A) Old Add-ons Panel**:

- Edit → Preferences → **Add-ons** (not Get Extensions)
- Search: `Fabex`
- Enable if found

**B) Search All Tabs**:

- In Preferences, try searching in the search box at top-right
- Type: `Fabex` or `CNC`
- Blender will show matching items

---

## 🎯 What to Expect After Enabling

Once enabled, you'll have access to:

1. **Fabex Panel** (Press `N` in 3D View):

   - CAM Operations
   - Machine settings
   - Tool library
   - G-code export

2. **3D View Menus**:

   - Add → Curve → Fabex items
   - Object → Fabex tools

3. **Export Menu**:
   - File → Export → Fabex G-code

---

## 🔍 Troubleshooting

### Issue: "I don't see Extensions in Preferences"

**Solution**: You might be looking at the wrong place:

- Make sure you're in **Edit → Preferences**
- Look for these tabs on the LEFT sidebar:
  - Get Extensions (NEW in Blender 4.2+)
  - Add-ons (old system)
- Fabex should appear in **Get Extensions** tab

### Issue: "Extensions panel is empty"

**Solution**: Check installation location:

```powershell
Test-Path "C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org\fabex"
```

Should return: `True`

If False, the addon moved or was deleted. Re-run:

```powershell
.\install_blendercam.ps1
```

### Issue: "Fabex appears but won't enable"

**Check console for errors**:

1. Window → Toggle System Console
2. Try enabling Fabex again
3. Look for red error messages

**Common error**: Missing Python dependency

```powershell
# Install shapely (if not already installed)
& "C:\Program Files\Blender Foundation\Blender 4.5\4.5\python\bin\python.exe" -m pip install shapely
```

### Issue: "I enabled it but don't see the panel"

**Verify in 3D View**:

1. Make sure you're in the **3D Viewport** (not Shader Editor, etc.)
2. Press `N` key to toggle sidebar visibility
3. Look at the TABS at the top of the sidebar (Tool, Item, Fabex CNC, etc.)
4. Click the **Fabex CNC** tab

**If still not visible**:

- Restart Blender
- Check if it's actually enabled (Edit → Preferences → search "Fabex")

---

## 📸 Visual Guide

### What to Look For:

**In Preferences → Get Extensions:**

```
┌─────────────────────────────────────────┐
│ Get Extensions                          │
├─────────────────────────────────────────┤
│ [Search box]                            │
│                                         │
│ ▶ Installed (1)                        │
│   ✓ Fabex CNC (formerly BlenderCAM)   │
│                                         │
└─────────────────────────────────────────┘
```

**In 3D View Sidebar (Press N):**

```
┌────────────────┐
│ Tool │ Item │ Fabex CNC │  ← Click here
├────────────────┤
│                │
│ CAM Operations │
│ [+ Add new]    │
│                │
│ Machine        │
│ Post Processor │
│                │
└────────────────┘
```

---

## ✅ Verification Commands (After Enabling)

Run this to confirm it's loaded:

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --background --python "F:\Documents\CODE\Blender-MCP\check_addons.py"
```

You should see:

```
=== Checking for Fabex variants ===
  bl_ext.blender_org.fabex: True  ← Should say True!
```

---

## 🚀 Next Steps After Enabling

1. **Open your project**:

   ```
   F:\Documents\CODE\Blender-MCP\reference_projects\4axis_helix_reference.blend
   ```

2. **Follow the workflow**:
   - See: `VALIDATION_CHECKLIST.md`
   - Configure HELIX CAM operation
   - Export G-code
   - Validate with `validate_gcode.ps1`

---

## 📞 Need Help?

If you're still stuck:

1. Take a screenshot of your Blender Preferences window
2. Run the check script and share output
3. Check Blender console (Window → Toggle System Console) for errors

---

**TL;DR**: Open Blender GUI → Edit → Preferences → Get Extensions → Find "Fabex CNC" → Enable checkbox → Done!
