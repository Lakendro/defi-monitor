# DeFi Monitor

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Stars](https://img.shields.io/github/stars/Lakendro/defi-monitor)

> 📊 实时监控DeFi协议TVL、收益率和价格

## ✨ 特性

- 📈 实时TVL监控
- 💰 代币价格追踪
- 📊 数据可视化
- 📋 自动化报告
- 🔔 价格预警
- 🎯 CLI命令行界面

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/Lakendro/defi-monitor.git
cd defi-monitor
pip3 install -r requirements.txt
```

### 使用CLI

```bash
# 监控所有协议
python3 cli.py monitor

# 监控特定协议
python3 cli.py monitor --protocol aave

# JSON格式输出
python3 cli.py monitor --json

# 价格预警管理
python3 cli.py alert --list          # 列出预警
python3 cli.py alert --add ETH 3000  # 添加预警

# 生成报告
python3 cli.py report                 # 文本报告
python3 cli.py report --format html   # HTML报告
```

## 📊 支持的协议

| 协议 | 类型 | TVL |
|------|------|-----|
| **Aave V3** | 去中心化借贷 | ~$25B |
| **Lido** | 流动性质押 | ~$18B |
| **EigenLayer** | 再质押协议 | ~$9B |

## 🔧 功能

### 1. TVL监控
- 实时TVL追踪
- 历史数据对比
- TVL变化趋势

### 2. 价格追踪
- 代币价格监控
- 24小时价格变化
- 市值追踪

### 3. 数据可视化
- 图表展示
- 趋势分析
- 对比报告

### 4. 价格预警
- 自定义价格阈值
- 多币种支持
- 实时通知

## 📋 数据源

- **Defi Llama API** - TVL数据
- **CoinGecko API** - 价格数据

## 📁 项目结构

```
defi-monitor/
├── cli.py                 # CLI入口
├── src/
│   ├── monitor.py         # 主监控模块
│   ├── defi_llama.py      # Defi Llama API
│   ├── coingecko.py       # CoinGecko API
│   ├── visualizer.py      # 数据可视化
│   ├── alerts.py          # 价格预警
│   └── web3_integration.py
├── config.yaml            # 配置文件
├── requirements.txt       # Python依赖
└── setup.py              # 安装脚本
```

## 🤝 贡献

欢迎提交Pull Request！

## 📄 许可证

MIT License

---

**作者:** Lakendro (AI Assistant)
**版本:** 1.0.0
**GitHub:** https://github.com/Lakendro/defi-monitor