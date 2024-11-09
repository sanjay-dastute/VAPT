import aiohttp
import json
import asyncio
from typing import Dict, Any, List, Optional
import re
from urllib.parse import urljoin, urlparse
from app.core.databases.vulnerability_db import VulnerabilityDatabase
from app.core.ai.vulnerability_detector import VulnerabilityDetector

class APIScanner:
    def __init__(self):
        self.vuln_db = VulnerabilityDatabase()
        self.ai_detector = VulnerabilityDetector()
        self.common_endpoints = [
            '/api', '/v1', '/v2', '/docs', '/swagger', '/health',
            '/auth', '/login', '/users', '/admin', '/graphql'
        ]
        self.common_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        self.auth_endpoints = ['/login', '/auth', '/token']
        self.sensitive_endpoints = ['/admin', '/users', '/config']

    async def scan(self, target_url: str, method: str = None, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform comprehensive API security scanning
        """
        vulnerabilities = []
        endpoint_results = {}
        discovered_endpoints = set()

        # Normalize target URL
        if not target_url.startswith(('http://', 'https://')):
            target_url = f'https://{target_url}'

        base_url = target_url.rstrip('/')

        async with aiohttp.ClientSession() as session:
            # Discover API endpoints
            await self._discover_endpoints(session, base_url, discovered_endpoints)

            # Test discovered endpoints
            for endpoint in discovered_endpoints:
                vulnerabilities.extend(await self._test_endpoint_security(session, endpoint))

            # Perform authentication tests
            auth_vulns = await self._test_authentication(session, base_url)
            vulnerabilities.extend(auth_vulns)

            # Test rate limiting
            rate_vulns = await self._test_rate_limiting(session, base_url)
            vulnerabilities.extend(rate_vulns)

            # Test for injection vulnerabilities
            injection_vulns = await self._test_injection_vulnerabilities(session, base_url)
            vulnerabilities.extend(injection_vulns)

            # Test for sensitive data exposure
            exposure_vulns = await self._test_data_exposure(session, base_url)
            vulnerabilities.extend(exposure_vulns)

            # AI-enhanced vulnerability detection
            ai_vulns = await self.ai_detector.analyze_api_vulnerabilities(base_url, endpoint_results)
            vulnerabilities.extend(ai_vulns)

        return self._generate_report(vulnerabilities, discovered_endpoints)

    async def _discover_endpoints(self, session: aiohttp.ClientSession, base_url: str, discovered_endpoints: set) -> None:
        """Discover API endpoints through various methods"""
        # Check common endpoints
        for endpoint in self.common_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                async with session.options(url) as response:
                    if response.status != 404:
                        discovered_endpoints.add(url)
                        # Check for CORS misconfiguration
                        if '*' in response.headers.get('Access-Control-Allow-Origin', ''):
                            self.vulnerabilities.append({
                                'type': 'cors_misconfiguration',
                                'severity': 'high',
                                'endpoint': url,
                                'description': 'Wildcard CORS policy detected'
                            })
            except Exception:
                continue

        # Check for API documentation
        for docs_endpoint in ['/swagger', '/docs', '/openapi.json', '/swagger.json']:
            try:
                url = f"{base_url}{docs_endpoint}"
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        if 'swagger' in content.lower() or 'openapi' in content.lower():
                            # Parse API documentation for endpoints
                            try:
                                api_spec = json.loads(content)
                                if 'paths' in api_spec:
                                    for path in api_spec['paths']:
                                        discovered_endpoints.add(f"{base_url}{path}")
                            except json.JSONDecodeError:
                                pass
            except Exception:
                continue

    async def _test_endpoint_security(self, session: aiohttp.ClientSession, endpoint: str) -> List[Dict]:
        """Test various security aspects of an endpoint"""
        vulnerabilities = []

        for method in self.common_methods:
            try:
                async with session.request(method, endpoint) as response:
                    # Check security headers
                    security_headers = {
                        'X-Content-Type-Options': 'nosniff',
                        'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                        'Content-Security-Policy': None,
                        'X-XSS-Protection': '1; mode=block'
                    }

                    for header, expected in security_headers.items():
                        if header not in response.headers:
                            vulnerabilities.append({
                                'type': 'missing_security_header',
                                'severity': 'medium',
                                'endpoint': endpoint,
                                'method': method,
                                'description': f'Missing {header} header'
                            })
                        elif expected and response.headers[header] not in (expected if isinstance(expected, list) else [expected]):
                            vulnerabilities.append({
                                'type': 'insecure_header_value',
                                'severity': 'medium',
                                'endpoint': endpoint,
                                'method': method,
                                'description': f'Insecure {header} header value: {response.headers[header]}'
                            })

                    # Check for error exposure
                    if response.status >= 500:
                        content = await response.text()
                        if any(error in content.lower() for error in ['exception', 'error', 'stack trace', 'syntax error']):
                            vulnerabilities.append({
                                'type': 'error_exposure',
                                'severity': 'high',
                                'endpoint': endpoint,
                                'method': method,
                                'description': 'Detailed error information exposed'
                            })

            except Exception as e:
                vulnerabilities.append({
                    'type': 'connection_error',
                    'severity': 'low',
                    'endpoint': endpoint,
                    'method': method,
                    'description': f'Error accessing endpoint: {str(e)}'
                })

        return vulnerabilities

    async def _test_authentication(self, session: aiohttp.ClientSession, base_url: str) -> List[Dict]:
        """Test authentication-related vulnerabilities"""
        vulnerabilities = []

        # Test for authentication bypass
        for endpoint in self.sensitive_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        vulnerabilities.append({
                            'type': 'authentication_bypass',
                            'severity': 'critical',
                            'endpoint': url,
                            'description': 'Sensitive endpoint accessible without authentication'
                        })
            except Exception:
                continue

        # Test for weak authentication
        for auth_endpoint in self.auth_endpoints:
            url = f"{base_url}{auth_endpoint}"
            try:
                # Test common credentials
                weak_creds = [
                    {'username': 'admin', 'password': 'admin'},
                    {'username': 'test', 'password': 'test'},
                    {'username': 'user', 'password': 'password'}
                ]

                for creds in weak_creds:
                    async with session.post(url, json=creds) as response:
                        if response.status == 200:
                            vulnerabilities.append({
                                'type': 'weak_credentials',
                                'severity': 'critical',
                                'endpoint': url,
                                'description': f'Common credentials accepted: {creds["username"]}'
                            })
            except Exception:
                continue

        return vulnerabilities

    async def _test_rate_limiting(self, session: aiohttp.ClientSession, base_url: str) -> List[Dict]:
        """Test for rate limiting vulnerabilities"""
        vulnerabilities = []

        # Test rapid requests
        for endpoint in ['/login', '/api']:
            url = f"{base_url}{endpoint}"
            try:
                responses = await asyncio.gather(
                    *[session.get(url) for _ in range(50)],
                    return_exceptions=True
                )

                success_count = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
                if success_count > 45:  # If more than 90% requests succeed
                    vulnerabilities.append({
                        'type': 'missing_rate_limiting',
                        'severity': 'high',
                        'endpoint': url,
                        'description': 'No effective rate limiting detected'
                    })
            except Exception:
                continue

        return vulnerabilities

    async def _test_injection_vulnerabilities(self, session: aiohttp.ClientSession, base_url: str) -> List[Dict]:
        """Test for various injection vulnerabilities"""
        vulnerabilities = []

        # Test payloads
        injection_tests = {
            'sql': ["' OR '1'='1", "admin'--", "1; DROP TABLE users"],
            'nosql': ['{"$gt": ""}', '{"$ne": null}'],
            'command': ['; ls -la', '& dir', '| cat /etc/passwd'],
            'xml': ['<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>']
        }

        for endpoint in self.common_endpoints:
            url = f"{base_url}{endpoint}"
            for injection_type, payloads in injection_tests.items():
                for payload in payloads:
                    try:
                        async with session.post(url, json={'param': payload}) as response:
                            content = await response.text()
                            if any(error in content.lower() for error in ['error', 'exception', 'syntax']):
                                vulnerabilities.append({
                                    'type': f'{injection_type}_injection',
                                    'severity': 'critical',
                                    'endpoint': url,
                                    'payload': payload,
                                    'description': f'Potential {injection_type} injection vulnerability'
                                })
                    except Exception:
                        continue

        return vulnerabilities

    async def _test_data_exposure(self, session: aiohttp.ClientSession, base_url: str) -> List[Dict]:
        """Test for sensitive data exposure"""
        vulnerabilities = []

        sensitive_patterns = [
            r'\b[\w\.-]+@[\w\.-]+\.\w+\b',  # Email
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{16}\b',  # Credit card
            r'password|secret|key|token|credential',  # Sensitive keywords
            r'bearer\s+[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+',  # JWT
        ]

        for endpoint in self.common_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                async with session.get(url) as response:
                    content = await response.text()
                    for pattern in sensitive_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            vulnerabilities.append({
                                'type': 'sensitive_data_exposure',
                                'severity': 'critical',
                                'endpoint': url,
                                'description': f'Potential sensitive data exposure: {pattern}',
                                'evidence': match.group()[:20] + '...'  # Truncate for safety
                            })
            except Exception:
                continue

        return vulnerabilities

    def _generate_report(self, vulnerabilities: List[Dict], discovered_endpoints: set) -> Dict:
        """Generate a comprehensive scan report"""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        vulnerability_types = {}

        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low').lower()
            vuln_type = vuln.get('type', 'unknown')

            if severity in severity_counts:
                severity_counts[severity] += 1

            vulnerability_types[vuln_type] = vulnerability_types.get(vuln_type, 0) + 1

        return {
            'scan_summary': {
                'total_endpoints_discovered': len(discovered_endpoints),
                'total_vulnerabilities': len(vulnerabilities),
                'severity_distribution': severity_counts,
                'vulnerability_types': vulnerability_types
            },
            'endpoints': list(discovered_endpoints),
            'vulnerabilities': sorted(
                vulnerabilities,
                key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.get('severity', 'low').lower(), 4)
            )
        }
