"""
RSI三周期自动化分析系统
基于多周期RSI三阶判断法实现自动化趋势分析和交易信号生成

核心方法论：
- RSI(24): 确定中期趋势方向
- RSI(12): 观察中期动能
- RSI(6): 把握短期时机
"""

import warnings
from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
import yfinance as yf

warnings.filterwarnings('ignore')


class RSIAnalyzer:
    """RSI三周期自动化分析器"""

    def __init__(self, periods: List[int] = [6, 12, 24]):
        """
        初始化RSI分析器

        Args:
            periods: RSI周期列表，默认[6, 12, 24]
        """
        self.periods = sorted(periods)  # 确保从小到大排序

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        计算RSI指标

        Args:
            prices: 价格序列
            period: RSI周期

        Returns:
            RSI值序列
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def get_stock_data(self, symbol: str, days: int = 200) -> pd.DataFrame:
        """
        获取股票数据

        Args:
            symbol: 股票代码
            days: 获取天数

        Returns:
            包含OHLCV数据的DataFrame
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        try:
            # 使用收盘价计算RSI
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            if data.empty:
                raise ValueError(f"无法获取股票 {symbol} 的数据")

            return data
        except Exception as e:
            raise ValueError(f"获取股票数据失败: {str(e)}")

    def analyze_trend_direction(self, rsi_24: float) -> Dict[str, str]:
        """
        第一步：分析趋势方向 (RSI(24))

        Args:
            rsi_24: 24周期RSI值

        Returns:
            趋势分析结果
        """
        if rsi_24 > 60:
            direction = "强势多头"
            action = "只做多"
            risk_level = "低"
        elif 50 <= rsi_24 <= 60:
            direction = "温和上涨"
            action = "可持有或低吸"
            risk_level = "中"
        elif 40 <= rsi_24 < 50:
            direction = "趋势转弱"
            action = "谨慎或观望"
            risk_level = "中高"
        else:  # < 40
            direction = "中期空头"
            action = "避免做多"
            risk_level = "高"

        return {
            "direction": direction,
            "action": action,
            "risk_level": risk_level,
            "rsi_24": round(rsi_24, 2)
        }

    def analyze_momentum_alignment(self, rsi_6: float, rsi_12: float, rsi_24: float) -> Dict[str, str]:
        """
        第二步：分析动能排列

        Args:
            rsi_6, rsi_12, rsi_24: 三个周期的RSI值

        Returns:
            动能分析结果
        """
        rsi_values = [rsi_6, rsi_12, rsi_24]  # noqa: F841
        rsi_names = ["RSI(6)", "RSI(12)", "RSI(24)"] # noqa: F841

        # 判断排列状态
        if rsi_6 > rsi_12 > rsi_24:
            alignment = "多头排列"
            momentum = "动能加速"
            strength = "强劲"
        elif abs(rsi_6 - rsi_12) < 3 and abs(rsi_12 - rsi_24) < 3:
            alignment = "收敛走平"
            momentum = "趋势健康"
            strength = "稳定"
        elif rsi_6 < rsi_12 < rsi_24:
            alignment = "倒挂衰减"
            momentum = "动能放缓"
            strength = "减弱"
        else:
            alignment = "混乱排列"
            momentum = "方向不明"
            strength = "不确定"

        # 特殊警戒信号
        warning_signals = []
        if rsi_6 < rsi_12 and rsi_6 < 50:
            warning_signals.append("RSI(6)快速下穿RSI(12)并逼近50")
        if rsi_6 > 80:
            warning_signals.append("RSI(6)极端超买")

        return {
            "alignment": alignment,
            "momentum": momentum,
            "strength": strength,
            "warning_signals": warning_signals,
            "rsi_values": {
                "RSI(6)": round(rsi_6, 2),
                "RSI(12)": round(rsi_12, 2),
                "RSI(24)": round(rsi_24, 2)
            }
        }

    def find_trading_signals(self, rsi_6: float, rsi_12: float, rsi_24: float,
                           recent_prices: pd.Series) -> Dict[str, any]:
        """
        第三步：寻找交易信号

        Args:
            rsi_6, rsi_12, rsi_24: RSI值
            recent_prices: 最近价格数据

        Returns:
            交易信号分析
        """
        signals = {
            "buy_signals": [],
            "sell_signals": [],
            "hold_signals": [],
            "current_price": round(recent_prices.iloc[-1], 2)
        }

        # 判断市场环境
        is_bullish_env = rsi_24 > 50
        is_bearish_env = rsi_24 < 50

        # 买入信号
        if is_bullish_env:
            # RSI(6)回调至45-50区域
            if 45 <= rsi_6 <= 50:
                signals["buy_signals"].append("RSI(6)回调至45-50安全区域，可考虑买入")
            # 黄金组合
            if rsi_24 > 55 and rsi_6 <= 50:
                signals["buy_signals"].append("黄金组合：RSI(24)>55 + RSI(6)回踩50 = 加仓机会")
        elif is_bearish_env:
            # 极端超卖
            if rsi_6 < 20:
                signals["buy_signals"].append("极端超卖(RSI(6)<20)，可轻仓试多")

        # 卖出/回避信号
        if rsi_6 > 80:
            signals["sell_signals"].append("RSI(6)>80极端超买，警惕回落")
        if is_bearish_env and 55 <= rsi_6 <= 60:
            signals["sell_signals"].append("空头环境RSI(6)反弹至55-60遇阻")

        # 持有信号
        if is_bullish_env and rsi_6 > 50:
            signals["hold_signals"].append("多头环境RSI(6)>50，可继续持有")
        if rsi_6 < rsi_12 < rsi_24 and rsi_24 > 50:
            signals["hold_signals"].append("多头排列且RSI(24)>50，趋势健康可持有")

        return signals

    def comprehensive_analysis(self, symbol: str, days: int = 200) -> Dict[str, any]:
        """
        综合分析 - 执行完整的RSI三阶判断

        Args:
            symbol: 股票代码
            days: 分析天数

        Returns:
            完整的分析结果
        """
        try:
            # 获取数据
            data = self.get_stock_data(symbol, days)
            if len(data) < max(self.periods) + 10:
                raise ValueError("数据不足，无法进行可靠的RSI计算")

            # 计算RSI
            close_prices = data['Close']
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.iloc[:, 0]  # 取第一列（处理MultiIndex）
            rsi_values = {}
            for period in self.periods:
                rsi_values[period] = self.calculate_rsi(close_prices, period)

            # 获取最新值
            latest_rsi = {period: rsi_values[period].iloc[-1] for period in self.periods}
            rsi_6, rsi_12, rsi_24 = latest_rsi[6], latest_rsi[12], latest_rsi[24]

            # 执行三步分析
            trend_analysis = self.analyze_trend_direction(rsi_24)
            momentum_analysis = self.analyze_momentum_alignment(rsi_6, rsi_12, rsi_24)
            trading_signals = self.find_trading_signals(rsi_6, rsi_12, rsi_24, close_prices)

            # 生成总结
            summary = self._generate_summary(trend_analysis, momentum_analysis, trading_signals)

            return {
                "symbol": symbol,
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "trend_analysis": trend_analysis,
                "momentum_analysis": momentum_analysis,
                "trading_signals": trading_signals,
                "summary": summary,
                "data_points": len(data),
                "success": True
            }

        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "success": False
            }

    def _generate_summary(self, trend: Dict, momentum: Dict, signals: Dict) -> str:
        """生成分析总结"""
        summary_parts = []

        # 趋势总结
        summary_parts.append(f"趋势状态：{trend['direction']}({trend['rsi_24']})")

        # 动能总结
        summary_parts.append(f"动能状态：{momentum['alignment']}，{momentum['momentum']}")

        # 信号总结
        if signals["buy_signals"]:
            summary_parts.append(f"买入信号：{len(signals['buy_signals'])}个")
        if signals["sell_signals"]:
            summary_parts.append(f"卖出信号：{len(signals['sell_signals'])}个")
        if signals["hold_signals"]:
            summary_parts.append(f"持有信号：{len(signals['hold_signals'])}个")

        # 风险提示
        if momentum["warning_signals"]:
            summary_parts.append(f"⚠️ 警戒信号：{len(momentum['warning_signals'])}个")

        return " | ".join(summary_parts)

    def batch_analysis(self, symbols: List[str], days: int = 200) -> List[Dict]:
        """
        批量分析多个股票

        Args:
            symbols: 股票代码列表
            days: 分析天数

        Returns:
            分析结果列表
        """
        results = []
        for symbol in symbols:
            print(f"正在分析 {symbol}...")
            result = self.comprehensive_analysis(symbol, days)
            results.append(result)

        return results

    def print_analysis_report(self, analysis_result: Dict) -> None:
        """
        打印分析报告

        Args:
            analysis_result: 分析结果字典
        """
        if not analysis_result.get("success", False):
            print(f"❌ 分析失败: {analysis_result.get('error', '未知错误')}")
            return

        print(f"\n📊 {analysis_result['symbol']} RSI三周期分析报告")
        print("=" * 50)
        print(f"分析时间: {analysis_result['analysis_date']}")
        print(f"数据周期: {analysis_result['data_points']}个交易日")
        print()

        # 趋势分析
        trend = analysis_result['trend_analysis']
        print("🎯 第一步：趋势方向 (RSI(24))")
        print(f"   RSI(24): {trend['rsi_24']}")
        print(f"   趋势状态: {trend['direction']}")
        print(f"   建议操作: {trend['action']}")
        print(f"   风险等级: {trend['risk_level']}")
        print()

        # 动能分析
        momentum = analysis_result['momentum_analysis']
        print("⚡ 第二步：动能排列")
        print(f"   排列状态: {momentum['alignment']}")
        print(f"   动能状态: {momentum['momentum']}")
        print(f"   强度评估: {momentum['strength']}")
        print("   RSI数值:")
        for name, value in momentum['rsi_values'].items():
            print(f"     {name}: {value}")
        if momentum['warning_signals']:
            print("   ⚠️ 警戒信号:")
            for signal in momentum['warning_signals']:
                print(f"     • {signal}")
        print()

        # 交易信号
        signals = analysis_result['trading_signals']
        print("💰 第三步：交易信号")
        print(f"   当前价格: ${signals['current_price']}")

        if signals["buy_signals"]:
            print("   🟢 买入信号:")
            for signal in signals["buy_signals"]:
                print(f"     • {signal}")

        if signals["sell_signals"]:
            print("   🔴 卖出/回避信号:")
            for signal in signals["sell_signals"]:
                print(f"     • {signal}")

        if signals["hold_signals"]:
            print("   🟡 持有信号:")
            for signal in signals["hold_signals"]:
                print(f"     • {signal}")

        if not any(signals[k] for k in ["buy_signals", "sell_signals", "hold_signals"]):
            print("   ⚪ 无明确信号，建议观望")

        print()
        print("📋 总结")
        print(f"   {analysis_result['summary']}")
        print()


def main():
    """主函数 - 示例用法"""
    analyzer = RSIAnalyzer()

    # 单股票分析示例
    symbol = "AAPL"  # 苹果公司
    print(f"开始分析股票: {symbol}")
    result = analyzer.comprehensive_analysis(symbol)
    analyzer.print_analysis_report(result)

    # 批量分析示例
    symbols = ["MSFT", "GOOGL", "TSLA"]
    print("\n批量分析示例:")
    batch_results = analyzer.batch_analysis(symbols)

    # 打印批量结果摘要
    print("\n📈 批量分析摘要:")
    for result in batch_results:
        if result["success"]:
            print(f"✅ {result['symbol']}: {result['summary']}")
        else:
            print(f"❌ {result['symbol']}: 分析失败")


if __name__ == "__main__":
    main()