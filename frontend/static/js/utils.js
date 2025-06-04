// API配置
const API_BASE_URL = 'http://localhost:8000/api'; // 根据后端地址修改

// DOM元素
const cityInput = document.getElementById('cityInput');
const searchBtn = document.getElementById('searchBtn');
const cityTabs = document.getElementById('cityTabs');
const currentLocation = document.getElementById('currentLocation');
const currentDateTime = document.getElementById('currentDateTime');
const weatherIcon = document.getElementById('weatherIcon');
const currentTemp = document.getElementById('currentTemp');
const weatherDesc = document.getElementById('weatherDesc');
const feelsLike = document.getElementById('feelsLike');
const humidity = document.getElementById('humidity');
const windSpeed = document.getElementById('windSpeed');
const pressure = document.getElementById('pressure');
const reminderCard = document.getElementById('reminderCard');
const reminderContent = document.getElementById('reminderContent');
const aqiValue = document.getElementById('aqiValue');
const aqiLevel = document.getElementById('aqiLevel');
const pm25 = document.getElementById('pm25');
const pm10 = document.getElementById('pm10');
const sunrise = document.getElementById('sunrise');
const sunset = document.getElementById('sunset');
const visibility = document.getElementById('visibility');
const hourlyForecast = document.getElementById('hourlyForecast');
const dailyForecast = document.getElementById('dailyForecast');
const loadingSpinner = document.getElementById('loadingSpinner');

// 设置弹窗元素
const settingsBtn = document.getElementById('settingsBtn');
const refreshBtn = document.getElementById('refreshBtn');
const settingsModal = document.getElementById('settingsModal');
const closeSettings = document.getElementById('closeSettings');
const defaultCityInput = document.getElementById('defaultCity');
const rainReminderCheckbox = document.getElementById('rainReminder');
const coldReminderCheckbox = document.getElementById('coldReminder');
const airReminderCheckbox = document.getElementById('airReminder');
const coldThresholdInput = document.getElementById('coldThreshold');
const rainThresholdInput = document.getElementById('rainThreshold');
const saveSettingsBtn = document.getElementById('saveSettings');
const cancelSettingsBtn = document.getElementById('cancelSettings');

// AI聊天元素
const aiResponse = document.getElementById('aiResponse');
const suggestionsList = document.getElementById('suggestionsList');
const userMessageInput = document.getElementById('userMessageInput');
const sendMessageBtn = document.getElementById('sendMessageBtn');
const refreshAiBtn = document.getElementById('refreshAiBtn');

// 全局状态
let currentCity = '北京'; // 默认城市
let favoriteCities = [];
let userPreferences = {};

// --- 辅助函数 ---

/**
 * 显示加载动画
 */
function showLoading() {
    if (loadingSpinner) loadingSpinner.style.display = 'flex';
}

/**
 * 隐藏加载动画
 */
function hideLoading() {
    if (loadingSpinner) loadingSpinner.style.display = 'none';
}

/**
 * 格式化日期时间
 * @param {Date} date - 日期对象
 * @returns {string} 格式化的日期时间字符串
 */
function formatDateTime(date) {
    const options = {
        year: 'numeric', month: 'long', day: 'numeric',
        hour: '2-digit', minute: '2-digit', weekday: 'long'
    };
    return date.toLocaleDateString('zh-CN', options);
}

/**
 * 根据天气代码获取图标类名
 * @param {string} weatherCode - 天气代码 (例如 OpenWeatherMap 的 icon id)
 * @param {boolean} isDay - 是否是白天
 * @returns {string} Font Awesome 图标类名
 */
function getWeatherIconClass(weatherCode, isDay = true) {
    // 示例映射，需要根据实际API调整
    const iconMap = {
        '01d': 'fas fa-sun', // clear sky day
        '01n': 'fas fa-moon', // clear sky night
        '02d': 'fas fa-cloud-sun', // few clouds day
        '02n': 'fas fa-cloud-moon', // few clouds night
        '03d': 'fas fa-cloud', // scattered clouds
        '03n': 'fas fa-cloud', // scattered clouds
        '04d': 'fas fa-cloud-meatball', // broken clouds
        '04n': 'fas fa-cloud-meatball', // broken clouds
        '09d': 'fas fa-cloud-showers-heavy', // shower rain
        '09n': 'fas fa-cloud-showers-heavy', // shower rain
        '10d': 'fas fa-cloud-sun-rain', // rain day
        '10n': 'fas fa-cloud-moon-rain', // rain night
        '11d': 'fas fa-poo-storm', // thunderstorm
        '11n': 'fas fa-poo-storm', // thunderstorm
        '13d': 'fas fa-snowflake', // snow
        '13n': 'fas fa-snowflake', // snow
        '50d': 'fas fa-smog', // mist
        '50n': 'fas fa-smog', // mist
    };
    return iconMap[weatherCode] || (isDay ? 'fas fa-question-circle' : 'fas fa-question-circle'); // 默认图标
}

/**
 * 根据AQI值获取等级和颜色
 * @param {number} aqi - AQI值
 * @returns {object} { level: string, className: string }
 */
function getAqiInfo(aqi) {
    if (aqi <= 50) return { level: '优', className: 'good' };
    if (aqi <= 100) return { level: '良', className: 'moderate' };
    if (aqi <= 150) return { level: '轻度污染', className: 'unhealthy-sensitive' };
    if (aqi <= 200) return { level: '中度污染', className: 'unhealthy' };
    if (aqi <= 300) return { level: '重度污染', className: 'very-unhealthy' };
    return { level: '严重污染', className: 'hazardous' };
}



/**
 * 安全地设置元素的textContent
 * @param {HTMLElement} element - DOM元素
 * @param {string|number} text - 要设置的文本
 * @param {string} defaultText - 默认文本
 */
function setText(element, text, defaultText = '--') {
    if (element) {
        element.textContent = (text !== undefined && text !== null && text !== '') ? text : defaultText;
    }
}

/**
 * 安全地设置元素的innerHTML
 * @param {HTMLElement} element - DOM元素
 * @param {string} html - 要设置的HTML
 * @param {string} defaultHtml - 默认HTML
 */
function setHtml(element, html, defaultHtml = '') {
    if (element) {
        element.innerHTML = html || defaultHtml;
    }
}

/**
 * 切换元素的显示/隐藏
 * @param {HTMLElement} element - DOM元素
 * @param {boolean} show - 是否显示
 */
function toggleElement(element, show) {
    if (element) {
        element.style.display = show ? '' : 'none';
    }
}
