from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from typing import List, Optional, Dict
import json
import uuid
from datetime import datetime
from pathlib import Path
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, OPENAI_MAX_TOKENS
from model_s.models import WeatherContext, ChatResponse, SimpleMessageRequest, SimpleMessageResponse
from langchain_core.messages import SystemMessage, HumanMessage

class WeatherAIService:
    def __init__(self):
        # 使用LangChain初始化通义千问模型
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
            model=OPENAI_MODEL,
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=0.7
        )
        
        # 构建提示词模板
        self.chat_template = self._build_chat_template()
        
        # 简单聊天会话存储
        self.simple_chat_sessions: Dict[str, List[Dict]] = {}
        self.max_session_length = 20  # 最大会话长度
    
    def generate_weather_suggestions(self, weather_context: WeatherContext, user_message: Optional[str] = None) -> ChatResponse:
        """根据天气情况生成AI建议"""
        try:
            # 构建消息
            messages = self._build_messages(weather_context, user_message)
            
            # 调用通义千问模型
            response = self.llm.invoke(messages)
            ai_response = response.content
            
            # 解析响应
            suggestions = self._extract_suggestions(ai_response)
            
            return ChatResponse(
                response=ai_response,
                suggestions=suggestions,
                weather_context=weather_context.dict()
            )
            
        except Exception as e:
            print(f"AI服务调用失败: {str(e)}")
            # 降级处理：返回基础建议
            return self._get_fallback_suggestions(weather_context)
    
    def _build_chat_template(self) -> ChatPromptTemplate:
        """构建LangChain聊天模板"""
        system_template = """你是一个智能天气助手，专门为用户提供基于当前天气条件的实用建议。

你的职责：
1. 分析当前天气数据（温度、湿度、风速、能见度、空气质量等）
2. 根据天气情况提供实用的生活建议
3. 建议应该包括：穿衣、出行、健康、活动等方面
4. 保持友好、专业的语调
5. 建议要具体、可操作

回复格式要求：
- 以自然对话的方式回复
- 在回复末尾用【建议】标签列出3-5条具体建议
- 每条建议用一行表示，前面加上"• "

示例：
今天北京的天气不错呢！气温适中，空气质量也还可以。

【建议】
• 适合穿轻薄外套，早晚可能稍凉
• 是个不错的户外活动天气，可以考虑散步或运动
• 空气质量一般，敏感人群外出建议戴口罩"""

        human_template = """当前{city}的天气情况：
- 温度：{temperature}°C（体感温度：{feels_like}°C）
- 天气：{weather_description}
- 湿度：{humidity}%
- 风速：{wind_speed} m/s
- 能见度：{visibility_km} km
- 空气质量指数：{aqi}
- 降水概率：{rain_probability}%
- 时间：{time_period}

{user_input}

请根据以上天气情况{request_type}。"""

        return ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", human_template)
        ])
    
    def _build_messages(self, weather_context: WeatherContext, user_message: Optional[str]):
        """构建聊天消息"""
        # 准备模板变量
        template_vars = {
            "city": weather_context.city,
            "temperature": weather_context.temperature,
            "feels_like": weather_context.feels_like,
            "weather_description": weather_context.weather_description,
            "humidity": weather_context.humidity,
            "wind_speed": weather_context.wind_speed,
            "visibility_km": f"{weather_context.visibility/1000:.1f}",
            "aqi": weather_context.aqi,
            "rain_probability": weather_context.rain_probability or 0,
            "time_period": '白天' if weather_context.is_day else '夜晚'
        }
        
        if user_message:
            template_vars["user_input"] = f"用户问题：{user_message}"
            template_vars["request_type"] = "回答用户问题并提供相关建议"
        else:
            template_vars["user_input"] = ""
            template_vars["request_type"] = "提供今日生活建议"
        
        # 使用模板生成消息
        return self.chat_template.format_messages(**template_vars)
    
    def _extract_suggestions(self, ai_response: str) -> List[str]:
        """从AI响应中提取建议列表"""
        suggestions = []
        lines = ai_response.split('\n')
        
        # 查找【建议】部分
        in_suggestions = False
        for line in lines:
            line = line.strip()
            if '【建议】' in line:
                in_suggestions = True
                continue
            
            if in_suggestions and line:
                # 移除前缀符号
                if line.startswith('• '):
                    suggestions.append(line[2:])
                elif line.startswith('- '):
                    suggestions.append(line[2:])
                elif line.startswith('* '):
                    suggestions.append(line[2:])
                elif line and not line.startswith('【'):
                    suggestions.append(line)
        
        return suggestions[:5]  # 最多返回5条建议
    

    # 存储天气数据的函数
    def save_weather_data(self, city: str, weather_data: Dict, air_quality: Dict):
        """将天气数据以JSON格式存储到文件中"""
        try:
            # 定义天气数据存储路径
            WEATHER_DATA_DIR = Path("data/weather")
            WEATHER_DATA_FILE = WEATHER_DATA_DIR / "weather_data.json"

            # 确保数据目录存在
            WEATHER_DATA_DIR.mkdir(parents=True, exist_ok=True)
            # 准备存储数据
            data_to_save = {
                "timestamp": datetime.now().isoformat(),
                "city": city,
                "weather_data": weather_data,
                "air_quality": air_quality
            }
            
            # 删除现有文件（如果存在）
            if WEATHER_DATA_FILE.exists():
                WEATHER_DATA_FILE.unlink()
            
            # 创建新的数据列表
            new_data = [data_to_save]
            
            # 保存数据
            with open(WEATHER_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
                
            print(f"已保存{city}的天气数据")
            return True
        except Exception as e:
            print(f"保存天气数据失败: {str(e)}")
            return False
    
    # 读取已存储的天气数据
    def load_weather_data(self, city: str) -> Optional[Dict]:
        """从文件中读取指定城市的最新天气数据"""
        try:
            # 定义天气数据存储路径
            WEATHER_DATA_DIR = Path("data/weather")
            WEATHER_DATA_FILE = WEATHER_DATA_DIR / "weather_data.json"
            
            # 检查文件是否存在
            if not WEATHER_DATA_FILE.exists():
                print(f"天气数据文件不存在")
                return None
                
            # 读取数据
            with open(WEATHER_DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    all_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"天气数据文件格式错误")
                    return None
            
            # 查找指定城市的最新数据
            city_data = [item for item in all_data if item["city"].lower() == city.lower()]
            if not city_data:
                print(f"未找到{city}的天气数据")
                return None
                
            # 返回最新的数据（列表中的最后一项）
            latest_data = city_data[-1]
            print(f"已加载{city}的天气数据，时间戳: {latest_data['timestamp']}")
            return latest_data
        except Exception as e:
            print(f"读取天气数据失败: {str(e)}")
            return None

# 创建全局实例
weather_ai_service = WeatherAIService()
