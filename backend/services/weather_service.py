import requests
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pypinyin import lazy_pinyin, Style
from config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL, OPENWEATHER_ONECALL_URL,OPENWEATHER_GEO_URL
from model_s.models import WeatherData, AirQualityData, ForecastItem

class WeatherService:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = OPENWEATHER_BASE_URL
        self.onecall_url = OPENWEATHER_ONECALL_URL
        self.geo_url = OPENWEATHER_GEO_URL
        self.cache = {}
        
        # 中文城市名到英文的映射
        self.city_name_mapping = {
            "北京": "Beijing",
            "上海": "Shanghai", 
            "广州": "Guangzhou",
            "深圳": "Shenzhen",
            "杭州": "Hangzhou",
            "南京": "Nanjing",
            "成都": "Chengdu",
            "重庆": "Chongqing",
            "天津": "Tianjin",
            "武汉": "Wuhan",
            "西安": "Xi'an",
            "苏州": "Suzhou",
            "青岛": "Qingdao",
            "郑州": "Zhengzhou",
            "大连": "Dalian",
            "宁波": "Ningbo",
            "厦门": "Xiamen",
            "济南": "Jinan",
            "沈阳": "Shenyang",
            "东莞": "Dongguan"        }
    
    def convert_city_name(self, city: str) -> str:
        """
        转换城市名称为英文或拼音
        优先使用预定义映射，否则使用拼音转换
        """
        # 首先检查预定义映射
        if city in self.city_name_mapping:
            return self.city_name_mapping[city]
        
        # 如果包含中文字符，转换为拼音
        if any('\u4e00' <= char <= '\u9fff' for char in city):
            # 转换为拼音，首字母大写
            pinyin_list = lazy_pinyin(city, style=Style.NORMAL)
            pinyin_name = ''.join(word.capitalize() for word in pinyin_list)
            return pinyin_name
          # 如果已经是英文，直接返回
        return city
        
    async def get_current_weather(self, city: str, country_code: Optional[str] = None) -> WeatherData:
        """根据城市名获取当前天气数据"""
        try:
            # 转换中文城市名为英文或拼音
            converted_city = self.convert_city_name(city)
            
            # 按城市名或 城市,国家 查询当前天气
            location = converted_city if not country_code else f"{converted_city},{country_code}"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "lang": "zh_cn"
            }
        
            # 调用天气API
            response = requests.get(f"{self.base_url}/weather", params=params)
            response.raise_for_status()
            data = response.json()
        
            # 提取经纬度信息
            coord = data.get("coord", {})
            lat = coord.get("lat")
            lon = coord.get("lon")
        
            # 转换为标准格式
            weather_data = WeatherData(
                city=data["name"],
                lat=lat,
                lon=lon,
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                pressure=data["main"]["pressure"],
                description=data["weather"][0]["description"],
                icon=data["weather"][0]["icon"],                wind_speed=data["wind"]["speed"],
                wind_direction=data["wind"]["deg"],
                visibility=data["visibility"],  # 默认10km能见度
                rain_1h=data.get("rain", {}).get("1h", 0.0),
                clouds_all=data.get("clouds", {}).get("all", 0),
                sunrise=datetime.fromtimestamp(data["sys"]["sunrise"], tz=timezone.utc),
                sunset=datetime.fromtimestamp(data["sys"]["sunset"], tz=timezone.utc),
                timestamp=datetime.now(tz=timezone.utc)
            )

            return weather_data
            
        except requests.RequestException as e:
            raise Exception(f"天气API调用失败: {str(e)}")
        except Exception as e:
            raise Exception(f"天气数据处理失败: {str(e)}")
    
    async def get_air_quality(self, lat: float, lon: float) -> AirQualityData:
        """获取空气质量数据"""
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key
            }
            response = requests.get(f"{self.base_url}/air_pollution", params=params)
            response.raise_for_status()
            data = response.json()
            components = data["list"][0]["components"]
            # 提取顶层坐标和数据时间戳
            coord = data.get("coord", {})
            lon0 = coord.get("lon") if coord else None
            lat0 = coord.get("lat") if coord else None
            dt = data["list"][0].get("dt")
            timestamp = datetime.fromtimestamp(dt, tz=timezone.utc) if dt else None
            air_quality = AirQualityData(
                aqi=int(data["list"][0]["main"]["aqi"]),
                co=components["co"],
                no=components["no"],
                no2=components["no2"],
                o3=components["o3"],
                so2=components["so2"],
                pm2_5=components["pm2_5"],
                pm10=components["pm10"],
                nh3=components["nh3"],
                timestamp=timestamp,
                lat=lat0,
                lon=lon0
            )
            return air_quality
            
        except Exception as e:
            raise Exception(f"空气质量数据获取失败: {str(e)}")
    
    async def get_coordinates(self, city: str) -> tuple:
        """获取城市坐标"""
        try:
            # 转换中文城市名为英文或拼音
            converted_city = self.convert_city_name(city)
            
            params = {
                "q": converted_city,
                "limit": 1,
                "appid": self.api_key
            }
            
            response = requests.get(f"{self.geo_url}/direct", params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise Exception("未找到该城市")
                
            return data[0]["lat"], data[0]["lon"]
            
        except Exception as e:
            raise Exception(f"坐标获取失败: {str(e)}")
    
    async def get_forecast(self, city: str, days: int = 5) -> list[ForecastItem]:
        """获取天气预报"""
        try:
            # 转换中文城市名为英文或拼音
            converted_city = self.convert_city_name(city)
            
            params = {
                "q": converted_city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "zh_cn"
            }
            
            response = requests.get(f"{self.base_url}/forecast", params=params)
            response.raise_for_status()
            data = response.json()
            
            forecasts = []
            for item in data["list"][:days * 8]:  # 每天8个时段
                forecast = ForecastItem(
                    datetime=datetime.fromtimestamp(item["dt"], tz=timezone.utc),
                    temperature=item["main"]["temp"],
                    feels_like=item["main"]["feels_like"],
                    humidity=item["main"]["humidity"],
                    description=item["weather"][0]["description"],
                    icon=item["weather"][0]["icon"],
                    pop=item.get("pop", 0) * 100,  # 转换为百分比
                    clouds_all=item.get("clouds", {}).get("all", 0),
                    wind_speed=item.get("wind", {}).get("speed", 0.0),
                    wind_direction=item.get("wind", {}).get("deg", 0),
                    wind_gust=item.get("wind", {}).get("gust"),
                    visibility=item.get("visibility", 0)
                )
                forecasts.append(forecast)
            
            return forecasts
            
        except Exception as e:
            raise Exception(f"天气预报获取失败: {str(e)}")
    

# 全局服务实例
weather_service = WeatherService()
