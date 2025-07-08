import os
import importlib
import inspect
from typing import Dict, List, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ToolLoader:
    """Auto-discovery system for tools with @function_tool decorator."""
    
    def __init__(self, tools_directory: str = "app.tools"):
        self.tools_directory = tools_directory
        self.tools: Dict[str, Any] = {}
        self.discover_tools()
    
    def discover_tools(self) -> Dict[str, Any]:
        """Auto-discover all tools in the tools directory."""
        logger.info(f"Discovering tools in {self.tools_directory}")
        
        try:
            current_dir = Path(__file__).parent.parent
            tools_path = current_dir / "tools"
            
            logger.info(f"Looking for tools in: {tools_path}")
            
            if not tools_path.exists():
                logger.warning(f"Tools directory {tools_path} does not exist")
                return self.tools
            
            python_files = list(tools_path.glob("*.py"))
            python_files = [f for f in python_files if not f.name.startswith("__")]
            
            logger.info(f"Found {len(python_files)} Python files: {[f.name for f in python_files]}")
            
            for file_path in python_files:
                module_name = file_path.stem
                full_module_name = f"{self.tools_directory}.{module_name}"
                
                try:
                    module = importlib.import_module(full_module_name)
                    
                    for name, obj in inspect.getmembers(module):
                        # Skip standard imports and system objects
                        if name.startswith('__') or name in ['function_tool', 'logger', 'logging']:
                            continue
                            
                        # Check if it's a FunctionTool or decorated function
                        is_function_tool = 'FunctionTool' in str(type(obj))
                        is_function = inspect.isfunction(obj)
                        has_wrapped = hasattr(obj, '__wrapped__')
                        has_schema = hasattr(obj, '_function_tool_schema')
                        starts_with_tool_name = name.startswith(('get_', 'calculate', 'find_', 'search_', 'fetch_'))
                        
                        # Verify if it belongs to current module for regular functions
                        belongs_to_module = True
                        if is_function and not is_function_tool:
                            obj_module = getattr(obj, '__module__', '')
                            belongs_to_module = obj_module.startswith(full_module_name)
                        
                        has_tool_decorator = (
                            is_function_tool or 
                            (belongs_to_module and (has_wrapped or has_schema or starts_with_tool_name))
                        )
                        
                        if has_tool_decorator:
                            tool_name = getattr(obj, 'name', name)
                            self.tools[tool_name] = obj
                            logger.info(f"✅ Discovered tool: {tool_name} from {full_module_name}")
                        
                except Exception as e:
                    logger.error(f"Failed to load tool from {full_module_name}: {e}")
            
            logger.info(f"Total tools discovered: {len(self.tools)}")
            if self.tools:
                logger.info(f"Available tools: {list(self.tools.keys())}")
                
        except Exception as e:
            logger.error(f"Error during tool discovery: {e}")
            
        return self.tools
    
    def get_tool(self, name: str) -> Any:
        """Get a specific tool by name."""
        return self.tools.get(name)
    
    def get_tools_by_names(self, names: List[str]) -> List[Any]:
        """Get multiple tools by their names."""
        tools = []
        for name in names:
            tool = self.tools.get(name)
            if tool:
                tools.append(tool)
            else:
                logger.warning(f"Tool '{name}' not found in discovered tools")
        return tools
    
    def list_available_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self.tools.keys())
