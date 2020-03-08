# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Control_MainWindow.py'],
             pathex=['D:\\办公软件\\Python源文件\\数据挖掘应用2'],
             binaries=[],
             datas=[],
             hiddenimports=['numpy.random.common'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Control_MainWindow',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
