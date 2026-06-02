from flask import Flask, request, jsonify
from flask_cors import CORS
import akshare as ak
import pandas as pd

app = Flask(__name__)
CORS(app)  # 允许跨域访问

@app.route('/dividend', methods=['GET'])
def get_dividend():
    """获取股票分红数据"""
    stock_code = request.args.get('code')
    
    if not stock_code:
        return jsonify({'error': '缺少股票代码'}), 400
    
    # 格式化股票代码：6位数字，不足补0
    code = stock_code.zfill(6)
    
    try:
        # 方法1：尝试获取历史分红明细
        df = ak.stock_history_dividend_detail(
            indicator="分红", 
            stock=code, 
            date=""
        )
        
        if df is not None and not df.empty:
            # 提取最近一年分红
            latest = df.iloc[0]
            dividend_per_share = latest.get('派息(税前)(元)', 0)
            
            # 获取实时股价
            try:
                spot_df = ak.stock_zh_a_spot()
                stock_row = spot_df[spot_df['代码'] == code]
                if not stock_row.empty:
                    current_price = float(stock_row['最新价'].iloc[0])
                    dividend_yield = round(dividend_per_share / current_price * 100, 2) if current_price > 0 else 0
                else:
                    current_price = None
                    dividend_yield = None
            except:
                current_price = None
                dividend_yield = None
            
            # 获取股票名称
            try:
                name_df = ak.stock_individual_info_em(symbol=code)
                stock_name = name_df[name_df['item'] == '股票简称']['value'].iloc[0] if not name_df.empty else code
            except:
                stock_name = code
            
            return jsonify({
                'success': True,
                'code': code,
                'name': stock_name,
                'dividendPerShare': float(dividend_per_share) if dividend_per_share else 0,
                'currentPrice': current_price,
                'dividendYield': dividend_yield,
                'dividendHistory': df.to_dict(orient='records')[:5]  # 最近5年
            })
    
    except Exception as e:
        # 方法2：如果上述接口失败，尝试另一个接口
        try:
            df = ak.stock_fhps_detail_ths(symbol=code)
            if df is not None and not df.empty:
                # 处理数据...
                return jsonify({
                    'success': True,
                    'code': code,
                    'data': df.to_dict(orient='records')
                })
        except Exception as e2:
            pass
        
        return jsonify({
            'success': False,
            'error': f'未找到股票 {code} 的分红数据'
        }), 404

@app.route('/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)