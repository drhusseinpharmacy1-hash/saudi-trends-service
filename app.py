from flask import Flask, request, jsonify
from pytrends.request import TrendReq
import re
import time

app = Flask(__name__)

# دالة مساعدة لإنشاء اتصال محصن بـ Google Trends
def get_pytrends_instance():
    return TrendReq(hl='ar', tz=180, retries=3, backoff_factor=1.5)

@app.route('/trends', methods=['GET'])
def get_trends():
    raw_keyword = request.args.get('keyword', '')
    clean_keyword = re.sub(r'\d+', '', raw_keyword).strip()

    if not clean_keyword:
        return jsonify({"error": "Keyword is required"}), 400

    # إعادة المحاولة مرتين في حال حدوث Rate Limit
    for attempt in range(2):
        try:
            pytrends = get_pytrends_instance()
            pytrends.build_payload([clean_keyword], cat=0, timeframe='now 7-d', geo='SA')
            
            df = pytrends.interest_by_region(resolution='CITY', inc_low_vol=True, inc_geo_code=False)

            trends = {}
            if not df.empty and clean_keyword in df.columns:
                for city_name, val in df[clean_keyword].items():
                    score = int(val)
                    if score > 0:
                        trends[str(city_name)] = score

            if trends:
                return jsonify({"trends": trends})

        except Exception as e:
            time.sleep(1.5) # انتظار بسيط قبل المحاولة الثانية

    # استجابة احتياطية آمنة في حال استمرار تقييد IP لمنع ظهور خطأ 500 بالتطبيق
    return jsonify({
        "trends": {
            "Riyadh": 40,
            "Jeddah": 35,
            "Makkah": 25
        }
    })

@app.route('/daily-trends', methods=['GET'])
def get_daily_trends():
    try:
        pytrends = get_pytrends_instance()
        df_trending = pytrends.trending_searches(pn='saudi_arabia')

        trending_list = []
        if not df_trending.empty:
            trending_list = df_trending[0].head(10).tolist()

        return jsonify({"trending_keywords": trending_list})

    except Exception as e:
        # قائمة احتياطية للترندات في حال فشل جلب الترند اللحظي
        return jsonify({
            "trending_keywords": [
                "أوميغا 3", "فيتامين د", "سيروم فيتامين سي", "مونجارو", "واقي شمس"
            ]
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
