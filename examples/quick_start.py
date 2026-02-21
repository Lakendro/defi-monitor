#!/usr/bin/env python3
"""
Quick Start Example

Simple script demonstrating basic DeFi monitoring functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_fetcher import DataFetcher
from src.defi_llama import DefiLlamaAPI
from src.coingecko import CoinGeckoAPI


def quick_monitor():
    """Quick monitoring example."""
    
    print("="*60)
    print("DeFi Monitor - Quick Start Example")
    print("="*60)
    print()
    
    # Initialize APIs
    defillama = DefiLlamaAPI({})
    coingecko = CoinGeckoAPI({})
    
    # Monitor Aave
    print("Fetching Aave data...")
    print("-" * 40)
    
    # Get TVL from DefiLlama
    aave_tvl = defillama.get_protocol_tvl('aave-v3')
    if aave_tvl:
        print(f"TVL: ${aave_tvl['tvl']:,.0f}")
        if aave_tvl.get('change_24h'):
            print(f"24h Change: {aave_tvl['change_24h']:+.2f}%")
    
    # Get price from CoinGecko
    aave_price = coingecko.get_token_price('aave')
    if aave_price:
        print(f"Price: ${aave_price['price']:.4f}")
        if aave_price.get('change_24h'):
            print(f"24h Price Change: {aave_price['change_24h']:+.2f}%")
    
    print()
    
    # Monitor Lido
    print("Fetching Lido data...")
    print("-" * 40)
    
    lido_tvl = defillama.get_protocol_tvl('lido')
    if lido_tvl:
        print(f"TVL: ${lido_tvl['tvl']:,.0f}")
        if lido_tvl.get('change_24h'):
            print(f"24h Change: {lido_tvl['change_24h']:+.2f}%")
    
    lido_price = coingecko.get_token_price('lido-dao')
    if lido_price:
        print(f"Price: ${lido_price['price']:.4f}")
        if lido_price.get('change_24h'):
            print(f"24h Price Change: {lido_price['change_24h']:+.2f}%")
    
    print()
    
    # Monitor EigenLayer
    print("Fetching EigenLayer data...")
    print("-" * 40)
    
    eigen_tvl = defillama.get_protocol_tvl('eigenlayer')
    if eigen_tvl:
        print(f"TVL: ${eigen_tvl['tvl']:,.0f}")
        if eigen_tvl.get('change_24h'):
            print(f"24h Change: {eigen_tvl['change_24h']:+.2f}%")
    
    eigen_price = coingecko.get_token_price('eigenlayer')
    if eigen_price:
        print(f"Price: ${eigen_price['price']:.4f}")
        if eigen_price.get('change_24h'):
            print(f"24h Price Change: {eigen_price['change_24h']:+.2f}%")
    
    print()
    print("="*60)
    print("Quick monitoring completed!")
    print("="*60)


if __name__ == '__main__':
    quick_monitor()
