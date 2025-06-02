// weather.js
// 与后端 API 交互获取数据

/** 获取当前天气 */
async function fetchCurrentWeather(city) {
    showLoading();
    try {
        const res = await fetch(`${API_BASE_URL}/weather/current`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city })
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            console.error('后端错误：', err);
            throw new Error(err.detail || '获取当前天气失败');
        }
        return await res.json();
    } finally {
        hideLoading();
    }
}

/** 获取天气预报 */
async function fetchForecast(city) {
    showLoading();
    try {
        const res = await fetch(`${API_BASE_URL}/weather/forecast`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city })
        });
        if (!res.ok) throw new Error('获取天气预报失败');
        const data = await res.json();
        return data.forecast;
    } finally {
        hideLoading();
    }
}

/** 获取用户偏好 */
async function fetchPreferences() {
    const res = await fetch(`${API_BASE_URL}/preferences`);
    if (!res.ok) throw new Error('获取用户偏好失败');
    return await res.json();
}

/** 保存用户偏好 */
async function savePreferences(prefs) {
    const res = await fetch(`${API_BASE_URL}/preferences`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(prefs)
    });
    if (!res.ok) throw new Error('保存偏好失败');
    return await res.json();
}

/** 获取天气提醒 */
async function fetchAlerts(city) {
    const res = await fetch(`${API_BASE_URL}/alerts/${city}`);
    if (!res.ok) throw new Error('获取提醒失败');
    const data = await res.json();
    return data.alerts;
}
