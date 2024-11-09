"""Blockchain and Smart Contract Security Scanner"""
from typing import Dict, Any, List, Optional
import json
import os
import asyncio
from web3 import Web3
from eth_utils import to_checksum_address
from app.core.databases.vulnerability_db import VulnerabilityDatabase
from app.core.ai.vulnerability_detector import VulnerabilityDetector

class BlockchainScanner:
    def __init__(self):
        self.vuln_db = VulnerabilityDatabase()
        self.ai_detector = VulnerabilityDetector()
        # Initialize Web3 with configurable endpoint
        self.w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'))

        # Common smart contract vulnerability patterns
        self.vulnerability_patterns = {
            'reentrancy': {
                'pattern': r'\.call\.value\(|\.send\(|\.transfer\(',
                'severity': 'critical',
                'description': 'Potential reentrancy vulnerability detected'
            },
            'integer_overflow': {
                'pattern': r'\+\+|\+=|-=|\*=|\/=',
                'severity': 'high',
                'description': 'Potential integer overflow/underflow'
            },
            'tx_origin': {
                'pattern': r'tx\.origin',
                'severity': 'high',
                'description': 'Usage of tx.origin for authorization'
            },
            'unchecked_return': {
                'pattern': r'\.call\{.+\}\([^\)]*\)[^;]*[^revert]',
                'severity': 'high',
                'description': 'Unchecked return value from low-level call'
            },
            'self_destruct': {
                'pattern': r'selfdestruct|suicide',
                'severity': 'critical',
                'description': 'Self-destruct functionality present'
            }
        }

    async def scan(self, target: str, scan_type: str = 'contract') -> Dict[str, Any]:
        vulnerabilities = []

        try:
            if scan_type == 'contract':
                if not self.w3.is_address(target):
                    return {'error': 'Invalid Ethereum address', 'vulnerabilities': []}

                await self._scan_deployed_contract(target, vulnerabilities)
            elif scan_type == 'source':
                await self._scan_contract_source(target, vulnerabilities)

            # Enhance results with AI analysis
            ai_results = await self.ai_detector.analyze_smart_contract(target)
            vulnerabilities.extend(ai_results)

            return self._generate_report(vulnerabilities)

        except Exception as e:
            return {'error': str(e), 'vulnerabilities': []}

    async def _scan_deployed_contract(self, contract_address: str, vulnerabilities: List[Dict[str, Any]]):
        """Scan a deployed smart contract"""
        try:
            # Basic contract checks
            code = self.w3.eth.get_code(contract_address)
            if len(code) == 0:
                vulnerabilities.append({
                    'type': 'no_code',
                    'severity': 'high',
                    'description': 'Contract has no code (EOA or self-destructed)'
                })
                return

            # Check contract balance
            balance = self.w3.eth.get_balance(contract_address)
            if balance > 0:
                vulnerabilities.append({
                    'type': 'non_zero_balance',
                    'severity': 'info',
                    'description': f'Contract holds {self.w3.from_wei(balance, "ether")} ETH'
                })

            # Check transaction history
            tx_count = self.w3.eth.get_transaction_count(contract_address)
            if tx_count == 0:
                vulnerabilities.append({
                    'type': 'no_transactions',
                    'severity': 'medium',
                    'description': 'Contract has never been used (no transactions)'
                })

            # Run bytecode analysis
            bytecode_vulns = self._analyze_bytecode(code)
            vulnerabilities.extend(bytecode_vulns)

            # Run Mythril analysis
            await self._run_mythril_analysis(contract_address, vulnerabilities)

        except Exception as e:
            vulnerabilities.append({
                'type': 'scan_error',
                'severity': 'info',
                'description': f'Error scanning contract {contract_address}: {str(e)}'
            })

    async def _scan_contract_source(self, source_path: str, vulnerabilities: List[Dict[str, Any]]):
        """Scan smart contract source code"""
        try:
            # Run Slither analysis
            await self._run_slither_analysis(source_path, vulnerabilities)

            # Pattern-based source code analysis
            with open(source_path, 'r') as f:
                content = f.read()
                await self._analyze_source_patterns(content, source_path, vulnerabilities)

        except Exception as e:
            vulnerabilities.append({
                'type': 'scan_error',
                'severity': 'info',
                'description': f'Error scanning source {source_path}: {str(e)}'
            })

    def _analyze_bytecode(self, code: bytes) -> List[Dict[str, Any]]:
        """Analyze contract bytecode for vulnerabilities"""
        vulnerabilities = []

        # Check for delegatecall usage
        if b'delegatecall' in code:
            vulnerabilities.append({
                'type': 'delegatecall_usage',
                'severity': 'medium',
                'description': 'Contract uses delegatecall, which can be dangerous if not properly secured'
            })

        # Check for selfdestruct
        if b'selfdestruct' in code or b'suicide' in code:
            vulnerabilities.append({
                'type': 'selfdestruct_present',
                'severity': 'high',
                'description': 'Contract contains selfdestruct functionality'
            })

        # Check for unchecked external calls
        if b'call' in code and not b'require' in code:
            vulnerabilities.append({
                'type': 'unchecked_call',
                'severity': 'high',
                'description': 'Contract contains potentially unchecked external calls'
            })

        return vulnerabilities

    async def _analyze_source_patterns(self, content: str, file_path: str, vulnerabilities: List[Dict[str, Any]]):
        """Analyze source code for vulnerability patterns"""
        import re

        for vuln_type, vuln_info in self.vulnerability_patterns.items():
            matches = re.finditer(vuln_info['pattern'], content)
            for match in matches:
                line_number = content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': vuln_type,
                    'severity': vuln_info['severity'],
                    'description': vuln_info['description'],
                    'file': file_path,
                    'line': line_number,
                    'code': match.group(0)
                })

    async def _run_mythril_analysis(self, contract_address: str, vulnerabilities: List[Dict[str, Any]]):
        """Run Mythril analysis on contract"""
        try:
            process = await asyncio.create_subprocess_exec(
                'myth', 'analyze', '-a', contract_address,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()

            results = stdout.decode()
            if results:
                mythril_vulns = self._parse_mythril_results(results)
                vulnerabilities.extend(mythril_vulns)
        except Exception:
            pass

    async def _run_slither_analysis(self, source_path: str, vulnerabilities: List[Dict[str, Any]]):
        """Run Slither analysis on contract source"""
        try:
            process = await asyncio.create_subprocess_exec(
                'slither', source_path, '--json', '-',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()

            results = stdout.decode()
            if results:
                slither_vulns = self._parse_slither_results(results)
                vulnerabilities.extend(slither_vulns)
        except Exception:
            pass

    def _parse_mythril_results(self, results: str) -> List[Dict[str, Any]]:
        """Parse Mythril analysis results"""
        vulnerabilities = []
        try:
            if 'SWC-' in results:
                vulnerabilities.append({
                    'type': 'mythril_finding',
                    'severity': 'high',
                    'description': 'Mythril security issue detected',
                    'details': results
                })
        except Exception:
            pass
        return vulnerabilities

    def _parse_slither_results(self, results: str) -> List[Dict[str, Any]]:
        """Parse Slither analysis results"""
        vulnerabilities = []
        try:
            slither_results = json.loads(results)
            for finding in slither_results.get('results', {}).get('detectors', []):
                vulnerabilities.append({
                    'type': 'slither_finding',
                    'severity': finding.get('impact', 'medium'),
                    'description': finding.get('description', ''),
                    'details': finding
                })
        except Exception:
            pass
        return vulnerabilities

    def _generate_report(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive scan report"""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        vulnerability_types = {}

        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low').lower()
            vuln_type = vuln.get('type', 'unknown')

            if severity in severity_counts:
                severity_counts[severity] += 1

            vulnerability_types[vuln_type] = vulnerability_types.get(vuln_type, 0) + 1

        return {
            'scan_summary': {
                'total_vulnerabilities': len(vulnerabilities),
                'severity_distribution': severity_counts,
                'vulnerability_types': vulnerability_types
            },
            'vulnerabilities': sorted(
                vulnerabilities,
                key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}.get(
                    x.get('severity', 'low').lower(), 5
                )
            )
        }
