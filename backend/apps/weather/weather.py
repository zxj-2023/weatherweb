from fastapi import APIRouter,HTTPException

from model_s.models import WeatherRequest
from services.weather_service import weather_service
from services.user_service import reminder_service

weather=APIRouter()

@weather.post("/current")
async def get_current_weather(request: WeatherRequest):
    """根据城市获取当前天气信息"""
    try:
        weather_data = await weather_service.get_current_weather(
            request.city, 
            request.country_code
        )
        
        air_quality_lat = weather_data.lat
        air_quality_lon = weather_data.lon
        
        air_quality = await weather_service.get_air_quality(air_quality_lat, air_quality_lon)
        
        # 构建完整的天气数据
        complete_data = {
            "weather": weather_data,
            "air_quality": air_quality,
            "coordinates": {"lat": air_quality_lat, "lon": air_quality_lon} # Use the same lat/lon
        }
          # 检查提醒
        alert_data = {
            "temperature": weather_data.temperature,
            "humidity": weather_data.humidity,
            "aqi": air_quality.aqi,
            "pop": 0,  # 当前天气没有降水概率，需要从预报获取
        }
        
        alerts = reminder_service.check_alerts(alert_data)
        complete_data["alerts"] = [alert for alert in alerts]
        
        return complete_data
        
    except Exception as e:
        # 记录更详细的错误信息，便于调试
        print(f"Error in get_current_weather for city {request.city}: {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@weather.post("/forecast")
async def get_weather_forecast(request: WeatherRequest):
    """获取天气预报"""
    try:
        forecast = await weather_service.get_forecast(request.city, days=5)
        return {"forecast": [item.dict() for item in forecast]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))