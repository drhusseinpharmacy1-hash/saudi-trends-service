from flask import Flask, request, jsonify
from pytrends.request import TrendReq
import re

app = Flask(__name__)

@app.route('/trends', methods=['GET'])
def get_trends():
    raw_keyword = request.args.get('keyword', '')
    
    # تنظيف الكلمة من الأرقام والتركيزات لضمان اتساع نتائج البحث
    clean_keyword = re.sub(r'\d+', '', raw_keyword).strip()
    
    if not clean_keyword:
        return jsonify({"error": "Keyword is required"}), 400

    try:
        pytrends = TrendReq(hl='ar', tz=180)
        pytrends.build_payload([clean_keyword], cat=0, timeframe='now 7-d', geo='SA')
        
        # جلب البيانات على مستوى المدن (CITY) لتنحيص جدة ومكة والرياض وباقي المدن
        df = pytrends.interest_by_region(resolution='CITY', inc_low_vol=True, inc_geo_code=False)
        
        trends = {}
        if not df.empty and clean_keyword in df.columns:
            for city_name, val in df[clean_keyword].items():
                score = int(val)
                if score > 0:
                    trends[str(city_name)] = score

        return jsonify({"trends": trends})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
