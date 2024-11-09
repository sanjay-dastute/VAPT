from app.core.databases.vulnerability_db import VulnerabilityDatabase
from app.core.ai.vulnerability_detector import VulnerabilityDetector
from typing import Dict, Any, List
import re
import os
import asyncio
from pathlib import Path

class SourceCodeScanner:
    def __init__(self):
        self.vuln_db = VulnerabilityDatabase()
        self.ai_detector = VulnerabilityDetector()
        self.vulnerability_patterns = {
            'sql_injection': {
                'pattern': r'execute\s*\(\s*[\'"][^\']*\%s.*[\'"]\s*\)|raw_input\s*\(\s*.*\s*\)|input\s*\(\s*.*\s*\)',
                'severity': 'high',
                'description': 'Potential SQL injection vulnerability'
            },
            'xss': {
                'pattern': r'innerHTML|document\.write\s*\(|eval\s*\(.*\)|setTimeout\s*\(.*\)|setInterval\s*\(.*\)',
                'severity': 'high',
                'description': 'Potential Cross-site Scripting (XSS) vulnerability'
            },
            'hardcoded_secrets': {
                'pattern': r'password\s*=\s*[\'"][^\'"]+[\'"]\s*;|api[_-]?key\s*=\s*[\'"][^\'"]+[\'"]\s*;|secret\s*=\s*[\'"][^\'"]+[\'"]\s*;',
                'severity': 'high',
                'description': 'Hardcoded secrets detected'
            },
            'command_injection': {
                'pattern': r'exec\s*\(|system\s*\(|popen\s*\(|subprocess\.call|subprocess\.Popen|shell\s*=\s*True',
                'severity': 'critical',
                'description': 'Potential command injection vulnerability'
            },
            'path_traversal': {
                'pattern': r'\.\.\/|\.\.\\|\%2e\%2e\%2f|\%2e\%2e\/|\%2e\%2e\%5c',
                'severity': 'high',
                'description': 'Potential path traversal vulnerability'
            },
            'insecure_deserialization': {
                'pattern': r'pickle\.loads|yaml\.load|eval\(.*\)|unserialize\(',
                'severity': 'high',
                'description': 'Potential insecure deserialization'
            },
            'weak_crypto': {
                'pattern': r'md5\(|sha1\(|DES\.|RC4\.|random\.',
                'severity': 'medium',
                'description': 'Use of weak cryptographic algorithms'
            },
            'debug_code': {
                'pattern': r'console\.log\(|print\(|debug\s*=\s*true|DEBUG\s*=\s*True',
                'severity': 'low',
                'description': 'Debug code or logging statements found'
            }
        }

    async def scan(self, code_path: str, language: str = None) -> Dict[str, Any]:
        vulnerabilities = []
        try:
            if os.path.isfile(code_path):
                await self._scan_file(code_path, vulnerabilities)
            elif os.path.isdir(code_path):
                await self._scan_directory(code_path, vulnerabilities)

            return {
                'scan_summary': {
                    'total_vulnerabilities': len(vulnerabilities),
                    'high_severity': len([v for v in vulnerabilities if v['severity'] == 'high']),
                    'medium_severity': len([v for v in vulnerabilities if v['severity'] == 'medium']),
                    'low_severity': len([v for v in vulnerabilities if v['severity'] == 'low'])
                },
                'vulnerabilities': vulnerabilities
            }
        except Exception as e:
            return {'error': str(e), 'vulnerabilities': []}

    async def _scan_file(self, file_path: str, vulnerabilities: List[Dict[str, Any]]):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
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
        except Exception as e:
            vulnerabilities.append({
                'type': 'scan_error',
                'severity': 'info',
                'description': f'Error scanning file {file_path}: {str(e)}'
            })

    async def _scan_directory(self, dir_path: str, vulnerabilities: List[Dict[str, Any]]):
        language_extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'php': ['.php'],
            'csharp': ['.cs'],
            'cpp': ['.cpp', '.cc', '.cxx', '.h', '.hpp'],
            'go': ['.go'],
            'ruby': ['.rb'],
            'swift': ['.swift'],
            'kotlin': ['.kt']
        }

        for root, _, files in os.walk(dir_path):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                for lang, exts in language_extensions.items():
                    if file_ext in exts:
                        file_path = os.path.join(root, file)
                        await self._scan_file(file_path, vulnerabilities)
                        await self._analyze_language_specific(file_path, lang, vulnerabilities)
                        break
