# Blender MCP Server - Test Examples

Test your Blender MCP server with these natural language commands in GitHub Copilot Pro.

## 🧪 **Basic Testing Commands**

### **Quick Verification**
```
@mcp Can you list the available Blender tools?
```
*Expected: List of 25+ MCP tools organized by category*

```
Create a simple red cube at the origin
```
*Expected: "✅ Mock: Created cube 'Cube' at (0, 0, 0)" (in mock mode)*

## 🎯 **Individual Tool Testing**

### **Mesh Operations**
```
Create a blue sphere named "TestSphere"
```
```
Add a metallic cylinder with 2-unit height
```
```
Move the cube to position (2, 0, 1)
```
```
Scale the sphere to 1.5x its current size
```
```
Rotate the cylinder 45 degrees around the Z-axis
```

### **Material System**
```
Create a red metallic material with 0.2 roughness
```
```
Make an emission material that glows green with strength 5
```
```
Assign the metallic material to the cube
```
```
Set the sphere's material metallic property to 0.8
```

### **Scene Management**  
```
Show me all objects in the current scene
```
```
Position the camera at (5, -5, 3) looking at the origin
```
```
Add a sun light above the scene with 3W energy
```
```
Create a new empty scene
```

### **Animation**
```
Animate the cube moving from (0,0,0) to (5,0,0) over 50 frames
```
```
Create a rotation animation: spin the sphere 360° over 100 frames
```
```
Set the timeline to run from frame 1 to 200
```
```
Add keyframes for the cylinder's current position at frame 25
```

### **Rendering**
```
Set render resolution to 1920x1080 at 100% quality
```
```
Configure Cycles render engine with 128 samples
```
```
Render the current scene as a PNG image
```
```
Set up EEVEE rendering with denoising enabled
```

## 🎨 **Complex Workflow Testing**

### **Product Visualization Workflow**
```
Create a product visualization scene:
1. Add a chrome cube with high metallic and low roughness values
2. Position camera at (7, -7, 5) for a good viewing angle  
3. Add a key light (sun) from the top-right
4. Add a fill light (point) to soften shadows
5. Set render resolution to 2560x1440
6. Configure Cycles with 256 samples for high quality
7. Render the final image
```

### **Simple Animation Sequence**
```
Create a logo animation:
1. Start with a cube at the origin
2. Create a blue emission material with strength 3
3. Apply the material to the cube
4. Animate the cube rotating 720° around Y-axis over 120 frames
5. Simultaneously animate scaling from 0.5x to 1.5x over same duration
6. Set camera at (8, -6, 4) pointing at the cube
7. Set timeline to 1-120 frames
8. Render the animation sequence
```

### **Architectural Preview**
```
Set up an architectural preview scene:
1. Create a large cube (10x10x3 units) as a building base
2. Add a smaller cube (2x2x4 units) on top as a tower
3. Create a concrete-like material (gray, low metallic, medium roughness)
4. Apply the material to both objects
5. Position sun light to simulate noon lighting
6. Set camera for exterior architectural view
7. Configure EEVEE for fast preview rendering
8. Render at 1080p resolution
```

## 🔧 **Debugging & Validation**

### **System Status Checks**
```
What Blender tools are currently available?
```
```
Show me the current scene information
```
```
List all materials in the scene
```
```
What's the current animation frame range?
```
```
Show me the current render settings
```

### **Error Handling Tests**
```
Try to delete an object that doesn't exist
```
*Expected: Graceful error message*

```
Set an invalid render format
```
*Expected: Error with valid format options*

```
Animate an object that doesn't exist  
```
*Expected: Object not found error*

## 🎭 **Mock Mode Responses**

When running in mock mode (without Blender), expect responses like:

- ✅ `Mock: Created cube 'TestCube' at (0, 0, 0)`
- ✅ `Mock: Assigned material 'RedMaterial' to object 'Cube'`
- ✅ `Mock: Moved camera 'Camera' to (5, -5, 3)`
- ✅ `Mock: Started animation playback`
- ✅ `Mock: Rendered image with CYCLES engine`

## 🚀 **Success Indicators**

Your MCP integration is working correctly when:

1. **Tool Discovery**: `@mcp` commands show 25+ Blender tools
2. **Natural Language**: Complex requests get broken into multiple tool calls
3. **Error Handling**: Invalid requests return helpful error messages  
4. **Workflow Execution**: Multi-step processes complete successfully
5. **Mock Responses**: All operations return realistic mock feedback

## 📊 **Performance Testing**

### **Stress Test Complex Workflow**
```
Create a complex scene with multiple animated objects:
1. Create 3 cubes at different positions
2. Create 3 different materials (red metallic, blue emission, green plastic)
3. Apply materials to respective cubes  
4. Animate each cube with different motions (rotate, scale, move)
5. Set up 3-point lighting
6. Position camera for dynamic view
7. Configure high-quality render settings
8. Render animation sequence
```

## 🎯 **Ready for Production**

Once these tests pass, your Blender MCP server is ready for:

- **AI-Assisted 3D Modeling**: Natural language object creation
- **Automated Scene Setup**: Complex lighting and camera work  
- **Animation Workflows**: Keyframe and timeline management
- **Render Pipeline**: Multi-engine rendering automation
- **Educational Use**: Learning Blender through conversation
- **Rapid Prototyping**: Quick 3D concept development

**Start with simple commands and gradually build up to complex workflows!** 🎨✨
