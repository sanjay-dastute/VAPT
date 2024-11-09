import asyncio
import aiohttp
import sys
import platform
import os
import json

async def test_scanner():
    print(f"Testing VAPT Scanner on {platform.system()}")
    print("System Information:")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python Version: {sys.version}")

    # Test backend connectivity
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/docs') as response:
                assert response.status == 200
                print("✓ Backend API is running")
    except Exception as e:
        print(f"✗ Backend API test failed: {str(e)}")
        return False

    # Test scanning functionality
    test_cases = [
        {
            "scan_type": "web",
            "target": "http://example.com"
        },
        {
            "scan_type": "api",
            "target": "http://api.example.com"
        },
        {
            "scan_type": "source_code",
            "target": "./backend"
        }
    ]

    for test_case in test_cases:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'http://localhost:8000/scan/{test_case["scan_type"]}',
                    json={"target": test_case["target"]}
                ) as response:
                    assert response.status in [200, 201]
                    print(f"✓ {test_case['scan_type']} scanner test passed")
        except Exception as e:
            print(f"✗ {test_case['scan_type']} scanner test failed: {str(e)}")
            return False

    print("\nAll tests completed successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(test_scanner())
