from flask import Flask, request, jsonify
from pytrends.request import TrendReq

app = Flask(__name__)

@app.route('/trends', methods=['GET'])
def get_trends():
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    try:
        pytrends = TrendReq(hl='ar', tz=-180, timeout=(10,25))
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='SA', gprop='')
        
        # استخراج الاهتمام على مستوى المدن (CITY) بدلاً من المناطق الإدارية (REGION)
        data = pytrends.interest_by_region(resolution='CITY', inc_low_vol=True, inc_geo_code=False)
        
        if data.empty or keyword not in data.columns:
            return jsonify({"status": "no_data"}), 200

        result = data[keyword].to_dict()
        
        # قائمة المدن الكبرى التي نريد عرض نتائجها في التطبيق
        target_cities = ["الرياض", "جدة", "مكة المكرمة", "الدمام", "المدينة المنورة", "القصيم", "عسير"]
        filtered_result = {city: int(result.get(city, 0)) for city in target_cities}

        return jsonify({
            "keyword": keyword,
            "trends": filtered_result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
