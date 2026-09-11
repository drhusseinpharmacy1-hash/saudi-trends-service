import os
from flask import Flask, jsonify, request
from pytrends.request import TrendReq
from datetime import datetime

app = Flask(__name__)

# إعداد رأس الصفحة لمنع التخزين المؤقت (No-Cache Headers)
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
        # الاتصال بـ Google Trends باللغة العربية وتوقيت السعودية
        pytrends = TrendReq(hl='ar-SA', tz=180, timeout=(10, 25))
        
        # بناء الـ Payload للكلمة المحددة داخل المملكة العربية السعودية
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='SA', gprop='')
        
        # جلب البيانات مقسمة حسب المدن/المناطق
        df = pytrends.interest_by_region(resolution='CITY', inc_low_vol=True, inc_geo_code=False)
        
        if not df.empty and keyword in df.columns:
            region_data = df[keyword].to_dict()
            # تصفية المدن التي تحتوي على نسبة بحث أعلى من 0
            filtered_trends = {k: int(v) for k, v in region_data.items() if v > 0}
            
            return jsonify({
                "status": "success",
                "keyword": keyword,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "trends": filtered_trends
            }), 200
        else:
            return jsonify({
                "status": "success",
                "keyword": keyword,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "trends": {}
            }), 200

    except Exception as e:
        print(f"Error fetching trends for {keyword}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

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
