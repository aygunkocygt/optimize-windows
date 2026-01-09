#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OneDrive Optimizer (agresif)

- Startup/task/policy zaten ayrı yerlerde ele alınıyor.
- Burada amaç OneDrive'ı tamamen kaldırmak (kullanıcı isteği).

Not: Uninstall işlemi çoğu sistemde geri alınabilir (OneDriveSetup.exe /install),
ama her zaman birebir aynı şekilde dönmeyebilir.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Dict, List


class OneDriveOptimizer:
    def __init__(self):
        self.changes: List[str] = []

    def _onedrive_setup_paths(self) -> List[Path]:
        windir = os.environ.get("WINDIR", r"C:\Windows")
        return [
            Path(windir) / "SysWOW64" / "OneDriveSetup.exe",
            Path(windir) / "System32" / "OneDriveSetup.exe",
        ]

    def _onedrive_exe_paths(self) -> List[Path]:
        localappdata = os.environ.get("LOCALAPPDATA", "")
        programdata = os.environ.get("PROGRAMDATA", "")
        return [
            Path(localappdata) / "Microsoft" / "OneDrive" / "OneDrive.exe",
            Path(programdata) / "Microsoft OneDrive" / "OneDrive.exe",
        ]

    def backup_state(self) -> Dict[str, bool]:
        installed = any(p.exists() for p in self._onedrive_exe_paths()) or any(p.exists() for p in self._onedrive_setup_paths())
        return {"was_installed": bool(installed)}

    def optimize(self) -> List[str]:
        changes: List[str] = []
        print("   📋 OneDrive kaldırılıyor (agresif)...")

        # OneDrive prosesini kapat
        try:
            subprocess.run(["taskkill", "/f", "/im", "OneDrive.exe"], capture_output=True, text=True, timeout=10, check=False)
        except Exception:
            pass

        # Uninstall
        setup_paths = [p for p in self._onedrive_setup_paths() if p.exists()]
        if not setup_paths:
            print("      ℹ️  OneDriveSetup.exe bulunamadı (atlandı)")
            return changes

        ok = False
        for setup in setup_paths:
            try:
                res = subprocess.run([str(setup), "/uninstall"], capture_output=True, text=True, timeout=120, check=False)
                if res.returncode == 0:
                    ok = True
            except Exception:
                continue

        if ok:
            changes.append("OneDrive kaldırıldı (OneDriveSetup.exe /uninstall)")
            print("      ✅ OneDrive kaldırıldı")
        else:
            print("      ⚠️  OneDrive kaldırılamadı (bazı sistemlerde kısıtlanabilir)")

        self.changes.extend(changes)
        return changes


