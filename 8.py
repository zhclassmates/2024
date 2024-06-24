import pandas as pd
from pycoingecko import CoinGeckoAPI
import time

# 初始化CoinGecko API客户端
cg = CoinGeckoAPI()

# 定义时间范围
date_start = '2024-01-11'
date_end = '2024-03-14'

# 定义日志文件
log_file = 'process_log.txt'

# 日志记录函数
def log_message(message):
    print(message)
    with open(log_file, 'a') as log:
        log.write(message + '\n')

# 获取代币的市场数据
def get_market_data(token_id, vs_currency='usd'):
    data = cg.get_coin_market_chart_range_by_id(
        id=token_id,
        vs_currency=vs_currency,
        from_timestamp=pd.Timestamp(date_start).timestamp(),
        to_timestamp=pd.Timestamp(date_end).timestamp()
    )
    return data

# 计算涨幅
def calculate_increase(prices):
    if not prices:
        return None
    start_price = prices[0][1]
    end_price = prices[-1][1]
    increase = (end_price - start_price) / start_price * 100
    return increase

# 获取前1200个代币列表
log_message("正在获取前1200个代币列表...")
all_coins = cg.get_coins_markets(vs_currency='usd', per_page=250, page=2) + \
            cg.get_coins_markets(vs_currency='usd', per_page=250, page=3) + \
            cg.get_coins_markets(vs_currency='usd', per_page=250, page=4) + \
            cg.get_coins_markets(vs_currency='usd', per_page=250, page=5) 
        
log_message(f"共获取到 {len(all_coins)} 种代币")

# 初始化结果列表
results = []

# 获取BTC数据并计算涨幅
log_message("正在获取BTC数据...")
btc_data = get_market_data('bitcoin')
btc_prices = btc_data['prices']
btc_increase = calculate_increase(btc_prices)
log_message(f"BTC的涨幅是: {btc_increase:.2f}%")

# 创建或清空结果文件
with open('exceed_btc.csv', 'w') as csvfile:
    csvfile.write("Token,Original Rank,Increase (%)\n")

with open('exceed_btc.txt', 'w') as txtfile:
    txtfile.write(f"BTC的涨幅是: {btc_increase:.2f}%\n")
    txtfile.write("超过BTC涨幅的代币:\n")

# 遍历所有代币并计算涨幅
for i, coin in enumerate(all_coins, start=1):
    token_id = coin['id']
    try:
        log_message(f"正在处理第 {i}/{len(all_coins)} 个代币: {coin['name']} ({token_id})")
        token_data = get_market_data(token_id)
        token_prices = token_data['prices']
        increase = calculate_increase(token_prices)
        if increase is not None:
            results.append((coin['name'], i, increase))

            # 按涨幅降序排序
            results.sort(key=lambda x: x[2], reverse=True)

            # 及时写入CSV文件
            with open('exceed_btc.csv', 'w') as csvfile:
                csvfile.write("Token,Original Rank,Increase (%)\n")
                for token, rank, inc in results:
                    csvfile.write(f"{token},{rank},{inc:.2f}\n")

            # 及时写入TXT文件
            with open('exceed_btc.txt', 'w') as txtfile:
                txtfile.write(f"BTC的涨幅是: {btc_increase:.2f}%\n")
                txtfile.write("超过BTC涨幅的代币:\n")
                for rank, (token, original_rank, inc) in enumerate(results, start=1):
                    txtfile.write(f"{rank}. {token} (原始排名: {original_rank}): {inc:.2f}%\n")
        time.sleep(1)  # 为了避免API速率限制，每次请求后暂停1秒
    except Exception as e:
        log_message(f"获取 {token_id} 数据时出错: {e}")

log_message("程序执行完毕，结果已生成。")
