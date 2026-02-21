#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeFi Monitor - 主程序
实时监控DeFi协议的TVL、收益率和价格
"""

import requests
import json
from datetime import datetime
from typing import Dict, List
import time


class DeFiMonitor:
    """DeFi数据监控器"""

    def __init__(self):
        self.protocols = {
            'aave': {
                'name': 'Aave V3',
                'defi_llama_slug': 'aave-v3',
                'coingecko_id': 'aave'
            },
            'lido': {
                'name': 'Lido',
                'defi_llama_slug': 'lido',
                'coingecko_id': 'lido-dao'
            },
            'eigenlayer': {
                'name': 'EigenLayer',
                'defi_llama_slug': 'eigenlayer',
                'coingecko_id': 'eigenlayer'
            }
        }
        self.defi_llama_base = 'https://api.llama.fi'
        self.coingecko_base = 'https://api.coingecko.com/api/v3'

    def get_tvl(self, protocol: str) -> Dict:
        """
        获取协议TVL

        Args:
            protocol: 协议名称

        Returns:
            TVL数据
        """
        slug = self.protocols[protocol]['defi_llama_slug']
        url = f"{self.defi_llama_base}/protocol/{slug}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {
                'protocol': protocol,
                'name': self.protocols[protocol]['name'],
                'tvl': data.get('tvl', 0),
                'tvl_change_1d': data.get('change_1d', 0),
                'tvl_change_7d': data.get('change_7d', 0),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'protocol': protocol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_price(self, protocol: str) -> Dict:
        """
        获取协议代币价格

        Args:
            protocol: 协议名称

        Returns:
            价格数据
        """
        coingecko_id = self.protocols[protocol]['coingecko_id']
        url = f"{self.coingecko_base}/simple/price"
        params = {
            'ids': coingecko_id,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if coingecko_id in data:
                return {
                    'protocol': protocol,
                    'name': self.protocols[protocol]['name'],
                    'price_usd': data[coingecko_id].get('usd', 0),
                    'price_change_24h': data[coingecko_id].get('usd_24h_change', 0),
                    'market_cap': data[coingecko_id].get('usd_market_cap', 0),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'protocol': protocol,
                    'error': 'Price not found',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'protocol': protocol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_all_protocols_data(self) -> List[Dict]:
        """
        获取所有协议数据

        Returns:
            所有协议数据列表
        """
        all_data = []

        for protocol in self.protocols:
            print(f"📊 正在获取 {self.protocols[protocol]['name']} 数据...")

            tvl_data = self.get_tvl(protocol)
            price_data = self.get_price(protocol)

            protocol_data = {
                'protocol': protocol,
                'name': self.protocols[protocol]['name'],
                'tvl': tvl_data.get('tvl', 0),
                'tvl_change_1d': tvl_data.get('tvl_change_1d', 0),
                'tvl_change_7d': tvl_data.get('tvl_change_7d', 0),
                'price_usd': price_data.get('price_usd', 0),
                'price_change_24h': price_data.get('price_change_24h', 0),
                'market_cap': price_data.get('market_cap', 0),
                'timestamp': datetime.now().isoformat()
            }

            all_data.append(protocol_data)
            time.sleep(1)  # 避免API限流

        return all_data

    def generate_report(self, data: List[Dict]) -> str:
        """
        生成监控报告

        Args:
            data: 协议数据列表

        Returns:
            报告文本
        """
        lines = [
            "# DeFi协议监控报告",
            "=" * 60,
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"监控协议数: {len(data)}",
            "",
            "## 协议详情",
            "-" * 60,
        ]

        for i, protocol in enumerate(data, 1):
            lines.extend([
                f"\n### {i}. {protocol['name']}",
                f"- **TVL:** ${protocol['tvl']:,.2f}",
                f"- **TVL变化 (1d):** {protocol['tvl_change_1d']:+.2f}%",
                f"- **TVL变化 (7d):** {protocol['tvl_change_7d']:+.2f}%",
                f"- **代币价格:** ${protocol['price_usd']:,.2f}",
                f"- **价格变化 (24h):** {protocol['price_change_24h']:+.2f}%",
                f"- **市值:** ${protocol['market_cap']:,.2f}",
            ])

        lines.extend([
            "",
            "=" * 60,
            "报告结束",
        ])

        return "\n".join(lines)

    def save_data(self, data: List[Dict], filename: str = None):
        """
        保存数据到文件

        Args:
            data: 协议数据列表
            filename: 文件名
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'defi_data_{timestamp}.json'

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ 数据已保存到 {filename}")


def main():
    """主函数"""
    monitor = DeFiMonitor()

    print("🔍 开始监控DeFi协议...")
    data = monitor.get_all_protocols_data()

    print(f"\n✅ 获取了 {len(data)} 个协议的数据")

    # 生成报告
    report = monitor.generate_report(data)
    print("\n" + report)

    # 保存数据
    monitor.save_data(data)

    # 保存报告
    with open('defi_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print("✅ 报告已保存到 defi_report.md")


if __name__ == '__main__':
    main()
