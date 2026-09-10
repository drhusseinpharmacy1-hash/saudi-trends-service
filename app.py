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

@app.route('/daily-trends', methods=['GET'])
def get_daily_trends():
    try:
        # الاتصال بـ Google Trends باللغة العربية وتوقيت السعودية
        pytrends = TrendReq(hl='ar-SA', tz=180, timeout=(10, 25))
        
        # جلب الأكثر بحثاً اليوم في السعودية
        df = pytrends.trending_searches(pn='saudi_arabia')
        
        # استخراج أول 12 كلمة بحث متصدرة
        keywords = df[0].tolist()[:12]
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trending_keywords": keywords
        }), 200

    except Exception as e:
        # في حال حدوث Rate Limit من جوجل أو خطأ في الاتصال
        print(f"Error fetching daily trends: {str(e)}")
        
        # قائمة احتياطية متجددة ديناميكياً
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
    # تشغيل السيرفر على المنفذ المحدد من Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
