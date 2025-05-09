from fastmcp import FastMCP
from tools.register import ToolsRegister
# from src.resources.register import ResourcesRegister
# from src.prompts.register import PromptsRegister

def create_mcp_server():
    """
    创建并配置FastMCP服务器实例。
    
    Returns:
        FastMCP: 配置好的FastMCP实例。
    """
    # 创建FastMCP实例
    mcp = FastMCP("Bilibili Mcp Server")
    
    # 注册各模块的工具
    tools_register = ToolsRegister(mcp)
    tools_register.register()
    
    # resources_register = ResourcesRegister(mcp)
    # resources_register.register()
    
    # prompts_register = PromptsRegister(mcp)
    # prompts_register.register()
    
    return mcp


if __name__ == "__main__":
    mcp = create_mcp_server()
    mcp.run()