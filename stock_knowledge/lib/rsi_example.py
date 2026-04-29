#!/usr/bin/env python3
"""
RSI三周期分析器使用示例
演示如何使用RSI自动化分析系统
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.rsi_analyzer import RSIAnalyzer


def single_stock_analysis(symbol="AAPL"):
    """单股票分析示例"""
    print("=== 单股票分析示例 ===")

    analyzer = RSIAnalyzer()

    result = analyzer.comprehensive_analysis(symbol, days=100)

    if result["success"]:
        analyzer.print_analysis_report(result)
    else:
        print(f"分析失败: {result.get('error')}")


def batch_analysis_example():
    """批量分析示例"""
    print("\n=== 批量分析示例 ===")

    analyzer = RSIAnalyzer()

    # 分析多只科技股
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

    print(f"开始批量分析 {len(symbols)} 只股票...")
    results = analyzer.batch_analysis(symbols, days=100)

    # 打印汇总报告
    print("\n📊 批量分析汇总报告")
    print("=" * 60)

    bullish_stocks = []
    bearish_stocks = []
    neutral_stocks = []

    for result in results:
        if not result["success"]:
            print(f"❌ {result['symbol']}: 分析失败")
            continue

        trend = result["trend_analysis"]
        momentum = result["momentum_analysis"]
        signals = result["trading_signals"]

        rsi_24 = trend["rsi_24"]
        alignment = momentum["alignment"]

        print(f"\n{result['symbol']} (${signals['current_price']})")
        print(f"  RSI(24): {rsi_24:.1f} | 排列: {alignment}")
        print(f"  趋势: {trend['direction']} | 风险: {trend['risk_level']}")

        # 分类股票
        if rsi_24 > 60 and alignment == "多头排列":
            bullish_stocks.append(result["symbol"])
            print("  💹 强势多头推荐")
        elif rsi_24 < 40:
            bearish_stocks.append(result["symbol"])
            print("  📉 空头环境回避")
        else:
            neutral_stocks.append(result["symbol"])
            print("  ⚖️ 中性观望")

    print("\n🏆 投资建议汇总:")
    print(f"  🟢 推荐买入: {', '.join(bullish_stocks) if bullish_stocks else '无'}")
    print(f"  🔴 谨慎持有: {', '.join(neutral_stocks) if neutral_stocks else '无'}")
    print(f"  ⚫ 建议回避: {', '.join(bearish_stocks) if bearish_stocks else '无'}")


def custom_periods_example():
    """自定义周期示例"""
    print("\n=== 自定义周期示例 ===")

    # 使用不同的RSI周期组合
    custom_analyzer = RSIAnalyzer(periods=[5, 10, 20])  # 短期组合

    symbol = "SPY"  # 标普500 ETF
    result = custom_analyzer.comprehensive_analysis(symbol, days=50)

    if result["success"]:
        print(f"使用自定义周期 [5, 10, 20] 分析 {symbol}:")
        custom_analyzer.print_analysis_report(result)
    else:
        print(f"分析失败: {result.get('error')}")


def real_time_monitoring_example():
    """实时监控示例"""
    print("\n=== 实时监控示例 ===")

    analyzer = RSIAnalyzer()

    # 监控多只股票的RSI状态
    watchlist = ["AAPL", "MSFT", "GOOGL"]

    print("实时RSI监控 (最近30天数据):")
    print("-" * 50)

    for symbol in watchlist:
        try:
            result = analyzer.comprehensive_analysis(symbol, days=30)
            if result["success"]:
                trend = result["trend_analysis"]
                momentum = result["momentum_analysis"]

                status = "🟢" if trend["rsi_24"] > 50 else "🔴"
                alignment_status = (
                    "↗️"
                    if momentum["alignment"] == "多头排列"
                    else "↘️"
                    if momentum["alignment"] == "倒挂衰减"
                    else "➡️"
                )

                print(
                    f"{status} {symbol}: RSI(24)={trend['rsi_24']:.1f} {alignment_status} {momentum['alignment']}"
                )
            else:
                print(f"❌ {symbol}: 数据获取失败")
        except Exception as e:
            print(f"❌ {symbol}: {str(e)}")


def main():
    """主函数"""
    print("🚀 RSI三周期自动化分析系统")
    print("基于多周期RSI三阶判断法")
    print("=" * 50)

    try:
        # 检查依赖
        import yfinance as yf  # noqa: F401

        print("✅ yfinance 已安装")

        # 运行示例
        single_stock_analysis(symbol="WDC")
        # batch_analysis_example()
        # custom_periods_example()
        # real_time_monitoring_example()

        print("\n🎯 使用提示:")
        print("1. 修改股票代码进行自定义分析")
        print("2. 调整days参数改变分析周期")
        print("3. 自定义periods参数使用不同RSI周期")
        print("4. 结合实际交易策略使用分析结果")

    except ImportError:
        print("❌ 缺少依赖库，请安装: pip install yfinance pandas numpy")
    except Exception as e:
        print(f"❌ 运行出错: {str(e)}")


# python ./stock_knowledge/lib/rsi_example.py
if __name__ == "__main__":
    main()
