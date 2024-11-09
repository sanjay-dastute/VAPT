import os
import zipfile
import subprocess
import json
import re
import aiohttp
from typing import Dict, Any, List, Optional, Tuple
from app.core.databases.vulnerability_db import VulnerabilityDatabase
from app.core.ai.vulnerability_detector import VulnerabilityDetector
from app.core.scanners.mobile_scanner_utils import *

class MobileScanner:
    def __init__(self):
        self.vuln_db = VulnerabilityDatabase()
        self.ai_detector = VulnerabilityDetector()
        self.android_permissions = {
            'dangerous': [
                'READ_CALENDAR', 'WRITE_CALENDAR',
                'CAMERA',
                'READ_CONTACTS', 'WRITE_CONTACTS', 'GET_ACCOUNTS',
                'ACCESS_FINE_LOCATION', 'ACCESS_COARSE_LOCATION',
                'RECORD_AUDIO',
                'READ_PHONE_STATE', 'READ_PHONE_NUMBERS', 'CALL_PHONE',
                'READ_CALL_LOG', 'WRITE_CALL_LOG', 'ADD_VOICEMAIL',
                'USE_SIP', 'PROCESS_OUTGOING_CALLS',
                'BODY_SENSORS',
                'SEND_SMS', 'RECEIVE_SMS', 'READ_SMS', 'RECEIVE_WAP_PUSH',
                'RECEIVE_MMS',
                'READ_EXTERNAL_STORAGE', 'WRITE_EXTERNAL_STORAGE'
            ],
            'signature': [
                'INSTALL_PACKAGES',
                'DELETE_PACKAGES',
                'BATTERY_STATS',
                'PACKAGE_USAGE_STATS',
                'BIND_ACCESSIBILITY_SERVICE',
                'BIND_INPUT_METHOD'
            ]
        }

        self.ios_permissions = [
            'NSCameraUsageDescription',
            'NSPhotoLibraryUsageDescription',
            'NSLocationWhenInUseUsageDescription',
            'NSLocationAlwaysUsageDescription',
            'NSMicrophoneUsageDescription',
            'NSContactsUsageDescription',
            'NSCalendarsUsageDescription',
            'NSRemindersUsageDescription',
            'NSMotionUsageDescription',
            'NSHealthUpdateUsageDescription',
            'NSHealthShareUsageDescription',
            'NSBluetoothPeripheralUsageDescription',
            'NSAppleMusicUsageDescription',
            'NSSpeechRecognitionUsageDescription',
            'NSFaceIDUsageDescription'
        ]

    async def scan(self, app_path: str, platform: str = None) -> Dict[str, Any]:
        vulnerabilities = []

        try:
            if not platform:
                platform = self._detect_platform(app_path)

            extract_dir = self._extract_app(app_path)

            vulnerabilities.extend(self._check_basic_security(extract_dir, platform))
            vulnerabilities.extend(self._check_permissions(extract_dir, platform))
            vulnerabilities.extend(self._check_network_security(extract_dir, platform))
            vulnerabilities.extend(self._check_binary_security(extract_dir, platform))
            vulnerabilities.extend(self._check_data_storage(extract_dir, platform))

            ai_vulns = await self.ai_detector.analyze_mobile_vulnerabilities(
                app_binary=open(app_path, 'rb').read(),
                metadata={'platform': platform, 'extracted_files': os.listdir(extract_dir)}
            )
            vulnerabilities.extend(ai_vulns)

        except Exception as e:
            return {
                'error': str(e),
                'vulnerabilities': []
            }

        return self._generate_report(vulnerabilities)

    def _detect_platform(self, app_path: str) -> str:
        if app_path.endswith('.apk'):
            return 'android'
        elif app_path.endswith('.ipa'):
            return 'ios'
        raise ValueError("Unsupported application format. Must be .apk or .ipa")

    def _extract_app(self, app_path: str) -> str:
        extract_dir = f"/tmp/mobile_scan_{os.path.basename(app_path)}"
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(app_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        return extract_dir

    def _check_basic_security(self, path: str, platform: str) -> List[Dict[str, Any]]:
        vulnerabilities = []

        if platform == 'android':
            if not self._has_root_detection(path):
                vulnerabilities.append({
                    'type': 'missing_root_detection',
                    'severity': 'high',
                    'description': 'No root detection mechanism found',
                    'recommendation': 'Implement root detection to prevent running on rooted devices'
                })

            if self._is_debuggable(path):
                vulnerabilities.append({
                    'type': 'debuggable_application',
                    'severity': 'critical',
                    'description': 'Application is debuggable',
                    'recommendation': 'Disable debugging in release builds'
                })

        elif platform == 'ios':
            if not self._has_jailbreak_detection(path):
                vulnerabilities.append({
                    'type': 'missing_jailbreak_detection',
                    'severity': 'high',
                    'description': 'No jailbreak detection mechanism found',
                    'recommendation': 'Implement jailbreak detection'
                })

        return vulnerabilities

    def _check_permissions(self, path: str, platform: str) -> List[Dict[str, Any]]:
        vulnerabilities = []

        if platform == 'android':
            permissions = self._get_android_permissions(path)
            dangerous_count = sum(1 for p in permissions if p in self.android_permissions['dangerous'])

            if dangerous_count > 5:
                vulnerabilities.append({
                    'type': 'excessive_permissions',
                    'severity': 'high',
                    'description': f'Application requests {dangerous_count} dangerous permissions',
                    'details': {'permissions': permissions},
                    'recommendation': 'Review and remove unnecessary dangerous permissions'
                })

        elif platform == 'ios':
            permissions = self._get_ios_permissions(path)
            if len(permissions) > 5:
                vulnerabilities.append({
                    'type': 'excessive_permissions',
                    'severity': 'medium',
                    'description': f'Application requests {len(permissions)} privacy-sensitive permissions',
                    'details': {'permissions': permissions},
                    'recommendation': 'Review and remove unnecessary permission requests'
                })

        return vulnerabilities

    def _check_network_security(self, path: str, platform: str) -> List[Dict[str, Any]]:
        vulnerabilities = []

        if platform == 'android':
            if not self._has_ssl_pinning(path):
                vulnerabilities.append({
                    'type': 'missing_ssl_pinning',
                    'severity': 'high',
                    'description': 'No SSL certificate pinning implemented',
                    'recommendation': 'Implement SSL certificate pinning'
                })

            if self._allows_cleartext_traffic(path):
                vulnerabilities.append({
                    'type': 'cleartext_traffic_allowed',
                    'severity': 'high',
                    'description': 'Application allows cleartext HTTP traffic',
                    'recommendation': 'Disable cleartext traffic and use HTTPS only'
                })

        elif platform == 'ios':
            if not self._has_ats_enabled(path):
                vulnerabilities.append({
                    'type': 'ats_disabled',
                    'severity': 'high',
                    'description': 'App Transport Security is disabled',
                    'recommendation': 'Enable App Transport Security'
                })

        return vulnerabilities

    def _check_binary_security(self, path: str, platform: str) -> List[Dict[str, Any]]:
        vulnerabilities = []

        if platform == 'android':
            native_libs = self._find_native_libraries(path)
            if native_libs:
                vulnerabilities.append({
                    'type': 'native_code_usage',
                    'severity': 'info',
                    'description': 'Application uses native libraries',
                    'details': {'libraries': native_libs}
                })

        elif platform == 'ios':
            if not self._has_pie(path):
                vulnerabilities.append({
                    'type': 'missing_pie',
                    'severity': 'high',
                    'description': 'Binary is not compiled with Position Independent Execution',
                    'recommendation': 'Enable PIE in build settings'
                })

        return vulnerabilities

    def _check_data_storage(self, path: str, platform: str) -> List[Dict[str, Any]]:
        vulnerabilities = []

        if platform == 'android':
            if self._has_world_readable_files(path):
                vulnerabilities.append({
                    'type': 'insecure_file_permissions',
                    'severity': 'high',
                    'description': 'Files with insecure permissions detected',
                    'recommendation': 'Use proper file permissions'
                })

        elif platform == 'ios':
            if self._uses_insecure_storage(path):
                vulnerabilities.append({
                    'type': 'insecure_data_storage',
                    'severity': 'high',
                    'description': 'Insecure data storage methods detected',
                    'recommendation': 'Use Keychain for sensitive data storage'
                })

        return vulnerabilities

    def _generate_report(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
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
