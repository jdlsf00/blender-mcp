# 🏭 BlenderCAM MCP Integration & Enhancement Plan

**Date**: November 12, 2025
**Status**: ✅ STL API Fixed | 🔄 Integration Planning | 📋 Enhancement Analysis
**Blender Version**: 4.5.3 LTS
**BlenderCAM Location**: `F:\Documents\Blender\blendercam-master\`

---

## 🎯 Executive Summary

**Mission**: Full integration between Blender-MCP and BlenderCAM (now Fabex) for natural language CNC automation, plus code review for enhancement opportunities.

**Key Discoveries**:

1. ✅ **STL API Already Updated**: `bpy.ops.wm.stl_import()` correctly implemented (Blender 4.5)
2. ✅ **BlenderCAM is Production-Ready**: 50+ modules, 40+ post-processors, 13+ years of development
3. ⚠️ **4-Axis Limitation**: Only INDEXED strategy (manual positioning), no continuous rotation
4. 🚀 **Integration Strategy**: MCP wraps BlenderCAM operations instead of reimplementing

---

## 📊 BlenderCAM Architecture Analysis

### Core System Components

#### 1. **Operation Management** (`cam_operation.py` - 1197 lines)

```python
class camOperation(PropertyGroup):
    # Main operation properties
    name: StringProperty()
    filename: StringProperty()
    auto_export: BoolProperty()
    object_name: StringProperty()

    # Nested property groups
    material: CAM_MATERIAL_Properties      # Stock material settings
    info: CAM_INFO_Properties              # Operation metadata
    optimisation: CAM_OPTIMISATION_Properties  # Performance settings
    movement: CAM_MOVEMENT_Properties      # Feedrates, spindle, etc.
```

**Key Properties for MCP Integration**:

- `strategy`: 'PARALLEL', 'CROSS', 'BLOCK', 'SPIRAL', 'WATERLINE', 'DRILL', 'POCKET', 'CUTOUT', etc.
- `cutter_type`: 'BALLNOSE', 'FLAT', 'VCARVE', 'BULLNOSE', 'BALLCONE'
- `cutter_diameter`: Tool size in meters (0.003 = 3mm)
- `feedrate`: Feed rate in m/min (1.0 = 1000mm/min)
- `spindle_rpm`: Spindle speed (12000 RPM typical)
- `stepdown`: Z-axis step depth in meters
- `stepover`: XY stepover as percentage (0.5 = 50%)

#### 2. **Toolpath Calculation** (`ops.py` - 810 lines)

```python
class CalculatePath(bpy.types.Operator, AsyncOperatorMixin):
    """Main operator for toolpath generation"""
    bl_idname = "object.calculate_cam_path"
    bl_label = "Calculate CAM Path"

    async def execute(self, context):
        # Background processing with threading
        await gcodepath.getPath(context, operation)
```

**Architecture**:

- **Async Operations**: Uses `AsyncOperatorMixin` for non-blocking execution
- **Threading**: Custom `threadCom` class with `timer_update()` for monitoring
- **Error Handling**: `CamException`, `AsyncCancelledException`
- **Background Processing**: `PathsBackground` operator for long operations

#### 3. **G-code Generation** (`gcodepath.py` - 885 lines)

```python
def exportGcodePath(filename, vertslist, operations):
    """Main G-code export function"""
    # Uses post-processor from nc/ directory
    c = startNewFile()  # Creates Creator instance from nc.iso or other

    # Loop through operations and vertices
    for o in operations:
        for vert in verts:
            if plunging:
                c.feed(x=vx, y=vy, z=vz)  # G1 feed move
            else:
                c.rapid(x=vx, y=vy, z=vz)  # G0 rapid move

    c.program_end()
    c.file_close()
```

**Key Features**:

- **4-Axis Support**: Handles `a=ra, b=rb` parameters for rotary axes
- **File Splitting**: Can split large operations into multiple files
- **Progress Tracking**: `duration` and `cut_distance` calculation
- **Simulation**: Optional feedrate adjustment based on simulation data

#### 4. **Post-Processor System** (`nc/` directory - 40+ files)

**Base Architecture** (`nc/iso.py` - 1417 lines):

```python
class Creator(nc.Creator):
    def __init__(self):
        # Address objects for modal G-code
        self.f = Address('F', fmt=Format(number_of_decimal_places=2))
        self.s = AddressPlusMinus('S', fmt=Format(number_of_decimal_places=2))
        self.x = None
        self.y = None
        self.z = None

    def feed(self, x=None, y=None, z=None, a=None, b=None):
        """Generate feed move (G1)"""

    def rapid(self, x=None, y=None, z=None, a=None, b=None):
        """Generate rapid move (G0)"""

    def spindle(self, rpm, clockwise=True):
        """Generate spindle command (M3/M4)"""
```

**Grbl Post-Processor** (`nc/grbl.py` - Inherits from `iso_modal.py`):

```python
class Creator(iso_modal.Creator):
    def __init__(self):
        iso_modal.Creator.__init__(self)
        self.output_block_numbers = False
        self.output_tool_definitions = False

    def program_begin(self, id, comment):
        self.write('(Created with grbl post processor)\n')
```

**Available Post-Processors** (40+ formats):

- **Hobbyist**: grbl, mach3, smoothie
- **Industrial**: fanuc, heidenhain, siemens_840d, mazak, okuma
- **Educational**: shopbot_mtc, linuxcnc (emc2)
- **Specialty**: laser (grbl_laser), plasma, fadal, centroid1
- **3D Printing**: makerbot, printbot3d

---

## 🔧 MCP Integration Implementation

### Phase 1: Core Integration (Immediate Priority)

#### Tool 1: `setup_cam_operation`

```python
MCPTool("setup_cam_operation", "Configure BlenderCAM operation", {
    "object_name": str,
    "strategy": str,  # PARALLEL, CROSS, POCKET, etc.
    "cutter_type": str,  # BALLNOSE, FLAT, VCARVE
    "cutter_diameter": float,  # in mm (will convert to meters)
    "feedrate": float,  # mm/min
    "spindle_rpm": int,
    "stepdown": float,  # mm
    "stepover": float,  # percentage (0-1)
    "operation_name": str  # optional
})

def _setup_cam_operation(self, **params):
    script = f'''
import bpy

# Enable BlenderCAM addon if not enabled
if "cam" not in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_enable(module="cam")

# Create or get operation
if not hasattr(bpy.context.scene, 'cam_operations'):
    bpy.ops.scene.cam_operation_add()

operation = bpy.context.scene.cam_operations[0]

# Configure operation properties
operation.object_name = "{params['object_name']}"
operation.strategy = '{params['strategy']}'
operation.cutter_type = '{params['cutter_type']}'
operation.cutter_diameter = {params['cutter_diameter'] / 1000}  # Convert mm to m
operation.feedrate = {params['feedrate'] / 1000}  # Convert mm/min to m/min
operation.spindle_rpm = {params['spindle_rpm']}
operation.stepdown = {params['stepdown'] / 1000}  # Convert mm to m
operation.stepover = {params['stepover']}

print(f"✅ CAM operation configured: {{operation.name}}")
'''
    return self.execute_blender_script(script)
```

#### Tool 2: `calculate_cam_toolpath`

```python
MCPTool("calculate_cam_toolpath", "Generate toolpath with BlenderCAM", {
    "operation_name": str  # optional, calculates all if not specified
})

def _calculate_cam_toolpath(self, operation_name=None):
    script = f'''
import bpy

# Trigger BlenderCAM toolpath calculation
if "{operation_name}":
    # Calculate single operation
    operation = None
    for op in bpy.context.scene.cam_operations:
        if op.name == "{operation_name}":
            operation = op
            break

    if operation:
        bpy.context.scene.cam_active_operation = operation
        bpy.ops.object.calculate_cam_path()
        print(f"✅ Toolpath calculated: {{operation.name}}")
    else:
        print(f"❌ Operation not found: {operation_name}")
else:
    # Calculate all operations
    bpy.ops.object.calculate_cam_paths_all()
    print(f"✅ All toolpaths calculated")
'''
    return self.execute_blender_script(script)
```

#### Tool 3: `export_cam_gcode`

```python
MCPTool("export_cam_gcode", "Export G-code with post-processor", {
    "filename": str,
    "post_processor": str,  # grbl, iso, linuxcnc, fanuc, etc.
    "operation_name": str  # optional
})

def _export_cam_gcode(self, filename, post_processor="grbl", operation_name=None):
    script = f'''
import bpy
from cam import gcodepath

# Get operations to export
if "{operation_name}":
    operations = [op for op in bpy.context.scene.cam_operations if op.name == "{operation_name}"]
else:
    operations = list(bpy.context.scene.cam_operations)

# Get path objects
vertslist = []
for operation in operations:
    path_obj = bpy.data.objects.get(f"cam_path_{{operation.name}}")
    if path_obj:
        vertslist.append(path_obj.data)

# Set post-processor
bpy.context.scene.cam_machine.post_processor = '{post_processor}'

# Export G-code
if vertslist and operations:
    gcodepath.exportGcodePath("{filename}", vertslist, operations)
    print(f"✅ G-code exported: {filename} ({{len(operations)}} operations)")
else:
    print(f"❌ No toolpaths found to export")
'''
    return self.execute_blender_script(script)
```

### Phase 2: Advanced Features

#### Tool 4: `setup_4axis_operation`

```python
MCPTool("setup_4axis_operation", "Configure 4-axis indexed operation", {
    "object_name": str,
    "rotation_axis": str,  # A, B, or C
    "rotation_angle": float,  # degrees
    "strategy": str,
    # ... other CAM parameters
})
```

#### Tool 5: `simulate_cam_operation`

```python
MCPTool("simulate_cam_operation", "Run BlenderCAM simulation", {
    "operation_name": str
})
```

---

## 🔬 BlenderCAM Enhancement Opportunities

### Priority 1: Continuous 4-Axis Enhancement (HIGH COMPLEXITY)

**Current Limitation**:

- Only **INDEXED** strategy supported for 4-axis
- Manual positioning between operations
- No simultaneous continuous rotation

**Evidence from Code**:

```python
# From gcodepath.py line 876
elif (operation.machine_axes == '5' and operation.strategy5axis == 'INDEXED') or \
     (operation.machine_axes == '4' and operation.strategy4axis == 'INDEXED'):
    operation.orientation = prepareIndexed(operation)
    await getPath3axis(context, operation)
    cleanupIndexed(operation)

# From gcodepath.py line 880
elif operation.machine_axes == '4':
    await getPath4axis(context, operation)
```

**Root Cause Investigation Needed**:

1. Check `getPath4axis()` implementation (line 882+)
2. Review `getPathPattern4axis()` - seems to be implemented
3. Analyze why only 'PARALLELR', 'PARALLEL', 'HELIX', 'CROSS' strategies work
4. Investigate `sampleChunksNAxis()` function

**Proposed Enhancement**:

- Implement continuous simultaneous 4-axis for SPIRAL, ZIGZAG strategies
- Add cylindrical wrapping for engravings
- Enhance rotation synchronization with linear movements

**Complexity**: HIGH - Requires deep understanding of toolpath algorithms and geometry

---

### Priority 2: API Modernization (MEDIUM COMPLEXITY)

**Issues Found**:

- Mix of old and new Blender APIs
- Some deprecated functions still in use
- Not leveraging Blender 4.5+ features fully

**Specific Opportunities**:

1. Replace `bpy.context.scene.objects` with `bpy.data.objects` where appropriate
2. Update to new mesh API (BMesh operations)
3. Leverage Geometry Nodes for procedural toolpaths (experimental)
4. Use new Blender 4.5 Asset Browser for tool libraries

**Benefits**:

- Better performance
- Future-proofing
- Access to new Blender features

**Complexity**: MEDIUM - Gradual refactoring, can be done incrementally

---

### Priority 3: Performance Optimization (MEDIUM COMPLEXITY)

**Current State**:

```python
# From gcodepath.py line 815
if USE_PROFILER == True:
    import cProfile
    import pstats
    import io
    pr = cProfile.Profile()
    pr.enable()
    await getPath3axis(context, operation)
    pr.disable()
    pr.dump_stats(time.strftime("BlenderCAM_%Y%m%d_%H%M.prof"))
```

**Numba JIT Compilation**:

- `numba_wrapper.py` exists but unclear if fully enabled
- Potential for 10-100x speedup on geometry calculations
- NumPy operations throughout codebase are JIT-compilable

**Action Items**:

1. Enable profiling for representative operations
2. Identify bottlenecks (likely in `sampleChunks()`, `shapelyToChunks()`)
3. Test numba on hotspots
4. Consider Cython for critical sections

**Complexity**: MEDIUM - Profile-guided optimization

---

### Priority 4: MCP Native Integration (LOW COMPLEXITY)

**Concept**: Add MCP protocol directly to BlenderCAM addon

**Benefits**:

- No wrapper server needed
- Direct natural language control
- GitHub Copilot integration built-in
- Reduced latency

**Implementation**:

```python
# In BlenderCAM __init__.py
from mcp import MCPServer

class BlenderCAMMCPServer(MCPServer):
    def __init__(self):
        super().__init__("blendercam", "1.0")
        self.add_tool("calculate_path", self.calculate_path)

    def calculate_path(self, operation_name):
        # Direct operator call
        bpy.ops.object.calculate_cam_path()
```

**Complexity**: LOW - Mostly integration work

---

### Priority 5: Enhanced Simulation (HIGH COMPLEXITY)

**Current**: Basic 3D mesh simulation of finished product

**Enhancements**:

- Real-time material removal visualization
- GPU-accelerated voxel rendering
- Collision detection visualization
- Tool engagement analysis
- Chipload visualization

**Technologies**:

- OpenGL compute shaders for voxel carving
- Blender's EEVEE/Cycles for rendering
- Physics simulation for material removal

**Complexity**: HIGH - Requires shader programming and GPU optimization

---

## 📋 Implementation Roadmap

### Week 1: Core Integration

- [x] Fix STL API for Blender 4.5
- [ ] Implement `setup_cam_operation` MCP tool
- [ ] Implement `calculate_cam_toolpath` MCP tool
- [ ] Implement `export_cam_gcode` MCP tool
- [ ] Test complete workflow: STL → BlenderCAM → G-code

### Week 2: Testing & Documentation

- [ ] Test all 40+ post-processors
- [ ] Create usage examples with Copilot prompts
- [ ] Document BlenderCAM integration in README
- [ ] Performance testing with complex models

### Week 3: Enhancement Analysis

- [ ] Deep dive into `getPath4axis()` implementation
- [ ] Profile performance bottlenecks
- [ ] Test numba optimizations
- [ ] Create enhancement proposal document

### Week 4: Contribution Planning

- [ ] Review Fabex/BlenderCAM contribution guidelines (GPL-3.0)
- [ ] Draft pull request for continuous 4-axis
- [ ] Prepare API modernization patches
- [ ] Submit enhancement proposals to maintainers

---

## 🎯 Success Metrics

### Integration Success

- ✅ Natural language commands work: "Generate pocket toolpath with 6mm endmill"
- ✅ All post-processors tested and documented
- ✅ Complete STL → G-code workflow functional
- ✅ Performance: <10 seconds for typical operations

### Enhancement Success

- ✅ Continuous 4-axis implementation accepted by Fabex maintainers
- ✅ 2x performance improvement on complex operations
- ✅ API modernization complete for Blender 4.5+
- ✅ MCP native integration prototype working

---

## 🔗 Key Resources

### BlenderCAM/Fabex

- **GitHub**: https://github.com/vilemduha/blendercam
- **Documentation**: https://github.com/vilemduha/blendercam/wiki
- **License**: GPL-3.0
- **Maintainer**: Alain Pelletier, Vilem Novak

### Related Projects

- **OpenCAMLib**: C++ library for CAM algorithms
- **FreeCAD Path**: Open-source CAM (reference implementation)
- **GRBLControl**: G-code sender for testing

### Development Environment

- **Blender Version**: 4.5.3 LTS
- **Python Version**: 3.11 (bundled with Blender)
- **Dependencies**: shapely, Equation, opencamlib (auto-installed)

---

## 💡 Next Immediate Actions

1. **Update `manage_todo_list`**: Mark STL API fix as completed
2. **Implement `setup_cam_operation`**: Create first MCP wrapper tool
3. **Test with simple example**: Create cube → Setup operation → Calculate → Export
4. **Read `getPath4axis()`**: Understand 4-axis implementation thoroughly

**Status**: Ready to implement Phase 1 MCP integration tools! 🚀
