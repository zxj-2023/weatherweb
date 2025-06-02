from fastapi import APIRouter,HTTPException

from services.user_service import prefs_service, reminder_service
from services.weather_service import weather_service

from model_s.models import UserPreferences

user=APIRouter()

@user.get("/preferences")
async def get_user_preferences():
    """获取用户偏好设置"""
    try:
        prefs = prefs_service.load_preferences()
        return prefs.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user.post("/preferences")
async def update_user_preferences(preferences: UserPreferences):
    """更新用户偏好设置"""
    try:
        success = prefs_service.save_preferences(preferences)
        if success:
            return {"message": "偏好设置已保存"}
        else:
            raise HTTPException(status_code=500, detail="保存失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user.post("/favorites/{city}")
async def add_favorite_city(city: str):
    """添加收藏城市"""
    try:
        success = prefs_service.add_favorite_city(city)
        if success:
            return {"message": f"已添加 {city} 到收藏"}
        else:
            raise HTTPException(status_code=500, detail="添加失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user.delete("/favorites/{city}")
async def remove_favorite_city(city: str):
    """移除收藏城市"""
    try:
        success = prefs_service.remove_favorite_city(city)
        if success:
            return {"message": f"已从收藏中移除 {city}"}
        else:
            raise HTTPException(status_code=500, detail="移除失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user.get("alerts/{city}")
async def get_weather_alerts(city: str):
    """获取特定城市的天气提醒"""
    try:
        # 获取天气数据
        weather_data = await weather_service.get_current_weather(city)
        lat, lon = await weather_service.get_coordinates(city)
        air_quality = await weather_service.get_air_quality(lat, lon)
          # 检查提醒
        alert_data = {
            "temperature": weather_data.temperature,
            "humidity": weather_data.humidity,
            "aqi": air_quality.aqi,
            "pop": 0,
        }
        
        alerts = reminder_service.check_alerts(alert_data)
        return {"alerts": [alert.dict() for alert in alerts]}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
