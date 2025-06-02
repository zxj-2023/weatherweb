from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WeatherRequest(BaseModel):
    city: str
    country_code: Optional[str] = None

class WeatherData(BaseModel):
    city: str  # 城市名称
    lat: float  # 纬度
    lon: float  # 经度
    visibility:int
    temperature: float  # 温度 (°C)
    feels_like: float  # 体感温度 (°C)
    humidity: int  # 湿度 (%)
    pressure: int  # 气压 (hPa)
    description: str  # 天气描述
    icon: str  # 天气图标代码
    wind_speed: float  # 风速 (m/s)
    wind_direction: int  # 风向 (度)    visibility: int  # 能见度 (米)
    rain_1h: Optional[float] = None  # 最近1小时降雨量 (mm)
    clouds_all: Optional[int] = None  # 云量 (%)
    sunrise: datetime  # 日出时间 (UTC)
    sunset: datetime  # 日落时间 (UTC)
    timestamp: datetime  # 数据时间戳 (UTC)

class AirQualityData(BaseModel):
    aqi: int  # 空气质量指数
    co: float  # 一氧化碳 µg/m³
    no: float  # 一氧化氮 µg/m³
    no2: float  # 二氧化氮 µg/m³
    o3: float  # 臭氧 µg/m³
    so2: float  # 二氧化硫 µg/m³
    pm2_5: float  # PM2.5 µg/m³
    pm10: float  # PM10 µg/m³
    nh3: float  # 氨 µg/m³
    timestamp: datetime  # 数据时间戳 (UTC)
    lat: float  # 纬度
    lon: float  # 经度

class ForecastItem(BaseModel):
    datetime: datetime  # 预报的时间戳
    temperature: float  # 温度 (°C)
    feels_like: float  # 体感温度 (°C)
    humidity: int  # 湿度 (%)
    description: str  # 天气描述
    icon: str  # 天气图标代码
    pop: float  # 降水概率 (%)
    clouds_all: int  # 云量 (%)
    wind_speed: float  # 风速 (m/s)
    wind_direction: int  # 风向 (度)
    wind_gust: Optional[float] = None  # 阵风 (m/s)
    visibility: int  # 能见度 (米)

class UserPreferences(BaseModel):
    default_location: str
    favorite_cities: List[str] = []
    reminder_rules: List[dict] = []
    temperature_unit: str = "celsius"
    
class ReminderRule(BaseModel):
    id: str
    name: str
    condition: str
    message: str
    active: bool = True

class AlertResponse(BaseModel):
    type: str
    message: str
    severity: str  # low, medium, high
