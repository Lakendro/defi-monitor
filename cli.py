#!/usr/bin/env python3
"""
DeFi Monitor - 主入口CLI

使用方法:
    python3 cli.py monitor      # 监控DeFi协议数据
    python3 cli.py alert        # 设置价格预警
    python3 cli.py report       # 生成报告
    python3 cli.py config       # 配置管理
"""

import argparse
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from monitor import DeFiMonitor
from alerts import PriceAlerts
from visualizer import Visualizer
from data_fetcher import DataFetcher
from defi_llama import DefiLlamaClient
from coingecko import CoinGeckoClient


def main():
    parser = argparse.ArgumentParser(
        description="DeFi Monitor - 实时监控DeFi协议TVL和收益率",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 cli.py monitor           # 获取所有协议数据
  python3 cli.py monitor --protocol aave  # 只获取Aave数据
  python3 cli.py alert --list      # 列出所有预警
  python3 cli.py alert --add ETH 3000  # 添加ETH价格预警
  python3 cli.py report            # 生成完整报告
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用的命令")
    
    # monitor命令
    monitor_parser = subparsers.add_parser("monitor", help="监控DeFi协议数据")
    monitor_parser.add_argument("--protocol", "-p", choices=["aave", "lido", "eigenlayer", "all"],
                                default="all", help="选择要监控的协议")
    monitor_parser.add_argument("--json", "-j", action="store_true", help="JSON格式输出")
    monitor_parser.add_argument("--save", "-s", help="保存到指定文件")
    
    # alert命令
    alert_parser = subparsers.add_parser("alert", help="价格预警管理")
    alert_parser.add_argument("--list", "-l", action="store_true", help="列出所有预警")
    alert_parser.add_argument("--add", nargs=2, metavar=("TOKEN", "PRICE"), help="添加预警")
    alert_parser.add_argument("--remove", "-r", type=int, help="删除指定ID的预警")
    
    # report命令
    report_parser = subparsers.add_parser("report", help="生成监控报告")
    report_parser.add_argument("--format", "-f", choices=["text", "json", "html"], 
                               default="text", help="报告格式")
    report_parser.add_argument("--output", "-o", help="输出到文件")
    
    # config命令
    config_parser = subparsers.add_parser("config", help="配置管理")
    config_parser.add_argument("--show", action="store_true", help="显示当前配置")
    config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="设置配置")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行对应的命令
    if args.command == "monitor":
        monitor_protocols(args)
    elif args.command == "alert":
        manage_alerts(args)
    elif args.command == "report":
        generate_report(args)
    elif args.command == "config":
        manage_config(args)


def monitor_protocols(args):
    """监控DeFi协议"""
    monitor = DeFiMonitor()
    
    if args.protocol == "all":
        data = monitor.get_all_protocols_data()
    else:
        data = [monitor.get_tvl(args.protocol), monitor.get_price(args.protocol)]
    
    if args.json:
        import json
        print(json.dumps(data, indent=2))
    else:
        for d in data:
            print(f"\n{d.get('name', 'Unknown')}:")
            print(f"  TVL: ${d.get('tvl', 0):,.2f}")
            print(f"  Price: ${d.get('price_usd', 0):,.2f}")
    
    if args.save:
        import json
        with open(args.save, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✅ 数据已保存到 {args.save}")


def manage_alerts(args):
    """管理价格预警"""
    alerts = PriceAlerts()
    
    if args.list:
        all_alerts = alerts.list_alerts()
        if not all_alerts:
            print("暂无预警规则")
            return
        for a in all_alerts:
            print(f"ID: {a['id']} | {a['token']} @ ${a['price']} | {a['direction']}")
    
    elif args.add:
        token, price = args.add
        alerts.add_alert(token.upper(), float(price))
        print(f"✅ 已添加 {token.upper()} 预警，价格 ${price}")
    
    elif args.remove:
        alerts.remove_alert(args.remove)
        print(f"✅ 已删除ID为 {args.remove} 的预警")


def generate_report(args):
    """生成报告"""
    monitor = DeFiMonitor()
    data = monitor.get_all_protocols_data()
    visualizer = Visualizer({})
    
    if args.format == "json":
        import json
        output = json.dumps(data, indent=2)
    elif args.format == "html":
        output = visualizer.generate_html_report(data)
    else:
        output = monitor.generate_report(data)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"✅ 报告已保存到 {args.output}")
    else:
        print(output)


def manage_config(args):
    """配置管理"""
    import yaml
    
    config_path = Path(__file__).parent / "config.yaml"
    
    if args.show:
        if config_path.exists():
            with open(config_path) as f:
                print(f.read())
        else:
            print("配置文件不存在")
    
    elif args.set:
        key, value = args.set
        config = {}
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
        
        config[key] = value
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        print(f"✅ 已设置 {key} = {value}")


if __name__ == "__main__":
    main()