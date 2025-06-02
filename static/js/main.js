document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('baziForm');
    const grid = document.getElementById("baziResultGrid");
    const aiAnalysisResultArea = document.getElementById('aiAnalysisResultArea');
    const aiButtonContainer = document.getElementById('aiButtonContainer');
    const submitBaziButton = document.getElementById('submitBaziButton');
    const aiButton = document.getElementById('aiButton');
    const aiButtonImage = document.getElementById('aiButtonImage');
    const feedbackForm = document.getElementById('feedbackForm');
    const clearUserDataButton = document.getElementById('clearUserDataButton');
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;


    // 提前定义 getRandomWuxing 函数
    const getRandomWuxing = () => {
        const wuxingElements = ["金", "木", "水", "火", "土"];
        const randomIndex = Math.floor(Math.random() * wuxingElements.length);
        return wuxingElements[randomIndex];
    };

    // 获取当前语言
    const getCurrentLanguage = () => {
        return document.documentElement.lang || 'zh';
    };

    // 翻译表
    const translations = {
        zh: {
            nameRequired: '姓名不能为空且长度不能超过50字符',
            locationRequired: '请输入出生地',
            invalidDate: '请输入有效的出生日期，且不能晚于今天',
            timeRequired: '请输入出生时间',
            serverError: '服务器错误: ',
            baziError: '排盘出错：',
            unableToParse: '无法解析排盘结果',
            requestFailed: '请求处理失败：',
            aiError: 'AI 服务器错误: ',
            aiNoContent: '暂无内容或分析出错。',
            aiRequestFailed: 'AI 分析请求失败：',
            project: '项目',
            yearPillar: '年柱',
            monthPillar: '月柱',
            dayPillar: '日柱',
            hourPillar: '时柱',
            heavenlyStemEarthlyBranch: '天干地支',
            hiddenStems: '藏干',
            zodiac: '生肖',
            constellation: '星座',
            fiveElementsCount: '五行个数',
            unableToCount: '无法统计',
            analyzingBazi: '八字分析中...',
            analyzingFiveElements: '五行分析中...',
            feedbackNameRequired: '请输入您的姓名',
            feedbackEmailRequired: '请输入有效的邮箱地址',
            feedbackMessageRequired: '请输入反馈内容',
            feedbackSuccess: '感谢您的反馈！',
            feedbackError: '提交反馈失败：'
        },
        en: {
            nameRequired: 'Name cannot be empty and must not exceed 50 characters',
            locationRequired: 'Please enter your birthplace',
            invalidDate: 'Please enter a valid date of birth, not later than today',
            timeRequired: 'Please enter your birth time',
            serverError: 'Server error: ',
            baziError: 'Error in Bazi calculation: ',
            unableToParse: 'Unable to parse Bazi results',
            requestFailed: 'Request processing failed: ',
            aiError: 'AI server error: ',
            aiNoContent: 'No content or analysis error.',
            aiRequestFailed: 'AI analysis request failed: ',
            project: 'Item',
            yearPillar: 'Year Pillar',
            monthPillar: 'Month Pillar',
            dayPillar: 'Day Pillar',
            hourPillar: 'Hour Pillar',
            heavenlyStemEarthlyBranch: 'Heavenly Stem & Earthly Branch',
            hiddenStems: 'Hidden Stems',
            zodiac: 'Zodiac',
            constellation: 'Constellation',
            fiveElementsCount: 'Five Elements Count',
            unableToCount: 'Unable to count',
            analyzingBazi: 'Analyzing Bazi...',
            analyzingFiveElements: 'Analyzing Five Elements...',
            feedbackNameRequired: 'Please enter your name',
            feedbackEmailRequired: 'Please enter a valid email address',
            feedbackMessageRequired: 'Please enter your feedback message',
            feedbackSuccess: 'Thank you for your feedback!',
            feedbackError: 'Failed to submit feedback: '
        }
    };

    // 获取翻译文本
    const t = (key) => {
        const lang = getCurrentLanguage();
        return translations[lang][key] || key;
    };

    // 保存用户资料到 localStorage
    function saveUserData(data) {
        console.log("Saving user data:", data);
        localStorage.setItem("userData", JSON.stringify(data));
    }

    // 保存排盘结果到 localStorage
    function saveBaziResult(data) {
        console.log("Saving Bazi result:", data);
        localStorage.setItem("baziResult", JSON.stringify(data));
    }

    // 从 localStorage 加载用户资料并填充表单
    function loadUserData() {
        const savedData = localStorage.getItem("userData");
        if (savedData) {
            const data = JSON.parse(savedData);
            console.log("Loading saved user data:", data);
            document.getElementById("name").value = data.name || '';
            document.getElementById("location").value = data.location || '';
            document.getElementById("birth_date").value = data.birthday || '';
            document.getElementById("birth_time").value = data.birthtime || '';
            const genderRadios = document.getElementsByName("gender");
            for (let radio of genderRadios) {
                if (radio.value === data.gender) {
                    radio.checked = true;
                    break;
                }
            }
        }
    }

    // 从 localStorage 加载排盘结果并显示
    function loadBaziResult() {
        const savedResult = localStorage.getItem("baziResult");
        if (savedResult) {
            const data = JSON.parse(savedResult);
            console.log("Loading saved Bazi result:", data);
            if (data.pillars) {
                let row1 = `<tr><th>${t('project')}</th><th>${t('yearPillar')}</th><th>${t('monthPillar')}</th><th>${t('dayPillar')}</th><th>${t('hourPillar')}</th></tr>`;
                let row2 = `<tr><td>${t('heavenlyStemEarthlyBranch')}</td>` + data.pillars.map(p => `<td>${p}</td>`).join("") + "</tr>";
                let row3 = `<tr><td>${t('hiddenStems')}</td>` + (data.hidden_stems || ["?", "?", "?", "?"]).map(h => `<td>${h}</td>`).join("") + "</tr>";
                let row4 = `<tr><td>${t('zodiac')}</td><td colspan="4">${data.shengxiao || (getCurrentLanguage() === 'zh' ? '未知' : 'Unknown')}</td></tr>`;
                let row5 = `<tr><td>${t('constellation')}</td><td colspan="4">${data.xingzuo || (getCurrentLanguage() === 'zh' ? '未知' : 'Unknown')}</td></tr>`;
                let row6 = `<tr><td>${t('fiveElementsCount')}</td><td colspan="4">${t('unableToCount')}</td></tr>`;
                if (data.wuxing_counts && typeof data.wuxing_counts === 'object') {
                    const wuxingOrder = ["金", "木", "水", "火", "土"];
                    const wuxingClasses = { "金": "gold", "木": "wood", "水": "water", "火": "fire", "土": "earth" };
                    let counts_html = wuxingOrder.map(key => {
                        const value = data.wuxing_counts[key] !== undefined ? data.wuxing_counts[key] : '?';
                        return `<span class="wuxing-cell badge bg-${wuxingClasses[key]} me-2">${key} ${value}</span>`;
                    }).join('');
                    row6 = `<tr><td>${t('fiveElementsCount')}</td><td colspan="4">${counts_html}</td></tr>`;
                }
                grid.innerHTML = "<table id='bazi-table' class='table table-bordered text-center table-sm'>" + row1 + row2 + row3 + row4 + row5 + row6 + "</table>";
                // 设置随机精灵图片
                try {
                    if (typeof wuxingSprites !== 'undefined') {
                        const randomWuxing = getRandomWuxing();
                        aiButtonImage.src = wuxingSprites[randomWuxing];
                        aiButtonContainer.style.display = 'block';
                        submitBaziButton.style.display = 'none';
                    } else {
                        console.error("wuxingSprites is not defined");
                        grid.innerHTML = `<p class='text-danger text-center'>${t('baziError')}wuxingSprites not found</p>`;
                        submitBaziButton.style.display = 'block';
                    }
                } catch (error) {
                    console.error("Error setting sprite image:", error);
                    aiButtonContainer.style.display = 'block';
                }
            }
        }
    }

    // 为后续功能提供接口：获取保存的用户资料
    window.getSavedUserData = function() {
        const savedData = localStorage.getItem("userData");
        if (savedData) {
            return JSON.parse(savedData);
        }
        return null;
    };

    // 保存 AI 分析结果
    function saveAiAnalysisResult(data) {
        console.log("Saving AI analysis result:", data);
        localStorage.setItem("aiAnalysisResult", JSON.stringify(data));
    }

    // 加载 AI 分析结果
    function loadAiAnalysisResult() {
        const savedResult = localStorage.getItem("aiAnalysisResult");
        if (savedResult) {
            const data = JSON.parse(savedResult);
            console.log("Loading saved AI result:", data);
            aiAnalysisResultArea.style.display = 'block';
            aiAnalysisResultArea.innerText = data.result || t('aiNoContent');
            // 强制触发重绘
            requestAnimationFrame(() => {
                aiAnalysisResultArea.offsetHeight;
            });
            // 如果有 AI 结果，禁用五行精灵按钮并保持其显示
            aiButton.disabled = true;
            aiButtonContainer.style.display = 'block';
            submitBaziButton.style.display = 'none';
        }
    }

    // 页面加载时检查并显示保存的用户资料、排盘结果和 AI 分析结果
    loadUserData();
    loadBaziResult();
    loadAiAnalysisResult();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 清空之前的 AI 分析结果
        localStorage.removeItem("aiAnalysisResult");
        aiAnalysisResultArea.style.display = 'none';
        aiAnalysisResultArea.innerHTML = '';

        // 客户端验证
        const name = document.getElementById("name").value.trim();
        const location = document.getElementById("location").value.trim();
        const birthday = document.getElementById("birth_date").value;
        const birthtime = document.getElementById("birth_time").value;

        if (!name || name.length > 50) {
            alert(t('nameRequired'));
            return;
        }
        if (!location) {
            alert(t('locationRequired'));
            return;
        }
        const date = new Date(birthday);
        if (isNaN(date.getTime()) || date > new Date()) {
            alert(t('invalidDate'));
            return;
        }
        if (!birthtime) {
            alert(t('timeRequired'));
            return;
        }

        // 保存用户资料
        const userData = {
            name,
            location,
            birthday,
            birthtime,
            gender: document.querySelector('input[name="gender"]:checked')?.value || (getCurrentLanguage() === 'zh' ? "未知" : "Unknown")
        };
        saveUserData(userData);

        // 进入加载状态
        submitBaziButton.style.display = 'none';
        aiButtonContainer.style.display = 'none';
        grid.innerHTML = '';

        try {
            const response = await fetch('/calculate_bazi', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': csrfToken
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                throw new Error(`${t('serverError')}${response.status} ${response.statusText}`);
            }
            const data = await response.json();

            // 保存排盘结果
            saveBaziResult(data);

            if (data.pillars) {
                let row1 = `<tr><th>${t('project')}</th><th>${t('yearPillar')}</th><th>${t('monthPillar')}</th><th>${t('dayPillar')}</th><th>${t('hourPillar')}</th></tr>`;
                let row2 = `<tr><td>${t('heavenlyStemEarthlyBranch')}</td>` + data.pillars.map(p => `<td>${p}</td>`).join("") + "</tr>";
                let row3 = `<tr><td>${t('hiddenStems')}</td>` + (data.hidden_stems || ["?", "?", "?", "?"]).map(h => `<td>${h}</td>`).join("") + "</tr>";
                let row4 = `<tr><td>${t('zodiac')}</td><td colspan="4">${data.shengxiao || (getCurrentLanguage() === 'zh' ? '未知' : 'Unknown')}</td></tr>`;
                let row5 = `<tr><td>${t('constellation')}</td><td colspan="4">${data.xingzuo || (getCurrentLanguage() === 'zh' ? '未知' : 'Unknown')}</td></tr>`;
                let row6 = `<tr><td>${t('fiveElementsCount')}</td><td colspan="4">${t('unableToCount')}</td></tr>`;
                if (data.wuxing_counts && typeof data.wuxing_counts === 'object') {
                    const wuxingOrder = ["金", "木", "水", "火", "土"];
                    const wuxingClasses = { "金": "gold", "木": "wood", "水": "water", "火": "fire", "土": "earth" };
                    let counts_html = wuxingOrder.map(key => {
                        const value = data.wuxing_counts[key] !== undefined ? data.wuxing_counts[key] : '?';
                        return `<span class="wuxing-cell badge bg-${wuxingClasses[key]} me-2">${key} ${value}</span>`;
                    }).join('');
                    row6 = `<tr><td>${t('fiveElementsCount')}</td><td colspan="4">${counts_html}</td></tr>`;
                }
                grid.innerHTML = "<table id='bazi-table' class='table table-bordered text-center table-sm'>" + row1 + row2 + row3 + row4 + row5 + row6 + "</table>";
                // 设置随机精灵图片
                try {
                    if (typeof wuxingSprites !== 'undefined') {
                        const randomWuxing = getRandomWuxing();
                        aiButtonImage.src = wuxingSprites[randomWuxing];
                        aiButtonContainer.style.display = 'block';
                        aiButton.disabled = false; // 确保按钮在排盘后是可点击的
                    } else {
                        console.error("wuxingSprites is not defined");
                        grid.innerHTML = `<p class='text-danger text-center'>${t('baziError')}wuxingSprites not found</p>`;
                        submitBaziButton.style.display = 'block';
                    }
                } catch (error) {
                    console.error("Error setting sprite image:", error);
                    aiButtonContainer.style.display = 'block';
                }
            } else {
                grid.innerHTML = `<p class='text-danger text-center'>${t('baziError')}${data.error || t('unableToParse')}</p>`;
                submitBaziButton.style.display = 'block';
            }
        } catch (error) {
            console.error("Error in form submission:", error);
            grid.innerHTML = `<p class='text-danger text-center'>${t('requestFailed')}${error.message}</p>`;
            submitBaziButton.style.display = 'block';
        }
    });

    // 辅助函数：延迟指定时间
    const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // 强制触发 DOM 重绘
    const forceRedraw = (element) => {
        requestAnimationFrame(() => {
            element.style.display = 'none';
            element.offsetHeight; // 触发重排
            element.style.display = 'block';
            console.log("Forced redraw on element:", element.id);
        });
    };

    // 防止重复点击
    let isLoading = false;

    aiButton.addEventListener('click', async () => {
        if (isLoading) {
            console.log("AI Button click ignored - loading in progress");
            return;
        }

        console.log("AI Button clicked");
        isLoading = true;
        aiButton.disabled = true; // 禁用按钮

        // 检查是否已有保存的结果
        const savedResult = localStorage.getItem("aiAnalysisResult");
        if (savedResult) {
            console.log("Loading saved AI result");
            const data = JSON.parse(savedResult);
            aiAnalysisResultArea.innerText = data.result || t('aiNoContent');
            aiAnalysisResultArea.style.display = 'block';
            forceRedraw(aiAnalysisResultArea);
            isLoading = false;
            aiButton.disabled = true; // 保持禁用状态
            return;
        }

        // 显示加载状态 - 第一阶段：八字分析中
        aiAnalysisResultArea.style.display = 'block';
        aiAnalysisResultArea.innerHTML = `<div class="loading-spinner d-flex justify-content-center align-items-center p-5"><span class="spinner-border text-primary" role="status"></span><span class="ms-2">${t('analyzingBazi')}</span></div>`;
        forceRedraw(aiAnalysisResultArea);
        console.log("Loading animation displayed in aiAnalysisResultArea - Bazi Analysis");

        // 从 localStorage 获取用户资料
        const userData = getSavedUserData();
        if (!userData) {
            console.error("No user data found in localStorage");
            aiAnalysisResultArea.innerText = t('aiRequestFailed') + "No user data available.";
            aiAnalysisResultArea.style.display = 'block';
            forceRedraw(aiAnalysisResultArea);
            isLoading = false;
            aiButton.disabled = true; // 保持禁用状态
            return;
        }

        const { name, location, birthday, birthtime, gender } = userData;

        // 异步请求 AI 分析
        const fetchAiAnalysis = async () => {
            console.log("Sending AI analysis request");
            const response = await fetch('/ai_analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': csrfToken
                },
                body: JSON.stringify({ name, location, birthday, birthtime, gender })
            });

            if (!response.ok) {
                throw new Error(`${t('aiError')}${response.status}`);
            }

            const data = await response.json();
            console.log("AI analysis response:", data);
            return data;
        };

        try {
            // 加载动画分为两个阶段
            const loadingAnimationPromise = (async () => {
                // 第一阶段：八字分析中 - 持续 2 秒
                await delay(2000);
                console.log("Switching to Five Elements Analysis");
                // 第二阶段：五行分析中 - 持续 2 秒
                aiAnalysisResultArea.innerHTML = `<div class="loading-spinner d-flex justify-content-center align-items-center p-5"><span class="spinner-border text-primary" role="status"></span><span class="ms-2">${t('analyzingFiveElements')}</span></div>`;
                forceRedraw(aiAnalysisResultArea);
                console.log("Loading animation displayed in aiAnalysisResultArea - Five Elements Analysis");
                await delay(2000);
            })();

            // 同时发起 AI 分析请求
            const aiAnalysisPromise = fetchAiAnalysis();

            // 等待加载动画和 AI 分析请求都完成
            const [_, data] = await Promise.all([loadingAnimationPromise, aiAnalysisPromise]);

            // 清除加载动画
            aiAnalysisResultArea.innerHTML = '';
            console.log("Loading animation cleared");

            // 更新 AI 分析结果
            saveAiAnalysisResult(data);
            aiAnalysisResultArea.innerText = data.result || t('aiNoContent');
            aiAnalysisResultArea.style.display = 'block';
            forceRedraw(aiAnalysisResultArea);
            console.log("AI result displayed");

            // 保持五行精灵按钮显示并禁用
            aiButtonContainer.style.display = 'block';
            aiButton.disabled = true;
        } catch (error) {
            console.error("Error in AI analysis:", error);
            aiAnalysisResultArea.innerHTML = '';
            aiAnalysisResultArea.innerText = `${t('aiRequestFailed')}${error.message}`;
            aiAnalysisResultArea.style.display = 'block';
            forceRedraw(aiAnalysisResultArea);

            // 保持五行精灵按钮显示并禁用
            aiButtonContainer.style.display = 'block';
            aiButton.disabled = true;
        } finally {
            isLoading = false;
        }
    });

    aiButton.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') aiButton.click();
    });

    // 添加“清除保存资料”按钮的事件监听器
    if (clearUserDataButton) {
        clearUserDataButton.addEventListener('click', () => {
            // 清除 localStorage 中的用户资料、排盘结果和 AI 分析结果
            localStorage.removeItem("userData");
            localStorage.removeItem("baziResult");
            localStorage.removeItem("aiAnalysisResult");
            console.log("User data, Bazi result, and AI result cleared");

            // 重置表单
            form.reset();

            // 清空分析结果区域和排盘结果
            aiAnalysisResultArea.style.display = 'none';
            aiAnalysisResultArea.innerHTML = '';
            grid.innerHTML = '';

            // 隐藏“解读命盘”按钮并显示“排盘”按钮
            aiButtonContainer.style.display = 'none';
            submitBaziButton.style.display = 'block';
            aiButton.disabled = false; // 重新启用五行精灵按钮
        });
    } else {
        console.error("clearUserDataButton not found in the DOM");
    }

    // “立即赞助”按钮事件监听器
    if (donateNowButton) {
        donateNowButton.addEventListener('click', () => {
            // 直接跳转到预生成的 Stripe 支付 URL
            window.location.href = 'https://buy.stripe.com/3cIfZgft7fv9dKIfXi6c001';
        });
    } else {
        console.error("donateNowButton not found in the DOM");
    }

    window.changeLanguage = function(lang) {
        document.cookie = `language=${lang}; path=/`;
        location.reload();
    };

    feedbackForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('feedbackName').value.trim();
        const email = document.getElementById('feedbackEmail').value.trim();
        const message = document.getElementById('feedbackMessage').value.trim();

        if (!name) {
            alert(t('feedbackNameRequired'));
            return;
        }
        if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            alert(t('feedbackEmailRequired'));
            return;
        }
        if (!message) {
            alert(t('feedbackMessageRequired'));
            return;
        }

        try {
            const response = await fetch('/submit_feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': csrfToken
                },
                body: JSON.stringify({ name, email, message })
            });

            const data = await response.json();
            if (data.success) {
                alert(t('feedbackSuccess'));
                document.getElementById('modalFeedback').querySelector('.btn-close').click();
                feedbackForm.reset();
            } else {
                alert(`${t('feedbackError')}${data.message}`);
            }
        } catch (error) {
            alert(`${t('feedbackError')}${error.message}`);
        }
    });

    const symbols = [
        "⚅", "🌳", "💧", "🔥", "🪨",
        "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓",
        "🐀", "🐂", "🐅", "🐇", "🐉", "🐍", "🐎", "🐐", "🐒", "🐓", "🐕", "🐖"
    ];

    console.log("Particle effect initialized");

    function createParticle() {
        console.log("Creating a particle");
        const particle = document.createElement("div");
        particle.classList.add("particle");

        const swayContainer = document.createElement("div");
        swayContainer.classList.add("sway-container");
        swayContainer.innerText = symbols[Math.floor(Math.random() * symbols.length)] || "*";
        particle.appendChild(swayContainer);

        particle.style.left = `${Math.random() * 100}vw`;
        const duration = Math.random() * 10 + 5;
        particle.style.animationDuration = `${duration}s`;
        particle.style.webkitAnimationDuration = `${duration}s`;
        particle.style.animationDelay = `${Math.random() * 5}s`;
        particle.style.webkitAnimationDelay = `${Math.random() * 5}s`;
        swayContainer.style.animationDuration = `${duration / 2}s`;
        swayContainer.style.webkitAnimationDuration = `${duration / 2}s`;
        particle.style.fontSize = `${Math.random() * 10 + 15}px`;

        const background = document.getElementById("particle-background");
        if (background) {
            background.appendChild(particle);
        } else {
            console.error("Particle background container not found");
        }

        particle.addEventListener("animationend", () => {
            particle.remove();
        });

        setTimeout(() => {
            particle.remove();
        }, (duration + 5) * 1000);
    }

    setInterval(createParticle, 600);
});