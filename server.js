const express = require('express');
const app = express();
const port = process.env.PORT || 4000;

app.use(express.json());
app.use(express.static('index.html')); // 提供静态文件（如 index.html）

// 模拟 /calculate_bazi API
app.post('/calculate_bazi', (req, res) => {
    const userData = req.body;
    res.json({
        pillars: ["甲子", "乙丑", "丙寅", "丁卯"],
        hidden_stems: ["癸", "己", "戊", "丙"],
        shengxiao: "鼠",
        xingzuo: "水瓶座",
        wuxing_counts: { "金": 2, "木": 1, "水": 3, "火": 0, "土": 1 }
    });
});

// 模拟 /ai_analysis API
app.post('/destiny-analysis-app', (req, res) => {
    const userData = req.body;
    res.json({
        result: "这是一个示例 AI 分析结果。"
    });
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});