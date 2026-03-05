<!-- Blender MCP Server - GitHub Copilot Instructions -->

## Project Overview
This is a Model Context Protocol (MCP) server for Blender integration that allows GitHub Copilot Pro to control Blender through Python API calls using the bpy module.

## Key Components
- **MCP Server**: Python-based server that exposes Blender operations
- **Blender Addon**: Script that runs inside Blender to bridge with MCP server
- **bpy API Wrappers**: Safe wrappers around Blender's Python API
- **VS Code Integration**: Configuration for seamless MCP usage

## Coding Guidelines

### Blender API Usage
- Always use `bpy.context` and `bpy.data` safely with proper error handling
- Implement proper cleanup for mesh operations and scene modifications
- Use Blender's bmesh module for complex mesh operations
- Handle Blender's mode switching (Edit/Object mode) carefully
- Always check if objects exist before operating on them

### MCP Server Patterns
- Each Blender operation should be a separate MCP tool
- Use proper JSON schema validation for tool parameters
- Implement comprehensive error handling with user-friendly messages
- Log all operations for debugging
- Use async/await patterns where appropriate

### Safety Considerations
- Validate all input parameters before passing to Blender API
- Implement undo/redo support for destructive operations  
- Check Blender context before executing operations
- Handle Blender crashes gracefully
- Provide preview modes for destructive operations

### Code Structure
- Keep Blender operations in separate modules by category (mesh, animation, materials, etc.)
- Use type hints throughout the codebase
- Implement proper logging at different levels
- Create helper functions for common Blender patterns
- Use dependency injection for testability

## Example Operations to Support
- Mesh creation and modification
- Material and texture assignment
- Animation keyframe management
- Scene setup and lighting
- Camera positioning and animation
- Rendering operations
- Import/Export operations
- Modifier application

## Development Workflow
- Test each MCP tool individually
- Use Blender's background mode for automated testing
- Implement integration tests with actual Blender scenes
- Use Docker for consistent development environment
- Maintain compatibility with latest Blender LTS version