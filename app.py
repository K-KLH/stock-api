# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import akshare as ak
import pandas as pd

app = Flask(__name__)
CORS(app)

# 这是一个根路径测试接口，用来验证服务是否启动
@app.route('/')
def home():
    return "Hello from Cloud Run! The /dividend endpoint is ready."

# 这是你需要的主要分红接口
@app.route('/dividend', methods=['GET'])
def get_dividend():
    stock_code = request.args.get('code')
    if not stock_code:
        return jsonify({'error': '缺少股票代码'}), 400
    
    # 这里先放一段模拟数据，确保接口能通
    mock_data = {
        "success": True,
        "code": stock_code,
        "name": f"股票{stock_code}",
        "dividendPerShare": 2.5,
        "currentPrice": 25.0,
        "dividendYield": 10.0
    }
    return jsonify(mock_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)