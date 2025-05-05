from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_babel import Babel, _
import os
from dotenv import load_dotenv
import time
import sxtwl
from flask_wtf.csrf import generate_csrf
from database import init_db, save_feedback
from flask import Response

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "your-secret-key-here")
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Asia/Shanghai'

# 初始化 Babel
babel = Babel(app)
csrf = CSRFProtect(app)

# 初始化数据库
init_db()

@app.route('/ads.txt')
def ads_txt():
    # 把下面这行内容替换成 AdSense 提供给你的实际内容
    content = "google.com, pub-1744811073515831, DIRECT, f08c47fec0942fa0"
    return Response(content, mimetype='text/plain')

# 定义语言选择函数
@babel.localeselector

def get_locale():
    lang = request.cookies.get('language')
    if lang in ['zh', 'en']:
        return lang
    return request.accept_languages.best_match(['zh', 'en']) or 'zh'

# OpenAI Client 初始化
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("警告：未能从 .env 文件或环境变量中加载 OPENAI_API_KEY。AI 分析功能将不可用。")
    client = None
else:
    try:
        client = OpenAI(api_key=openai_api_key, timeout=30)
        print("OpenAI 客户端已成功初始化。")
    except Exception as e:
        print(f"使用环境变量中的 Key 初始化 OpenAI 客户端时出错: {e}")
        client = None

# 五行、天干、地支等映射
GAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}
ZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
}
GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
SHENGXIAO = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
hidden_stems_map = {
    '子': '癸', '丑': '己癸辛', '寅': '甲丙戊', '卯': '乙', '辰': '戊乙癸',
    '巳': '丙庚戊', '午': '丁己', '未': '己丁乙', '申': '庚壬戊', '酉': '辛',
    '戌': '戊辛丁', '亥': '壬甲'
}

def get_xingzuo(month, day):
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return _("Aries") if get_locale() == 'en' else "白羊座"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return _("Taurus") if get_locale() == 'en' else "金牛座"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 21):
        return _("Gemini") if get_locale() == 'en' else "双子座"
    elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
        return _("Cancer") if get_locale() == 'en' else "巨蟹座"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return _("Leo") if get_locale() == 'en' else "狮子座"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return _("Virgo") if get_locale() == 'en' else "处女座"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 23):
        return _("Libra") if get_locale() == 'en' else "天秤座"
    elif (month == 10 and day >= 24) or (month == 11 and day <= 22):
        return _("Scorpio") if get_locale() == 'en' else "天蝎座"
    elif (month == 11 and day >= 23) or (month == 12 and day <= 21):
        return _("Sagittarius") if get_locale() == 'en' else "射手座"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return _("Capricorn") if get_locale() == 'en' else "摩羯座"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return _("Aquarius") if get_locale() == 'en' else "水瓶座"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return _("Pisces") if get_locale() == 'en' else "双鱼座"
    else:
        return _("Unknown") if get_locale() == 'en' else "未知"

def calculate_bazi(year, month, day, hour, minute):
    try:
        day_obj = sxtwl.fromSolar(year, month, day)
        time_obj = sxtwl.Time(year, month, day, hour, minute, 0)
        year_gz = day_obj.getYearGZ()
        month_gz = day_obj.getMonthGZ()
        day_gz = day_obj.getDayGZ()
        hour_gz = day_obj.getHourGZ(int(time_obj.h), True)

        gz_indices = [(year_gz.tg, year_gz.dz), (month_gz.tg, month_gz.dz),
                      (day_gz.tg, day_gz.dz), (hour_gz.tg, hour_gz.dz)]
        pillars = [f"{GAN[tg_idx]}{ZHI[dz_idx]}" for tg_idx, dz_idx in gz_indices]
        dz_names = [ZHI[dz_idx] for _, dz_idx in gz_indices]
        hidden_stems = [hidden_stems_map.get(dz_name, "?") for dz_name in dz_names]

        wuxing_counts = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        for tg_idx, dz_idx in gz_indices:
            gan_char = GAN[tg_idx]
            zhi_char = ZHI[dz_idx]
            if gan_char in GAN_WUXING:
                wuxing_counts[GAN_WUXING[gan_char]] += 1
            if zhi_char in ZHI_WUXING:
                wuxing_counts[ZHI_WUXING[zhi_char]] += 1
        for stem_group in hidden_stems:
            for stem_char in stem_group:
                if stem_char in GAN_WUXING:
                    wuxing_counts[GAN_WUXING[stem_char]] += 1

        year_dz_idx = year_gz.dz
        shengxiao_name = _(SHENGXIAO[year_dz_idx]) if get_locale() == 'en' else SHENGXIAO[year_dz_idx]
        xingzuo_name = get_xingzuo(month, day)

        return {
            "pillars": pillars,
            "hidden_stems": hidden_stems,
            "shengxiao": shengxiao_name,
            "xingzuo": xingzuo_name,
            "wuxing_counts": wuxing_counts
        }
    except Exception as e:
        print(f"Error in calculate_bazi with input ({year}-{month}-{day} {hour}:{minute}): {e}")
        return {
            "error": f"八字计算失败: {e}" if get_locale() == 'zh' else f"Bazi calculation failed: {e}",
            "shengxiao": "错误" if get_locale() == 'zh' else "Error",
            "xingzuo": "错误" if get_locale() == 'zh' else "Error",
            "wuxing_counts": {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        }

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", csrf_token=generate_csrf(), get_locale=get_locale)

@app.route("/ziwei") # 定义紫微斗数的URL路径
def ziwei_page():
    # 这里暂时先渲染一个简单的 "即将推出" 页面
    # 你需要创建一个名为 coming_soon.html 的模板文件
    system_name = _("Zi Wei Dou Shu") if get_locale() == 'en' else "紫微斗数"
    return render_template("ziwei_page.html", system_name=system_name, get_locale=get_locale)

@app.route("/boneweight") # 定义称骨算命的URL路径
def boneweight_page():
    system_name = _("Bone Weight Fortune") if get_locale() == 'en' else "称骨算命"
    return render_template("boneweight_page.html", system_name=system_name, get_locale=get_locale)

@app.route("/sanshi") # 定义三世书的URL路径
def sanshi_page():
    system_name = _("Three Lives Book") if get_locale() == 'en' else "三世书"
    return render_template("sanshi_page.html", system_name=system_name, get_locale=get_locale)

@app.route("/shengxiao") # 定义生肖命理的URL路径
def shengxiao_page():
    system_name = _("Zodiac Analysis") if get_locale() == 'en' else "生肖命理"
    return render_template("shengxiao_page.html", system_name=system_name, get_locale=get_locale)

@app.route("/xingzuo") # 定义星座分析的URL路径
def xingzuo_page():
    system_name = _("Astrology") if get_locale() == 'en' else "星座分析"
    return render_template("xingzuo_page.html", system_name=system_name, get_locale=get_locale)

@app.route("/xingxiu") # 定义28星宿的URL路径
def xingxiu_page():
    system_name = _("28 Lunar Mansions") if get_locale() == 'en' else "28星宿"
    return render_template("xingxiu_page.html", system_name=system_name, get_locale=get_locale)

@app.route("/calculate_bazi", methods=["POST"])
def calculate_bazi_route():
    data = request.get_json()
    birthday = data["birthday"]
    birthtime = data["birthtime"]

    try:
        year, month, day = map(int, birthday.split("-"))
        hour, minute = map(int, birthtime.split(":"))
        bazi_data = calculate_bazi(year, month, day, hour, minute)
        return jsonify(bazi_data)
    except Exception as e:
        return jsonify({"error": f"排盘失败：{e}" if get_locale() == 'zh' else f"Bazi calculation failed: {e}"})

def call_openai_with_retry(prompt, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一位精通传统八字命理学的资深顾问，能够根据用户提供的生辰八字信息，进行专业、客观、条理清晰的命盘解读和人生建议。" if get_locale() == 'zh' else "You are an expert in traditional Chinese Bazi fortune-telling, capable of providing professional, objective, and clear destiny analysis and life advice based on the user's birth information."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            raise e

@app.route("/ai_analysis", methods=["POST"])
def ai_analysis():
    if not client:
        return jsonify({"result": "AI 分析功能当前不可用（API 密钥未配置或初始化失败）。" if get_locale() == 'zh' else "AI analysis is currently unavailable (API key not configured or initialization failed)."})

    data = request.get_json()
    name = data.get("name", "未知" if get_locale() == 'zh' else "Unknown")
    location = data.get("location", "未知" if get_locale() == 'zh' else "Unknown")
    birthday = data.get("birthday", "未知" if get_locale() == 'zh' else "Unknown")
    birthtime = data.get("birthtime", "未知" if get_locale() == 'zh' else "Unknown")
    gender = data.get("gender", "未知" if get_locale() == 'zh' else "Unknown")

    try:
        year, month, day = map(int, birthday.split("-"))
        hour, minute = map(int, birthtime.split(":"))
        bazi_data = calculate_bazi(year, month, day, hour, minute)
        if "error" in bazi_data:
            raise Exception(bazi_data["error"])
    except Exception as e:
        return jsonify({"result": f"无法为 AI 分析准备所需数据：{e}" if get_locale() == 'zh' else f"Unable to prepare data for AI analysis: {e}"})

    pillars = bazi_data.get("pillars", ["未知"]*4 if get_locale() == 'zh' else ["Unknown"]*4)
    hidden_stems = bazi_data.get("hidden_stems", ["未知"]*4 if get_locale() == 'zh' else ["Unknown"]*4)
    shengxiao = bazi_data.get("shengxiao", "未知" if get_locale() == 'zh' else "Unknown")

    user_info = f"个人信息：姓名({name}), 性别({gender}), 公历生日({birthday}), 出生时间({birthtime}), 出生地({location}), 生肖({shengxiao})." if get_locale() == 'zh' else f"Personal Info: Name({name}), Gender({gender}), Birthday({birthday}), Birth Time({birthtime}), Birthplace({location}), Zodiac({shengxiao})."
    bazi_info = (f"八字排盘：\n" if get_locale() == 'zh' else f"Bazi Chart:\n") + \
                (f"- 年柱: {pillars[0]} (藏干: {hidden_stems[0]})\n" if get_locale() == 'zh' else f"- Year Pillar: {pillars[0]} (Hidden Stems: {hidden_stems[0]})\n") + \
                (f"- 月柱: {pillars[1]} (藏干: {hidden_stems[1]})\n" if get_locale() == 'zh' else f"- Month Pillar: {pillars[1]} (Hidden Stems: {hidden_stems[1]})\n") + \
                (f"- 日柱: {pillars[2]} (藏干: {hidden_stems[2]}) <-- 日元/命主\n" if get_locale() == 'zh' else f"- Day Pillar: {pillars[2]} (Hidden Stems: {hidden_stems[2]}) <-- Day Master\n") + \
                (f"- 时柱: {pillars[3]} (藏干: {hidden_stems[3]})\n" if get_locale() == 'zh' else f"- Hour Pillar: {pillars[3]} (Hidden Stems: {hidden_stems[3]})\n")

    prompt = f"""
**输入信息:**
{user_info}
{bazi_info}

分析要求:
{"请根据以上完整的八字信息，模拟一位资深、专业、客观的东方命理顾问，进行一次**非常详细深入的八字命盘分析。请严格遵循八字命理的核心原理（如五行生克、十神关系、强弱喜忌等基础概念）。分析内容需重点详述以下方面（尤其是五行、事业财运、感情婚姻），并使用【】括号内的标题清晰分隔各部分，确保每个部分内容充实、论述具体：" if get_locale() == 'zh' else "Based on the complete Bazi information above, simulate a senior, professional, and objective Eastern fortune-telling expert to conduct a **highly detailed and in-depth Bazi destiny analysis. Strictly follow the core principles of Bazi fortune-telling (e.g., the interaction of the Five Elements, the Ten Gods relationships, and the balance of strength and weakness). The analysis should focus on the following aspects (especially the Five Elements, career and wealth, and relationships and marriage), and use titles in 【】 brackets to clearly separate each section, ensuring each section is comprehensive and detailed:"}

1.  【五行分析】(请详述)：
    {"明确指出此八字中金、木、水、火、土五个元素的具体旺衰程度（例如：哪个最旺？哪个次旺？是否有缺失？请量化或清晰描述）。 清晰判断 日主（日柱天干：{pillars[2][0]}）的五行属性及其旺衰等级（例如：身强？身弱？从强？从弱？或其他具体描述）。 基于旺衰分析，明确指出此命局最关键的喜用神（对命主有利的五行）和忌神（对命主不利的五行），并简要说明判断的核心依据（例如：身弱喜印比，身强喜财官伤等）。 点明五行平衡或不平衡对命主整体格局（例如：流通性、稳定性）的基础影响。" if get_locale() == 'zh' else "Clearly specify the strength and weakness of the Five Elements (Metal, Wood, Water, Fire, Earth) in this Bazi chart (e.g., which is the strongest? Which is the second strongest? Is any element missing? Quantify or describe clearly). Clearly determine the Five Element attribute and strength level of the Day Master (Day Stem: {pillars[2][0]}) (e.g., strong? weak? extremely strong? extremely weak? or other specific descriptions). Based on the strength analysis, identify the most critical favorable elements (beneficial to the Day Master) and unfavorable elements (detrimental to the Day Master), and briefly explain the core reasoning for the judgment (e.g., a weak Day Master favors the Resource and Peer elements, a strong Day Master favors Wealth, Officer, and Output elements). Highlight the impact of the balance or imbalance of the Five Elements on the overall chart structure (e.g., flow, stability)."}

2.  【性格特征】：
    {"基于八字组合（尤其是日柱、月柱的干支和十神）推断命主的主要性格优点和潜在缺点。（此部分可相对简洁）" if get_locale() == 'zh' else "Infer the main personality strengths and potential weaknesses of the Day Master based on the Bazi combination (especially the stems and branches of the Day and Month Pillars and the Ten Gods). (This section can be relatively concise)"}

3.  【事业财运】(请重点详述)：
    {"事业定位与方向：根据命局特点（五行喜忌、十神配置如官印相生、食伤生财等），深入分析命主是更适合稳定求职（例如：公务员、大公司职员）还是**创业经商/自由职业？有无管理或领导潜质？具体指出几个最适合命主长期发展的**行业领域或职业方向**（需明确结合喜用神五行属性，例如：喜木火，适合文化、教育、能源、互联网等）。 发展机遇与挑战：分析事业发展中可能遇到的主要阻碍（例如：是小人影响/比劫竞争？还是自身执行力/决策力问题？或是时运不济？）以及潜在的贵人运（例如：印星为用，易得长辈或上司帮助）或关键发展机遇期（可基于十神组合和力量简单推断）。 财运详细分析：区分正财（工资、固定收入）和偏财（投资、副业、意外之财）的来源及旺衰程度。命主是更容易获得哪种类型的财富？财富的规模潜力如何（小富、中富、大富）？命局中是否有明显的破财信息（例如：比劫过旺无制约）？需要注意哪些**理财观念或风险**？ 具体行动建议：提供至少3条有针对性的、可操作的建议，以帮助命主扬长避短，选择合适职业道路，提升事业层次和增加财富积累（例如：适合的合作对象五行属性？需要提升哪些技能？应该规避哪些投资风险？）。" if get_locale() == 'zh' else "Career Positioning and Direction: Based on the characteristics of the chart (favorable and unfavorable Five Elements, Ten Gods configuration such as Officer-Resource harmony, Output-Wealth generation, etc.), deeply analyze whether the Day Master is more suited for stable employment (e.g., civil servant, corporate employee) or **entrepreneurship/freelancing? Do they have management or leadership potential? Specify several industries or career paths most suitable for the Day Master’s long-term development** (must clearly relate to the favorable Five Elements, e.g., favoring Wood and Fire, suitable for culture, education, energy, internet industries, etc.). Opportunities and Challenges: Analyze the main obstacles the Day Master may face in career development (e.g., interference from petty people/Peer competition? Issues with execution/decision-making? Or poor timing?) and potential benefactor luck (e.g., Resource as a favorable element, likely to receive help from elders or superiors) or key development opportunities (can be inferred simply from the Ten Gods combination and strength). Wealth Analysis: Distinguish between Regular Wealth (salary, fixed income) and Irregular Wealth (investments, side businesses, windfalls) sources and their strength. Which type of wealth is the Day Master more likely to obtain? What is the potential scale of wealth (small, medium, large)? Are there clear signs of wealth loss in the chart (e.g., overly strong Peers without restraint)? What **financial concepts or risks** should they be aware of? Specific Actionable Advice: Provide at least 3 targeted, actionable suggestions to help the Day Master leverage strengths and mitigate weaknesses, choose the right career path, enhance career prospects, and increase wealth accumulation (e.g., favorable Five Elements for business partners? Skills to improve? Investment risks to avoid?)."}

4.  【感情婚姻】(请重点详述)：
    {"感情模式与择偶观：根据日柱干支、夫妻宫（日支：{pillars[2][1]}）的十神属性和与其他柱的关系，详细分析命主的恋爱态度（例如：是追求浪漫还是现实？主动还是被动？）和在感情中的**行为模式**（例如：控制欲强？依赖性重？付出型？）。对伴侣有何内在期望？ 配偶信息线索：详细分析命局中夫妻星（男命看【财星】，女命看【官杀星】）的状态（包括其旺衰、位置、是否为喜用神、有无受到严重冲克刑害），这暗示了未来伴侣可能的能力、性格特点以及与命主关系的质量和缘分深浅。 婚姻稳定性评估：根据夫妻宫（日支）的稳定性（是喜用神还是忌神？有无被严重冲、刑、合、害？）、结合整体命局（例如：比劫重重是否克妻/夫？食伤过旺是否不利女命婚姻？），深入分析婚姻关系的和谐度、早婚或晚婚的可能性、以及潜在的感情波动或危机（例如：易出现竞争者？沟通障碍？两地分居？）。 具体相处建议：提供至少3条具体的建议，帮助命主了解自身感情需求、选择合适的伴侣类型（例如：五行互补？性格匹配？）、或者在已有关系中趋吉避凶、维护婚姻长久稳定（例如：需要注意沟通方式？需要给对方空间？）。" if get_locale() == 'zh' else "Relationship Patterns and Partner Preferences: Based on the Day Pillar’s stem and branch, the Spouse Palace (Day Branch: {pillars[2][1]}), its Ten Gods attributes, and its relationship with other pillars, thoroughly analyze the Day Master’s attitude toward love (e.g., pursuing romance or practicality? Proactive or passive?) and their **behavior patterns** in relationships (e.g., controlling? Dependent? Giving?). What are their inner expectations for a partner? Spouse Information Clues: Thoroughly analyze the state of the Spouse Star in the chart (for males, look at the 【Wealth Star】; for females, look at the 【Officer/Seven Killings Star】) (including its strength, position, whether it’s a favorable element, and whether it’s severely clashed, punished, combined, or harmed), which indicates the potential abilities, personality traits of the future spouse, and the quality and depth of their relationship with the Day Master. Marriage Stability Assessment: Based on the stability of the Spouse Palace (Day Branch) (is it a favorable or unfavorable element? Is it severely clashed, punished, combined, or harmed?), combined with the overall chart (e.g., overly strong Peers causing spouse issues? Overly strong Output unfavorable for female marriage?), thoroughly analyze the harmony of the marriage, the likelihood of early or late marriage, and potential emotional fluctuations or crises (e.g., likely to face competitors? Communication barriers? Long-distance relationships?). Specific Relationship Advice: Provide at least 3 specific suggestions to help the Day Master understand their emotional needs, choose a suitable partner type (e.g., complementary Five Elements? Compatible personality?), or maintain long-term marital stability in existing relationships (e.g., need to improve communication? Need to give the partner space?)."}

5.  【健康提示】：
    {"根据八字中的五行平衡情况，指出身体方面可能存在的薄弱环节或需要注意的潜在健康问题。（此部分可相对简洁） 提出简单的养生建议。" if get_locale() == 'zh' else "Based on the balance of the Five Elements in the Bazi chart, identify potential weak areas or health concerns to be aware of. (This section can be relatively concise) Provide simple wellness advice."}

6.  【整体建议】：
    {"综合以上所有详细分析，为命主提炼几条最关键的人生发展指导和趋吉避凶的核心建议。" if get_locale() == 'zh' else "Synthesize all the detailed analyses above to provide several key life development guidelines and core advice for avoiding misfortune and seeking fortune."}

{"请确保语言专业、中肯、详尽，避免使用过于绝对或迷信的词汇，重点在于提供有价值、有深度、有指导意义的参考信息。结果不要出现#和*的符号" if get_locale() == 'zh' else "Ensure the language is professional, objective, and detailed, avoiding overly absolute or superstitious terms, focusing on providing valuable, in-depth, and guiding reference information. Do not use # or * symbols in the results."}
"""

    try:
        result = call_openai_with_retry(prompt)
        cleaned_result = result.replace('### ', '').replace('**', '')
        return jsonify({"result": cleaned_result.strip()})
    except Exception as e:
        print(f"调用 OpenAI API 时出错: {e}")
        return jsonify({"result": f"AI 分析失败：{str(e)}" if get_locale() == 'zh' else f"AI analysis failed: {str(e)}"})

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not message:
        return jsonify({"success": False, "message": "所有字段均为必填项。" if get_locale() == 'zh' else "All fields are required."})

    try:
        save_feedback(name, email, message)
        return jsonify({"success": True, "message": "感谢您的反馈！" if get_locale() == 'zh' else "Thank you for your feedback!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"提交失败：{str(e)}" if get_locale() == 'zh' else f"Submission failed: {str(e)}"})

if __name__ == "__main__":
    print("Application entry point. Run with a WSGI server like Waitress.")
    # app.run(host="0.0.0.0", port=5000, debug=True) # 已删除或注释掉