# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Collect everything MediaPipe needs (native libs, data files, hidden imports)
mp_datas, mp_binaries, mp_hiddenimports = collect_all("mediapipe")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=mp_binaries,
    datas=[
        ("pose_landmarker_lite.task", "."),
        *mp_datas,
    ],
    hiddenimports=mp_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PostureChecker",
    debug=False,
    strip=False,
    upx=False,
    console=False,        # no terminal window — keys are captured by the OpenCV window
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="PostureChecker",
)

app = BUNDLE(
    coll,
    name="PostureChecker.app",
    icon=None,
    bundle_identifier="com.posturechecker.app",
    info_plist={
        "NSCameraUsageDescription": "PostureChecker needs camera access to monitor your posture.",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleName": "PostureChecker",
        "LSMinimumSystemVersion": "12.0",
    },
)
