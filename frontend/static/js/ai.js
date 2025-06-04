// ai.js
// AI聊天功能模块

// AI聊天相关的API调用函数
async function fetchAISuggestions(city) {
    try {

        const response = await fetch(`${API_BASE_URL}/ai/suggestions/${encodeURIComponent(city)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`AI服务错误: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('获取AI建议失败:', error);
        throw error;
    } finally {

    }
}

async function sendChatMessage(city, message) {
    try {
        const response = await fetch(`${API_BASE_URL}/ai/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                city: city,
                message: message
            })
        });

        if (!response.ok) {
            throw new Error(`AI聊天错误: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('AI聊天失败:', error);
        throw error;
    } finally {

    }
}

// 渲染AI响应
function renderAIResponse(data) {
    // 更新AI响应内容
    if (aiResponse) {
        aiResponse.innerHTML = `
            <div class="ai-message">
                ${data.response}
            </div>
        `;
    }

    // 渲染建议列表
    if (suggestionsList && data.suggestions && data.suggestions.length > 0) {
        suggestionsList.innerHTML = '';
        data.suggestions.forEach(suggestion => {
            const suggestionDiv = document.createElement('div');
            suggestionDiv.className = 'suggestion-item';
            suggestionDiv.textContent = suggestion;
            suggestionsList.appendChild(suggestionDiv);
        });
    }
}

// 显示加载状态
function showAILoading() {
    if (aiResponse) {
        aiResponse.innerHTML = '<div class="loading-message">AI正在思考中...</div>';
    }
    if (suggestionsList) {
        suggestionsList.innerHTML = '';
    }
}

// 显示错误状态
function showAIError(error) {
    if (aiResponse) {
        aiResponse.innerHTML = `
            <div class="ai-message error">
                <i class="fas fa-exclamation-triangle"></i>
                抱歉，AI助手暂时无法提供建议。<br>
                <small>错误信息: ${error.message}</small>
            </div>
        `;
    }
    if (suggestionsList) {
        suggestionsList.innerHTML = '';
    }
}

// 加载AI建议
async function loadAISuggestions(city) {
    try {
        showAILoading();
        const data = await fetchAISuggestions(city);
        renderAIResponse(data);
    } catch (error) {
        showAIError(error);
    }
}

// 发送用户消息
async function handleSendMessage() {
    const message = userMessageInput?.value?.trim();
    if (!message || !currentCity) return;

    try {
        // 禁用发送按钮
        if (sendMessageBtn) {
            sendMessageBtn.disabled = true;
        }

        showAILoading();
        const data = await sendChatMessage(currentCity, message);
        renderAIResponse(data);

        // 清空输入框
        if (userMessageInput) {
            userMessageInput.value = '';
        }
    } catch (error) {
        showAIError(error);
    } finally {
        // 重新启用发送按钮
        if (sendMessageBtn) {
            sendMessageBtn.disabled = false;
        }
    }
}

// 初始化AI聊天事件监听器
function initAIChatEvents() {
    // 发送消息按钮
    if (sendMessageBtn) {
        sendMessageBtn.addEventListener('click', handleSendMessage);
    }

    // 输入框回车发送
    if (userMessageInput) {
        userMessageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleSendMessage();
            }
        });
    }

    // 刷新AI建议按钮
    if (refreshAiBtn) {
        refreshAiBtn.addEventListener('click', () => {
            if (currentCity) {
                loadAISuggestions(currentCity);
            }
        });
    }
}

// 导出函数供其他模块使用
window.loadAISuggestions = loadAISuggestions;
window.initAIChatEvents = initAIChatEvents;
