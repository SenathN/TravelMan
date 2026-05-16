
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('intents.json', '.'), ('nltk_data', 'nltk_data'), ('data/seed_chatbot.db', 'data')],
    hiddenimports=[
        'nltk.chunk.named_entity', 
        'nltk.tokenize.punkt', 
        'nltk.corpus.wordnet',
        'tkinter',
        'tkinter.messagebox',
        'tkinter.scrolledtext'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [], # No binaries/datas here for onedir
    exclude_binaries=True,
    name='TravelMate_v1.0.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disabled UPX to prevent Antivirus false positives
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False, # Disabled UPX
    upx_exclude=[],
    name='TravelMate_v1.0.0',
)
