from bilibili_api import search, video_zone
from bilibili_api.utils.network import Credential
from typing import Callable
from fastmcp import FastMCP

# 全局变量存储mcp实例
_mcp: FastMCP | None = None

def register_tools(mcp: FastMCP):
    """
    注册所有搜索相关的工具到mcp实例。
    
    Args:
        mcp (FastMCP): FastMCP实例
    """
    global _mcp
    _mcp = mcp
    
    # 注册
    general_search.register()
    search_by_type.register()
    get_default_search_keyword.register()
    get_hot_search_keywords.register()
    get_suggest_keywords.register()
    search_games.register()
    search_mangasearch_manga.register()
    search_cheese.register()


def tool(func: Callable) -> Callable:
    """
    工具函数装饰器，用于标记需要注册到mcp的函数。
    
    Args:
        func (Callable): 要注册的函数
        
    Returns:
        Callable: 装饰后的函数
    """
    setattr(func, 'register', lambda: _mcp.tool()(func) if _mcp else None)
    return func


@tool
async def general_search(keyword: str, page: int = 1) -> dict:
    """
    搜索Bilibili API，使用给定关键词进行基本搜索。

    Args:
        keyword (str): 在Bilibili API上搜索的关键词。
        page    (int): 页码. Defaults to 1.
    Returns:
        dict: 包含Bilibili API搜索结果的字典。
    """
    return await search.search(keyword, page=page)


@tool
async def search_by_type( 
    keyword: str, 
    search_type: str,
    order_type: str | None = None,
    time_range: int = -1,
    video_zone_type: str | None = None,
    order_sort: int | None = None,
    category_id: str | int | None = None,
    time_start: str | None = None,
    time_end: str | None = None,
    page: int = 1,
    page_size: int = 42
) -> dict:
    """
    按特定类型搜索Bilibili内容，支持多种筛选条件。

    Args:
        keyword (str): 搜索关键词
        search_type (str): 搜索类型，支持以下值：
            - "VIDEO": 视频
            - "BANGUMI": 番剧
            - "FT": 影视
            - "LIVE": 直播
            - "ARTICLE": 专栏
            - "TOPIC": 话题
            - "USER": 用户
            - "LIVEUSER": 直播用户
            - "PHOTO": 相册
        order_type (str | None): 排序类型，根据search_type不同而变化：
            - 视频："TOTALRANK"(综合), "PUBDATE"(发布日期), "CLICK"(播放量), 
                  "DM"(弹幕), "STOW"(收藏), "SCORES"(评论)
            - 用户："FANS"(粉丝数), "LEVEL"(等级)
            - 直播："NEWLIVE"(最新开播), "ONLINE"(综合排序)
            - 专栏："TOTALRANK"(综合), "PUBDATE"(发布日期), "CLICK"(播放量), 
                   "ATTENTION"(喜欢), "SCORES"(评论)
        time_range (int): 视频时长范围(分钟)，仅视频搜索有效
            - -1: 全部时长
            - 0-10: 10分钟以下
            - 10-30: 10-30分钟
            - 30-60: 30-60分钟
            - >60: 60分钟以上
        video_zone_type (str | None): 视频分区类型，仅视频搜索有效
            例如："DOUGA_MMD", "GAME_STANDALONE" 等
        order_sort (int | None): 排序方式，0为从高到低，1为从低到高，仅用户搜索有效
        category_id (str | int | None): 专栏/相簿分区ID，仅专栏和相册搜索有效
            - 专栏可选值："ALL", "ANIME", "GAME", "TV", "LIFE", 
                        "HOBBY", "LIGHTNOVEL", "TECHNOLOGY"
            - 相册可选值："ALL", "DRAWFRIEND", "PHOTOFRIEND"
        time_start (str | None): 起始时间，格式为"YYYY-MM-DD"
        time_end (str | None): 结束时间，格式为"YYYY-MM-DD"
        page (int): 页码，默认为1
        page_size (int): 每页结果数量，默认为42

    Returns:
        dict: 包含搜索结果的字典
    """
    # 将搜索类型字符串转换为枚举
    try:
        search_obj_type = getattr(search.SearchObjectType, search_type.upper())
    except AttributeError:
        return {
            "code": -1, 
            "message": f"无效的搜索类型: {search_type}",
            "valid_types": [t.name for t in search.SearchObjectType]
        }
    
    # 处理排序类型
    order_enum = None
    if order_type:
        try:
            if search_type.upper() == "VIDEO":
                # 视频排序选项：综合排序、发布日期、播放量等
                order_enum = getattr(search.OrderVideo, order_type.upper())
            elif search_type.upper() == "USER":
                # 用户排序选项：粉丝数、等级
                order_enum = getattr(search.OrderUser, order_type.upper())
            elif search_type.upper() in ["LIVE", "LIVEUSER"]:
                # 直播排序选项：最新开播、人气
                order_enum = getattr(search.OrderLiveRoom, order_type.upper())
            elif search_type.upper() == "ARTICLE":
                # 专栏排序选项：综合排序、发布日期、播放量等
                order_enum = getattr(search.OrderArticle, order_type.upper())
        except AttributeError:
            valid_orders = []
            if search_type.upper() == "VIDEO":
                valid_orders = [t.name for t in search.OrderVideo]
            elif search_type.upper() == "USER":
                valid_orders = [t.name for t in search.OrderUser]
            elif search_type.upper() in ["LIVE", "LIVEUSER"]:
                valid_orders = [t.name for t in search.OrderLiveRoom]
            elif search_type.upper() == "ARTICLE":
                valid_orders = [t.name for t in search.OrderArticle]
                
            return {
                "code": -1, 
                "message": f"无效的排序类型: {order_type}",
                "valid_orders": valid_orders
            }
    
    # 处理视频分区类型
    zone_type = None
    if video_zone_type and search_type.upper() == "VIDEO":
        try:
            zone_type = getattr(video_zone.VideoZoneTypes, video_zone_type.upper())
        except AttributeError:
            return {
                "code": -1, 
                "message": f"无效的视频分区类型: {video_zone_type}",
                "valid_zone_types": [t.name for t in video_zone.VideoZoneTypes]
            }
    
    # 处理分类ID
    category_id_value = None
    if category_id and search_type.upper() in ["ARTICLE", "PHOTO"]:
        if isinstance(category_id, int):
            category_id_value = category_id
        else:
            try:
                if search_type.upper() == "ARTICLE":
                    category_enum = getattr(search.CategoryTypeArticle, category_id.upper())
                else:  # PHOTO
                    category_enum = getattr(search.CategoryTypePhoto, category_id.upper())
                category_id_value = category_enum.value
            except AttributeError:
                valid_categories = []
                if search_type.upper() == "ARTICLE":
                    valid_categories = [t.name for t in search.CategoryTypeArticle]
                else:  # PHOTO
                    valid_categories = [t.name for t in search.CategoryTypePhoto]
                    
                return {
                    "code": -1, 
                    "message": f"无效的分类ID: {category_id}",
                    "valid_categories": valid_categories
                }
    
    # 检查时间范围参数
    if time_start and time_end:
        try:
            # 简单验证日期格式
            if not (time_start.count('-') == 2 and time_end.count('-') == 2):
                return {"code": -1, "message": "时间格式错误，应为'YYYY-MM-DD'"}
        except Exception as e:
            return {"code": -1, "message": f"时间参数错误: {str(e)}"}
    
    try:
        # 调用bilibili_api的search_by_type方法
        result = await search.search_by_type(
            keyword,
            search_type=search_obj_type,
            order_type=order_enum,
            order_sort=order_sort,
            time_range=time_range,
            video_zone_type=zone_type,
            category_id=category_id_value,
            time_start=time_start,
            time_end=time_end,
            page=page,
            page_size=page_size
        )
        return result
    except Exception as e:
        return {"code": -1, "message": f"搜索失败: {str(e)}"}


@tool
async def get_default_search_keyword() -> dict:
    """
    获取bilibili默认的搜索内容。

    Returns:
        dict: 包含默认搜索内容的字典。
    """
    return await search.get_default_search_keyword()


@tool
async def get_hot_search_keywords() -> dict:
    """
    获取bilibili热搜

    Returns:
        dict: 包含热搜内容的字典。
    """
    return await search.get_hot_search_keywords()


@tool
async def get_suggest_keywords(keyword: str) -> list[str]:
    """
    通过一些文字输入获取bilibili搜索建议。类似搜索词的联想。

    Args:
        keyword (str): 搜索关键词

    Returns:
        list[str]: 包含搜索建议内容的列表。
    """
    return await search.get_suggest_keywords(keyword)


@tool
async def search_games(keyword: str) -> dict:
    """
    搜索bilibili游戏特用函数

    Args:
        keyword (str): 搜索关键词

    Returns:
        dict: 包含搜索结果的字典。
    """
    return await search.search_games(keyword)


@tool
async def search_mangasearch_manga(
    keyword: str, page_num: int = 1, page_size: int = 9, credential: Credential = None
) -> dict:
    """
    搜索bilibili漫画特用函数

    Args:
        keyword   (str): 搜索关键词

        page_num  (int): 页码. Defaults to 1.

        page_size (int): 每一页的数据大小. Defaults to 9.

        credential (Credential): 凭据类. Defaults to None.

    Returns:
        dict: 包含搜索结果的字典。
    """
    return await search.search_manga(keyword, page_num, page_size, credential)


@tool
async def search_cheese(
    keyword: str,
    page_num: int = 1,
    page_size: int = 30,
    order: search.OrderCheese = search.OrderCheese.RECOMMEND,
) -> dict:
    """
    搜索bilibili课程特用函数

    Args:
        keyword   (str)        : 搜索关键词

        page_num  (int)        : 页码. Defaults to 1.

        page_size (int)        : 每一页的数据大小. Defaults to 30.

        order     (OrderCheese): 排序方式. Defaults to OrderCheese.RECOMMEND
    """
    return await search.search_cheese(keyword, page_num, page_size, order)
