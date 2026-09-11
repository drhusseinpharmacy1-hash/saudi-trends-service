import os
import time
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

# ------------------ 1. جلب اهتمام المناطق بكلمة معينة ------------------
@app.route('/trends', methods=['GET'])
def get_keyword_trends():
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    try:
        # إضافة مهلة وتكرار محاولات لتفادي Rate Limit من جوجل
        pytrends = TrendReq(hl='ar-SA', tz=180, timeout=(10, 25))
        
        # بناء الطلب بمرونة
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='SA', gprop='')
        
        # جلب البيانات
        df = pytrends.interest_by_region(resolution='CITY', inc_low_vol=True, inc_geo_code=False)
        
        filtered_trends = {}
        if not df.empty and keyword in df.columns:
            region_data = df[keyword].to_dict()
            filtered_trends = {str(k): int(v) for k, v in region_data.items() if v > 0}

        return jsonify({
            "status": "success",
            "keyword": keyword,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trends": filtered_trends
        }), 200

    except Exception as e:
        print(f"Error fetching trends for {keyword}: {str(e)}")
        # في حال حدوث خطأ أو حظر من جوجل، يتم إرجاع نتيجة فارغة بنجاح بدلاً من انهيار السيرفر بكود 500
        return jsonify({
            "status": "error",
            "message": "Google Trends request limit or connection error",
            "trends": {}
        }), 200

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
