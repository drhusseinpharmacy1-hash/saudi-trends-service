import os
import random
from flask import Flask, jsonify, request
from pytrends.request import TrendReq
from datetime import datetime

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# قائمة متصفحات للتخفي أثناء الطلب
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
]

@app.route('/trends', methods=['GET'])
def get_keyword_trends():
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    try:
        # 1. اختيار User-Agent عشوائي لتمويه الطلب كأنه من متصفح عايدي
        random_agent = random.choice(USER_AGENTS)
        
        # 2. تهيئة الاتصال بدون إجبار السيرفر على التدقيق العالي
        pytrends = TrendReq(
            hl='ar-SA', 
            tz=180, 
            timeout=(10, 25),
            retries=2,
            backoff_factor=1.5
        )
        
        # 3. طلب البيانات على مستوى المناطق (COUNTRY) لتجميع حجم البحث
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='SA', gprop='')
        
        df = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
        
        filtered_trends = {}
        if not df.empty and keyword in df.columns:
            region_data = df[keyword].to_dict()
            # تصفية أي قيمة أكبر من صفر
            filtered_trends = {str(k): int(v) for k, v in region_data.items() if v > 0}

        return jsonify({
            "status": "success",
            "keyword": keyword,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trends": filtered_trends
        }), 200

    except Exception as e:
        print(f"Error fetching trends for {keyword}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Connection limit: {str(e)}",
            "trends": {}
        }), 200

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
        fallback_keywords = [
            "واقي شمس", "مونجارو", "فيتامين د", "سيروم فيتامين سي", 
            "أوميغا 3", "كولاجين", "زينيكال", "روكوتان"
        ]
        return jsonify({
            "status": "fallback",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trending_keywords": fallback_keywords
        }), 200

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
