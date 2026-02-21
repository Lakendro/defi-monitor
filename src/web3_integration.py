"""
Web3 Integration Module

Module for interacting with blockchain using Web3.py.
"""

from typing import Dict, Optional, Any
from web3 import Web3
from web3.exceptions import TransactionNotFound, ContractLogicError


class Web3Manager:
    """Web3 manager for blockchain interactions."""

    def __init__(self, config: Dict):
        """
        Initialize Web3 manager.

        Args:
            config: Configuration dictionary
        """
        self.rpc_url = config.get('rpc_url', 'https://eth.llamarpc.com')
        self.timeout = config.get('timeout', 30)

        self.w3 = None
        self.connected = False

        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url, request_kwargs={'timeout': self.timeout}))
            self.connected = self.w3.is_connected()

            if self.connected:
                print(f"[INFO] Web3 connected to {self.rpc_url}")
            else:
                print(f"[WARN] Failed to connect to Web3 provider: {self.rpc_url}")
        except Exception as e:
            print(f"[WARN] Web3 initialization failed: {e}")

    def get_protocol_info(self, protocol_name: str) -> Optional[Dict]:
        """
        Get on-chain information for a protocol.

        Args:
            protocol_name: Protocol name (lowercase)

        Returns:
            Protocol information dictionary
        """
        if not self.connected:
            return None

        # Known contract addresses (mainnet)
        contracts = {
            'aave': {
                'address': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
                'symbol': 'AAVE',
                'decimals': 18
            },
            'lido': {
                'address': '0x5A98FcBEA516cf06857215779Fd812CA3beF1B32',
                'symbol': 'LDO',
                'decimals': 18
            },
            'eigenlayer': {
                'address': '0xEC53dF259767Ea6260C294307C9062F68e609629',  # EIGEN token
                'symbol': 'EIGEN',
                'decimals': 18
            }
        }

        protocol = contracts.get(protocol_name)

        if not protocol:
            return None

        try:
            address = self.w3.to_checksum_address(protocol['address'])

            # Get basic token info (using ERC-20 standard methods would require ABI)
            # For now, return basic info
            return {
                'address': address,
                'symbol': protocol['symbol'],
                'decimals': protocol['decimals'],
                'network': 'ethereum'
            }

        except Exception as e:
            print(f"[WARN] Error getting protocol info for {protocol_name}: {e}")
            return None

    def get_token_balance(self, address: str, token_address: str) -> Optional[float]:
        """
        Get token balance for an address.

        Args:
            address: Wallet address
            token_address: Token contract address

        Returns:
            Token balance or None
        """
        if not self.connected:
            return None

        try:
            address = self.w3.to_checksum_address(address)
            token_address = self.w3.to_checksum_address(token_address)

            # Minimal ERC-20 ABI for balanceOf
            abi = [{
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            }]

            contract = self.w3.eth.contract(address=token_address, abi=abi)
            balance = contract.functions.balanceOf(address).call()

            # Convert to float (assuming 18 decimals)
            return balance / 1e18

        except Exception as e:
            print(f"[WARN] Error getting token balance: {e}")
            return None

    def get_eth_balance(self, address: str) -> Optional[float]:
        """
        Get ETH balance for an address.

        Args:
            address: Wallet address

        Returns:
            ETH balance in ETH or None
        """
        if not self.connected:
            return None

        try:
            address = self.w3.to_checksum_address(address)
            balance_wei = self.w3.eth.get_balance(address)
            return self.w3.from_wei(balance_wei, 'ether')
        except Exception as e:
            print(f"[WARN] Error getting ETH balance: {e}")
            return None

    def get_block_number(self) -> Optional[int]:
        """
        Get current block number.

        Returns:
            Current block number or None
        """
        if not self.connected:
            return None

        try:
            return self.w3.eth.block_number
        except Exception as e:
            print(f"[WARN] Error getting block number: {e}")
            return None

    def get_gas_price(self) -> Optional[int]:
        """
        Get current gas price.

        Returns:
            Gas price in Gwei or None
        """
        if not self.connected:
            return None

        try:
            gas_price_wei = self.w3.eth.gas_price
            return self.w3.from_wei(gas_price_wei, 'gwei')
        except Exception as e:
            print(f"[WARN] Error getting gas price: {e}")
            return None

    def call_contract_method(self, contract_address: str, abi: list, method: str, *args) -> Optional[Any]:
        """
        Call a contract method.

        Args:
            contract_address: Contract address
            abi: Contract ABI
            method: Method name
            *args: Method arguments

        Returns:
            Method result or None
        """
        if not self.connected:
            return None

        try:
            contract_address = self.w3.to_checksum_address(contract_address)
            contract = self.w3.eth.contract(address=contract_address, abi=abi)
            method_obj = getattr(contract.functions, method)
            result = method_obj(*args).call()
            return result
        except Exception as e:
            print(f"[WARN] Error calling contract method: {e}")
            return None
