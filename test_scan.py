import asyncio
import aiohttp
import json
import sys

async def test_scan():
    print("Testing VAPT Scanner functionality...")

    # Test web scanner
    test_payload = {
        "target": "http://example.com",
        "options": {
            "scan_depth": "deep",
            "include_subdomains": True
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Test web scanner
            print("\nTesting Web Scanner...")
            async with session.post(
                'http://localhost:8000/scan/web',
                json=test_payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("Web Scanner Response:")
                    print(json.dumps(result, indent=2))

                    if result.get('scan_id'):
                        # Get scan results
                        async with session.get(
                            f'http://localhost:8000/scan/{result["scan_id"]}'
                        ) as results_response:
                            scan_results = await results_response.json()
                            print("\nScan Results:")
                            print(json.dumps(scan_results, indent=2))
                else:
                    print(f"Error: {response.status}")
                    print(await response.text())

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_scan())
