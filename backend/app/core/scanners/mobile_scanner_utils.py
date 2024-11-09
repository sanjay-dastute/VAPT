"""Utility functions for mobile application security scanning"""
import os
import re
import plistlib
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

def has_root_detection(path: str) -> bool:
    """Check if Android app implements root detection"""
    patterns = [
        r'RootBeer',
        r'checkForRoot',
        r'detectRootManagement',
        r'/system/app/Superuser.apk',
        r'isDeviceRooted',
        r'test-keys',
        r'/system/bin/su',
        r'/system/xbin/su'
    ]
    return any(search_in_files(path, pattern) for pattern in patterns)

def has_jailbreak_detection(path: str) -> bool:
    """Check if iOS app implements jailbreak detection"""
    patterns = [
        r'canOpenURL.*cydia://',
        r'/Applications/Cydia.app',
        r'isJailbroken',
        r'jailbreak',
        r'/Library/MobileSubstrate/MobileSubstrate.dylib',
        r'/bin/bash',
        r'/usr/sbin/sshd',
        r'/etc/apt'
    ]
    return any(search_in_files(path, pattern) for pattern in patterns)

def is_debuggable(path: str) -> bool:
    """Check if Android app is debuggable"""
    manifest_path = find_manifest(path)
    if not manifest_path:
        return False

    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        application = root.find('application')
        if application is not None:
            return application.get('{http://schemas.android.com/apk/res/android}debuggable') == 'true'
    except Exception:
        pass
    return False

def allows_backup(path: str) -> bool:
    """Check if Android app allows backup"""
    manifest_path = find_manifest(path)
    if not manifest_path:
        return True  # Default is true if not specified

    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        application = root.find('application')
        if application is not None:
            return application.get('{http://schemas.android.com/apk/res/android}allowBackup') != 'false'
    except Exception:
        pass
    return True

def get_android_permissions(path: str) -> List[str]:
    """Get list of permissions requested by Android app"""
    manifest_path = find_manifest(path)
    if not manifest_path:
        return []

    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        return [
            perm.get('{http://schemas.android.com/apk/res/android}name').split('.')[-1]
            for perm in root.findall('.//uses-permission')
            if perm.get('{http://schemas.android.com/apk/res/android}name')
        ]
    except Exception:
        return []

def get_ios_permissions(path: str) -> List[str]:
    """Get list of permissions requested by iOS app"""
    info_plist = find_info_plist(path)
    if not info_plist:
        return []

    try:
        with open(info_plist, 'rb') as f:
            plist = plistlib.load(f)
            return [
                key for key in plist.keys()
                if key.endswith('UsageDescription')
            ]
    except Exception:
        return []

def has_ssl_pinning(path: str) -> bool:
    """Check if app implements SSL pinning"""
    patterns = [
        r'CertificatePinner',
        r'SSLCertificateChecker',
        r'pinning',
        r'X509TrustManager',
        r'CFURLSessionDelegate',
        r'URLSessionDelegate.*didReceiveChallenge',
        r'SecTrustEvaluate'
    ]
    return any(search_in_files(path, pattern) for pattern in patterns)

def allows_cleartext_traffic(path: str) -> bool:
    """Check if Android app allows cleartext traffic"""
    manifest_path = find_manifest(path)
    if not manifest_path:
        return True

    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        application = root.find('application')
        if application is not None:
            return application.get('{http://schemas.android.com/apk/res/android}usesCleartextTraffic') != 'false'
    except Exception:
        pass
    return True

def has_ats_enabled(path: str) -> bool:
    """Check if iOS app has App Transport Security enabled"""
    info_plist = find_info_plist(path)
    if not info_plist:
        return False

    try:
        with open(info_plist, 'rb') as f:
            plist = plistlib.load(f)
            ats = plist.get('NSAppTransportSecurity', {})
            return not ats.get('NSAllowsArbitraryLoads', True)
    except Exception:
        return False

def has_pie(path: str) -> bool:
    """Check if iOS binary has Position Independent Execution enabled"""
    # This would typically use otool -hv on the actual binary
    # For simulation, we'll check for presence of PIE in build settings
    return True  # Placeholder - would need actual binary analysis

def find_native_libraries(path: str) -> List[str]:
    """Find native libraries in Android app"""
    lib_dir = os.path.join(path, 'lib')
    if not os.path.exists(lib_dir):
        return []

    native_libs = []
    for root, _, files in os.walk(lib_dir):
        for file in files:
            if file.endswith('.so'):
                native_libs.append(os.path.join(root, file))
    return native_libs

def has_world_readable_files(path: str) -> bool:
    """Check for world-readable/writable files in Android app"""
    patterns = [
        r'MODE_WORLD_READABLE',
        r'MODE_WORLD_WRITEABLE',
        r'openFileOutput.*MODE_WORLD_READABLE',
        r'openFileOutput.*MODE_WORLD_WRITEABLE'
    ]
    return any(search_in_files(path, pattern) for pattern in patterns)

def uses_insecure_storage(path: str) -> bool:
    """Check for insecure data storage practices"""
    android_patterns = [
        r'getSharedPreferences',
        r'getDefaultSharedPreferences',
        r'openFileOutput',
        r'getExternalStorageDirectory',
        r'getExternalFilesDir'
    ]

    ios_patterns = [
        r'NSUserDefaults',
        r'writeToFile',
        r'NSData.*writeToFile',
        r'NSKeyedArchiver'
    ]

    return any(search_in_files(path, pattern) for pattern in android_patterns + ios_patterns)

def search_in_files(path: str, pattern: str) -> bool:
    """Search for a pattern in all files under the given path"""
    for root, _, files in os.walk(path):
        for file in files:
            try:
                with open(os.path.join(root, file), 'r', errors='ignore') as f:
                    if re.search(pattern, f.read()):
                        return True
            except Exception:
                continue
    return False

def find_manifest(path: str) -> Optional[str]:
    """Find AndroidManifest.xml in the extracted APK"""
    manifest_path = os.path.join(path, 'AndroidManifest.xml')
    return manifest_path if os.path.exists(manifest_path) else None

def find_info_plist(path: str) -> Optional[str]:
    """Find Info.plist in the extracted IPA"""
    for root, _, files in os.walk(path):
        if 'Info.plist' in files:
            return os.path.join(root, 'Info.plist')
    return None
