// settings.js
// 设置弹窗控制与用户偏好加载/保存

/** 打开设置弹窗并加载当前偏好 */
async function openSettings() {
    try {
        const prefs = await fetchPreferences();
        // 默认城市
        defaultCityInput.value = prefs.default_location;
        // 收藏城市
        favoriteCities = prefs.favorite_cities;
        renderCityTabs();        // 提醒设置
        prefs.reminder_rules.forEach(rule => {
            switch (rule.id) {
                case 'rain_alert':
                    rainReminderCheckbox.checked = rule.active;
                    rainThresholdInput.value = (rule.condition.match(/\d+/) || [])[0] || rainThresholdInput.value;
                    break;
                case 'cold_alert':
                    coldReminderCheckbox.checked = rule.active;
                    coldThresholdInput.value = (rule.condition.match(/\d+/) || [])[0] || coldThresholdInput.value;
                    break;
                case 'air_quality_alert':
                    airReminderCheckbox.checked = rule.active;
                    break;
            }
        });
        // 弹窗显示
        settingsModal.style.display = 'flex';
    } catch (err) {
        console.error('加载设置失败', err);
    }
}

/** 关闭设置弹窗 */
function closeSettingsModal() {
    settingsModal.style.display = 'none';
}

// 事件绑定
settingsBtn.addEventListener('click', openSettings);
closeSettings.addEventListener('click', closeSettingsModal);
cancelSettingsBtn.addEventListener('click', closeSettingsModal);

/** 保存设置到后端并刷新 */
saveSettingsBtn.addEventListener('click', async () => {
    const newPrefs = {
        default_location: defaultCityInput.value || currentCity,
        favorite_cities: favoriteCities, reminder_rules: [
            { id: 'rain_alert', name: '降雨提醒', condition: `pop > ${rainThresholdInput.value}`, message: '今天可能下雨，记得带伞！', active: rainReminderCheckbox.checked },
            { id: 'cold_alert', name: '低温提醒', condition: `temperature < ${coldThresholdInput.value}`, message: '气温较低，注意保暖！', active: coldReminderCheckbox.checked },
            { id: 'air_quality_alert', name: '空气质量提醒', condition: 'aqi > 150', message: '空气质量较差，建议减少外出！', active: airReminderCheckbox.checked }
        ],
        temperature_unit: userPreferences.temperature_unit || 'celsius'
    };
    try {
        await savePreferences(newPrefs);
        userPreferences = newPrefs;
        closeSettingsModal();
        init();
    } catch (err) {
        console.error('保存设置失败', err);
    }
});

// 点击遮罩关闭弹窗
settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        closeSettingsModal();
    }
});

// 按ESC键关闭弹窗
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeSettingsModal();
    }
});
