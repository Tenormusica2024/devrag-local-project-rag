import json

# Read the file
with open('.claude.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Navigate to the current project's mcpServers
project_path = r"C:\Users\Tenormusica"
if 'projects' in data and project_path in data['projects']:
    project = data['projects'][project_path]
    
    if 'mcpServers' not in project:
        project['mcpServers'] = {}
    
    # Add devrag configuration
    project['mcpServers']['devrag'] = {
        "type": "stdio",
        "command": "C:\\Users\\Tenormusica\\devrag-windows-x64.exe",
        "args": [],
        "env": {}
    }
    
    print(f"Added devrag to project: {project_path}")
    print(f"Current MCP servers: {list(project['mcpServers'].keys())}")
    
    # Write back
    with open('.claude.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\nConfiguration saved successfully!")
else:
    print(f"Project not found: {project_path}")
    print(f"Available projects: {list(data.get('projects', {}).keys())}")
