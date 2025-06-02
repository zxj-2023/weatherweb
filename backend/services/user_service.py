import json
import os
from typing import Dict, Any, List
from model_s.models import UserPreferences, ReminderRule, AlertResponse
from config import USER_PREFS_FILE

class UserPreferencesService:
    def __init__(self):
        self.prefs_file = USER_PREFS_FILE
        self.default_prefs = {
            "default_location": "北京",
            "favorite_cities": ["北京", "上海", "广州", "深圳"],
            "reminder_rules": [
                {
                    "id": "rain_alert",
                    "name": "降雨提醒",
                    "condition": "pop > 60",
                    "message": "今天可能下雨，记得带伞！",
                    "active": True
                },
                {
                    "id": "cold_alert", 
                    "name": "低温提醒",
                    "condition": "temperature < 5",
                    "message": "气温较低，注意保暖！",
                    "active": True
                },
                {
                    "id": "hot_alert",
                    "name": "高温提醒", 
                    "condition": "temperature > 35",
                    "message": "气温很高，注意防暑降温！",
                    "active": True
                },
                {
                    "id": "air_quality_alert",
                    "name": "空气质量提醒",
                    "condition": "aqi > 150",
                    "message": "空气质量较差，建议减少外出！",
                    "active": True
                }
            ],
            "temperature_unit": "celsius"
        }
    
    def load_preferences(self) -> UserPreferences:
        """加载用户偏好设置"""
        try:
            if os.path.exists(self.prefs_file):
                with open(self.prefs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserPreferences(**data)
            else:
                # 创建默认设置
                self.save_preferences(UserPreferences(**self.default_prefs))
                return UserPreferences(**self.default_prefs)
        except Exception as e:
            print(f"加载用户偏好失败: {e}")
            return UserPreferences(**self.default_prefs)
    
    def save_preferences(self, preferences: UserPreferences) -> bool:
        """保存用户偏好设置"""
        try:
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                json.dump(preferences.dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存用户偏好失败: {e}")
            return False
    
    def add_favorite_city(self, city: str) -> bool:
        """添加收藏城市"""
        try:
            prefs = self.load_preferences()
            if city not in prefs.favorite_cities:
                prefs.favorite_cities.append(city)
                return self.save_preferences(prefs)
            return True
        except Exception as e:
            print(f"添加收藏城市失败: {e}")
            return False
    
    def remove_favorite_city(self, city: str) -> bool:
        """移除收藏城市"""
        try:
            prefs = self.load_preferences()
            if city in prefs.favorite_cities:
                prefs.favorite_cities.remove(city)
                return self.save_preferences(prefs)
            return True
        except Exception as e:
            print(f"移除收藏城市失败: {e}")
            return False

class ReminderService:
    def __init__(self, prefs_service: UserPreferencesService):
        self.prefs_service = prefs_service
    
    def check_alerts(self, weather_data: Dict[str, Any]) -> List[AlertResponse]:
        """检查并生成提醒"""
        prefs = self.prefs_service.load_preferences()
        alerts = []
        
        for rule in prefs.reminder_rules:
            if not rule.get("active", True):
                continue
                
            try:
                # 简单的条件评估
                condition = rule["condition"]
                if self._evaluate_condition(condition, weather_data):
                    alert = AlertResponse(
                        type=rule["id"],
                        message=rule["message"],
                        severity=self._get_severity(rule["id"], weather_data)
                    )
                    alerts.append(alert)
            except Exception as e:
                print(f"评估提醒条件失败 {rule['id']}: {e}")
        
        return alerts
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """评估提醒条件"""
        try:
            # 替换条件中的变量
            for key, value in data.items():
                condition = condition.replace(key, str(value))
            
            # 安全的条件评估
            allowed_names = {
                "__builtins__": {},
                "True": True,
                "False": False,
            }
            
            return eval(condition, allowed_names)
        except:
            return False
    def _get_severity(self, alert_type: str, data: Dict[str, Any]) -> str:
        """根据数据确定提醒严重程度"""
        severity_map = {
            "rain_alert": "medium",
            "cold_alert": "high" if data.get("temperature", 0) < 0 else "medium",
            "hot_alert": "high" if data.get("temperature", 0) > 40 else "medium", 
            "air_quality_alert": "high" if data.get("aqi", 0) > 200 else "medium"
        }
        
        return severity_map.get(alert_type, "low")

# 全局服务实例
prefs_service = UserPreferencesService()
reminder_service = ReminderService(prefs_service)
