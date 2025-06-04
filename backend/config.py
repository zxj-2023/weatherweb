import os
from dotenv import load_dotenv

load_dotenv()

# API配置
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"
OPENWEATHER_ONECALL_URL = "http://api.openweathermap.org/data/3.0/onecall"
OPENWEATHER_GEO_URL = "http://api.openweathermap.org/geo/1.0"

# AI聊天配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "qwen-max")
OPENAI_MAX_TOKENS = 500

# 应用配置
APP_HOST = "127.0.0.1"
APP_PORT = 8000
APP_DEBUG = True

# CORS配置
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",  # 新增：后端自身地址
    "http://127.0.0.1:8000",  # 新增：后端自身地址
    "file://"  # 支持本地HTML文件
]

# 数据存储
USER_PREFS_FILE = "user_preferences.json"
WEATHER_CACHE_TTL = 1800  # 缓存30分钟
