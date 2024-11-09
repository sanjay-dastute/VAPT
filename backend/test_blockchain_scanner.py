import asyncio
from app.core.scanners.blockchain_scanner import BlockchainScanner

async def test_scanner():
    scanner = BlockchainScanner()
    # Test with USDT contract address
    result = await scanner.scan('0xdAC17F958D2ee523a2206206994597C13D831ec7')
    print("Scan Results:", result)

if __name__ == "__main__":
    asyncio.run(test_scanner())
