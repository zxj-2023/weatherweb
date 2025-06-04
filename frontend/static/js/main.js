// main.js
// 主入口：渲染城市标签、加载并展示天气数据、绑定交互事件

document.addEventListener('DOMContentLoaded', init);

async function init() {
    try {
        // 加载用户偏好并设置全局状态
        userPreferences = await fetchPreferences();
        favoriteCities = userPreferences.favorite_cities || [];
        currentCity = userPreferences.default_location || currentCity;
        defaultCityInput.value = currentCity;

        renderCityTabs();
        await loadAndRender(currentCity);

        // 初始化AI聊天事件
        initAIChatEvents();

        // 绑定刷新按钮
        refreshBtn.addEventListener('click', () => loadAndRender(currentCity));
    } catch (err) {
        console.error('初始化失败', err);
    }
}

/** 渲染收藏城市标签 */
function renderCityTabs() {
    cityTabs.innerHTML = '';
    favoriteCities.forEach(city => {
        const tab = document.createElement('div');
        tab.className = 'city-tab' + (city === currentCity ? ' active' : '');
        tab.textContent = city;
        tab.addEventListener('click', async () => {
            currentCity = city;
            setActiveTab();
            await loadAndRender(city);
        });
        cityTabs.appendChild(tab);
    });
}

/** 设置活动标签样式 */
function setActiveTab() {
    const tabs = document.querySelectorAll('.city-tab');
    tabs.forEach(tab => {
        tab.classList.toggle('active', tab.textContent === currentCity);
    });
}

/** 添加收藏城市到服务器 */
async function addFavorite(city) {
    try {
        await fetch(`${API_BASE_URL}/favorites/${encodeURIComponent(city)}`, { method: 'POST' });
    } catch (err) {
        console.error('添加收藏失败', err);
    }
}

/** 加载并渲染指定城市的所有数据 */
async function loadAndRender(city) {
    try {
        // 当前天气 + 空气质量 + 提醒
        const data = await fetchCurrentWeather(city); renderCurrent(data.weather);

        renderAirQuality(data.air_quality);
        renderSunTimes(data.weather);
        renderVisibility(data.weather);
        renderAlerts(data.alerts);

        // 天气预报
        const forecast = await fetchForecast(city);
        renderForecast(forecast);
        
        // 加载AI建议
        loadAISuggestions(city);
    } catch (err) {
        console.error('加载数据失败', err);
    }
}

/** 渲染当前天气 */
function renderCurrent(weather) {
    setText(currentLocation, weather.city);
    setText(currentDateTime, formatDateTime(new Date()));
    weatherIcon.className = getWeatherIconClass(weather.icon);
    setText(currentTemp, weather.temperature);
    setText(weatherDesc, weather.description);
    setText(feelsLike, `${weather.feels_like}°C`);
    setText(humidity, `${weather.humidity}%`);
    setText(windSpeed, `${weather.wind_speed} m/s`);
    setText(pressure, `${weather.pressure} hPa`);
}

/** 渲染空气质量 */
function renderAirQuality(air) {
    setText(aqiValue, air.aqi);
    const info = getAqiInfo(air.aqi);
    setText(aqiLevel, info.level);
    aqiLevel.className = `aqi-level ${info.className}`;
    setText(pm25, `${air.pm2_5} μg/m³`);
    setText(pm10, `${air.pm10} μg/m³`);
}

/** 渲染日出日落 */
function renderSunTimes(weather) {
    const sr = new Date(weather.sunrise);
    const ss = new Date(weather.sunset);
    setText(sunrise, sr.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }));
    setText(sunset, ss.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }));
}

/** 渲染能见度 */
function renderVisibility(weather) {
    // 确保 visibility 是一个有效的数字
    const visibilityValue = parseFloat(weather.visibility);
    if (!isNaN(visibilityValue) && visibilityValue > 0) {
        const km = (visibilityValue / 1000).toFixed(1);
        setText(visibility, `${km} km`);
    } else {
        setText(visibility, '--');
    }
}

/** 渲染智能提醒 */
function renderAlerts(alerts) {
    if (alerts && alerts.length > 0) {
        toggleElement(reminderCard, true);
        reminderContent.innerHTML = '';
        alerts.forEach(alert => {
            const p = document.createElement('p');
            p.textContent = alert.message;
            reminderContent.appendChild(p);
        });
    } else {
        toggleElement(reminderCard, false);
    }
}

/** 渲染预报数据 */
function renderForecast(forecast) {
    // 24小时预报（取前8条，每3小时一条）
    hourlyForecast.innerHTML = '';
    const hours = forecast.slice(0, 8);
    hours.forEach(item => {
        const div = document.createElement('div');
        div.className = 'hour-item';
        const dt = new Date(item.datetime);
        div.innerHTML = `
            <div class="time">${dt.getHours()}:00</div>
            <div class="icon"><i class="${getWeatherIconClass(item.icon)}"></i></div>
            <div class="temp">${item.temperature}°C</div>
        `;
        hourlyForecast.appendChild(div);
    });

    // 7天预报（取每天第一个时段）
    dailyForecast.innerHTML = '';
    const days = forecast.filter((_, i) => i % 8 === 0);
    days.forEach(item => {
        const div = document.createElement('div');
        div.className = 'day-item';
        const dt = new Date(item.datetime);
        div.innerHTML = `
            <div class="date">${dt.getMonth() + 1}/${dt.getDate()}</div>
            <div class="icon"><i class="${getWeatherIconClass(item.icon)}"></i></div>
            <div class="temp">${item.temperature}°C</div>
        `;
        dailyForecast.appendChild(div);
    });
}

// 搜索并添加城市
searchBtn.addEventListener('click', async () => {
    const city = cityInput.value.trim();
    if (!city) return;
    if (!favoriteCities.includes(city)) {
        favoriteCities.push(city);
        await addFavorite(city);
        renderCityTabs();
    }
    currentCity = city;
    setActiveTab();
    await loadAndRender(city);
    cityInput.value = '';
});

/** 加载AI建议 */
async function loadAISuggestions(city) {
    try {
        const aiData = await fetchAISuggestions(city);
        renderAIResponse(aiData);
    } catch (error) {
        console.error('加载AI建议失败:', error);
        showAIError('AI服务暂时不可用，请稍后再试。');
    }
}
