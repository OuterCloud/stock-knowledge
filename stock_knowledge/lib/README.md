# RSI三周期自动化分析系统

基于多周期RSI三阶判断法的自动化股票趋势分析工具。

## 📋 核心方法论

**"长定方向，中观节奏，短找时机"**

- **RSI(24)**: 确定中期趋势方向
- **RSI(12)**: 观察中期动能变化
- **RSI(6)**: 把握短期买卖时机

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r lib/requirements.txt
```

### 2. 基本用法

```python
from lib.rsi_analyzer import RSIAnalyzer

# 创建分析器
analyzer = RSIAnalyzer()

# 分析单只股票
result = analyzer.comprehensive_analysis("AAPL")
analyzer.print_analysis_report(result)

# 批量分析
symbols = ["AAPL", "MSFT", "GOOGL"]
results = analyzer.batch_analysis(symbols)
```

### 3. 运行示例

```bash
cd /path/to/stock_knowledge
python lib/rsi_example.py
```

## 📊 分析结果说明

### 趋势方向 (RSI(24))
- **> 60**: 强势多头，只做多
- **50-60**: 温和上涨，可持有或低吸
- **40-50**: 趋势转弱，谨慎观望
- **< 40**: 中期空头，避免做多

### 动能排列
- **多头排列**: RSI(6) > RSI(12) > RSI(24) - 动能加速
- **收敛走平**: 三者接近 - 趋势健康
- **倒挂衰减**: RSI(6) < RSI(12) < RSI(24) - 动能放缓

### 交易信号
- **买入信号**: RSI(6)回调至45-50区域
- **卖出信号**: RSI(6)>80极端超买
- **黄金组合**: RSI(24)>55 + RSI(6)回踩50

## 🔧 高级用法

### 自定义RSI周期

```python
# 使用不同的周期组合
analyzer = RSIAnalyzer(periods=[5, 10, 20])
```

### 分析不同时间周期

```python
# 分析最近100天的走势
result = analyzer.comprehensive_analysis("AAPL", days=100)
```

### 批量监控

```python
# 实时监控多只股票
watchlist = ["AAPL", "MSFT", "TSLA", "NVDA"]
results = analyzer.batch_analysis(watchlist, days=30)
```

## 📁 文件结构

```
lib/
├── __init__.py          # 包初始化
├── rsi_analyzer.py      # 核心分析器
├── rsi_example.py       # 使用示例
└── requirements.txt     # 依赖列表
```

## ⚠️ 注意事项

1. **数据依赖**: 需要网络连接获取Yahoo Finance数据
2. **分析周期**: 建议至少使用100天数据保证RSI计算准确性
3. **市场适用性**: 适用于美股、A股等主流市场
4. **风险提示**: 技术分析仅供参考，不构成投资建议

## 🎯 投资建议

- RSI(24) > 50的环境下积极做多
- 关注三周期排列状态变化
- 结合价格结构和成交量验证信号
- 严格执行止损，避免过度集中持仓

## 📈 扩展功能

未来可扩展的功能：
- 实时数据流分析
- 多时间框架协同分析
- 自定义指标组合
- 自动化交易信号生成
- 历史回测验证