from fastmcp import FastMCP
from tools import search

class ToolsRegister:
    """
    工具模块注册类，用于注册搜索等工具功能。
    """
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
    
    def register(self):
        """
        注册搜索相关的工具和功能。
        """
        # 调用search模块的注册方法，将mcp对象传递给它
        search.register_tools(self.mcp)