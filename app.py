import os
import random
from flask import Flask, jsonify, request
from pytrends.request import TrendReq
from datetime import datetime

app = Flask(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
]

# ------------------ 1. جلب اتجاهات الكلمة حسب المناطق ------------------
@app.route('/trends', methods=['GET'])
def get_keyword_trends():
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        pytrends = TrendReq(
            hl='ar-SA', 
            tz=180, 
            timeout=(10, 25), 
            retries=2, 
            backoff_factor=1.5, 
            requests_args={'headers': headers}
        )
        
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='SA', gprop='')
        df = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
        
        filtered_trends = {}
        if not df.empty and keyword in df.columns:
            region_data = df[keyword].to_dict()
            sorted_regions = sorted(
                [(str(k), int(v)) for k, v in region_data.items() if v > 0], 
                key=lambda x: x[1], 
                reverse=True
            )
            filtered_trends = dict(sorted_regions)

        return jsonify({
            "status": "success",
            "keyword": keyword,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trends": filtered_trends
        }), 200

    except Exception as e:
        print(f"Error fetching trends for {keyword}: {str(e)}")
        # إرجاع استجابة واضحة في حال الحظر المباشر من Google
        return jsonify({
            "status": "error",
            "message": "Google rate limit hit or timeout occurred",
            "details": str(e),
            "trends": {}
        }), 429 if "429" in str(e) else 500

# ------------------ 2. جلب الأكثر بحثاً اليوم ------------------
@app.route('/daily-trends', methods=['GET'])
def get_daily_trends():
    try:
        pytrends = TrendReq(hl='ar-SA', tz=180, timeout=(10, 25))
        df = pytrends.trending_searches(pn='saudi_arabia')
        keywords = df[0].tolist()[:12]
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trending_keywords": keywords
        }), 200

    except Exception as e:
        print(f"Error fetching daily trends: {str(e)}")
        fallback_keywords = [
            "واقي شمس", "مونجارو", "فيتامين د", "سيروم فيتامين سي", 
            "أوميغا 3", "كولاجين", "زينيكال", "روكوتان"
        ]
        return jsonify({
            "status": "fallback",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trending_keywords": fallback_keywords
        }), 200

# ------------------ 3. فحص حالة السيرفر ------------------
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "service": "Saudi Trends Backend API",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
