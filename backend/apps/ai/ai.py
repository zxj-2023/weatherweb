from fastapi import APIRouter, HTTPException
from model_s.models import ChatRequest, ChatResponse, WeatherContext
from services.ai_service import weather_ai_service
from services.weather_service import weather_service
from datetime import datetime
from typing import Optional

ai_router = APIRouter()

@ai_router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """AI聊天接口：根据天气情况提供智能建议"""
    try:
        # 尝试从已存储的JSON数据中获取天气信息
        stored_weather_data = weather_ai_service.load_weather_data(request.city)
        
        if stored_weather_data:
            # 如果找到已存储的天气数据，使用它构建天气上下文
            weather_data = stored_weather_data["weather_data"]
            air_quality = stored_weather_data["air_quality"]
            
            # 构建天气上下文
            current_time = datetime.now()
            # 处理时间字符串转换回datetime对象
            sunrise = datetime.fromisoformat(weather_data["sunrise"]) if isinstance(weather_data["sunrise"], str) else weather_data["sunrise"]
            sunset = datetime.fromisoformat(weather_data["sunset"]) if isinstance(weather_data["sunset"], str) else weather_data["sunset"]
            
            # 移除时区信息进行比较
            if hasattr(sunrise, 'tzinfo') and sunrise.tzinfo:
                sunrise = sunrise.replace(tzinfo=None)
            if hasattr(sunset, 'tzinfo') and sunset.tzinfo:
                sunset = sunset.replace(tzinfo=None)
                
            is_day = sunrise <= current_time <= sunset
            
            weather_context = WeatherContext(
                city=weather_data["city"],
                temperature=weather_data["temperature"],
                feels_like=weather_data["feels_like"],
                humidity=weather_data["humidity"],
                weather_description=weather_data["description"],
                wind_speed=weather_data["wind_speed"],
                visibility=weather_data["visibility"],
                aqi=air_quality["aqi"],
                rain_probability=0,  # 当前天气没有降水概率
                is_day=is_day
            )
            
            # 生成AI建议
            ai_response = weather_ai_service.generate_weather_suggestions(
                weather_context=weather_context,
                user_message=request.message
            )
            
            return ai_response
        else:
            # 创建一个简单的响应，告知用户需要先获取天气数据
            return ChatResponse(
                response="我需要先了解当前的天气情况才能回答您的问题。请先点击刷新按钮获取最新天气数据，然后再与我聊天。",
                suggestions=["点击刷新按钮获取天气数据", "您可以询问天气相关的问题", "例如：今天需要带伞吗？"],
                weather_context=None
            )
    except Exception as e:
        print(f"AI聊天错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI服务暂时不可用: {str(e)}")

@ai_router.post("/suggestions/{city}")
async def get_weather_suggestions(city: str, message: Optional[str] = None):
    """快速获取天气建议（可选用户输入）"""
    try:
        # 获取当前天气数据
        weather_data = await weather_service.get_current_weather(city)
        air_quality = await weather_service.get_air_quality(weather_data.lat, weather_data.lon)
        
        # 将天气数据转换为可序列化的字典
        weather_data_dict = weather_data.dict()
        air_quality_dict = air_quality.dict()
        
        # 处理datetime对象，转换为ISO格式字符串
        for key, value in weather_data_dict.items():
            if isinstance(value, datetime):
                weather_data_dict[key] = value.isoformat()
                
        for key, value in air_quality_dict.items():
            if isinstance(value, datetime):
                air_quality_dict[key] = value.isoformat()
        
        # 保存天气数据到JSON文件
        weather_ai_service.save_weather_data(city, weather_data_dict, air_quality_dict)
        
        # 构建天气上下文
        current_time = datetime.now()
        sunrise = weather_data.sunrise.replace(tzinfo=None)
        sunset = weather_data.sunset.replace(tzinfo=None)
        is_day = sunrise <= current_time <= sunset
        
        weather_context = WeatherContext(
            city=weather_data.city,
            temperature=weather_data.temperature,
            feels_like=weather_data.feels_like,
            humidity=weather_data.humidity,
            weather_description=weather_data.description,
            wind_speed=weather_data.wind_speed,
            visibility=weather_data.visibility,
            aqi=air_quality.aqi,
            rain_probability=0,  # 当前天气没有降水概率，可以从预报获取
            is_day=is_day
        )
        
        # 生成AI建议
        ai_response = weather_ai_service.generate_weather_suggestions(
            weather_context=weather_context,
            user_message=message
        )
        
        return ai_response
        
    except Exception as e:
        print(f"获取天气建议错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"天气建议服务暂时不可用: {str(e)}")

