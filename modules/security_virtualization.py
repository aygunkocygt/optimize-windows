#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Güvenlik / Virtualization Tweak'leri (Opsiyonel)

- VBS (Virtualization-Based Security) kapatma
- Memory Integrity (HVCI) kapatma
- Credential Guard kapatma

NOT:
Bu ayarlar güvenliği düşürür ve bazı geliştirme özelliklerini etkileyebilir (WSL2/Hyper-V/Android Subsystem).
Bu yüzden optimize.py tarafında kullanıcı onayıyla çalıştırılması hedeflenir.
"""

from __future__ import annotations

import subprocess
import winreg
from typing import List


class SecurityVirtualizationOptimizer:
    """VBS/HVCI/Credential Guard kapatma (opsiyonel)."""

    def __init__(self):
        self.changes: List[str] = []

        # Opt-in flags (optimize.py tarafında set edilebilir)
        self.disable_vbs: bool = False
        self.disable_hvci: bool = False
        self.disable_credential_guard: bool = False

        # Çok agresif: Hypervisor'ı boot seviyesinde kapatır (WSL2/Hyper-V'yi kırabilir).
        self.disable_hypervisor_launch: bool = False

    def _set_reg_dword(self, root, subkey: str, name: str, value: int) -> bool:
        try:
            key = winreg.CreateKey(root, subkey)
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"      ⚠️  REG {subkey}\\{name}: {e}")
            return False

    def _bcdedit_set(self, args: List[str]) -> bool:
        """
        bcdedit ile boot config değiştirir.
        Not: Yönetici gerekir. Bazı sistemlerde Secure Boot/BitLocker nedeniyle kısıtlanabilir.
        """
        try:
            result = subprocess.run(
                ["bcdedit", *args],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True
            # bcdedit bazen stderr'e yazar
            print(f"      ⚠️  bcdedit {' '.join(args)}: {result.stderr.strip() or result.stdout.strip()}")
            return False
        except Exception as e:
            print(f"      ⚠️  bcdedit {' '.join(args)}: {e}")
            return False

    def apply_vbs_off(self) -> List[str]:
        """
        VBS/HVCI/Credential Guard kapatma uygular.
        Değişikliklerin tam etkisi için restart gerekebilir.
        """
        changes: List[str] = []
        print("   📋 VBS/HVCI/Credential Guard ayarları uygulanıyor...")

        # VBS
        if self.disable_vbs:
            # Device Guard / VBS
            if self._set_reg_dword(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\DeviceGuard",
                "EnableVirtualizationBasedSecurity",
                0,
            ):
                changes.append("VBS kapatıldı: EnableVirtualizationBasedSecurity=0")
                print("      ✅ VBS kapatıldı (EnableVirtualizationBasedSecurity)")

            # Bazı senaryolarda platform güvenlik özellikleri zorlanır
            if self._set_reg_dword(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\DeviceGuard",
                "RequirePlatformSecurityFeatures",
                0,
            ):
                changes.append("VBS kapatıldı: RequirePlatformSecurityFeatures=0")
                print("      ✅ VBS platform gereksinimleri kapatıldı")

        # HVCI (Memory Integrity)
        if self.disable_hvci:
            if self._set_reg_dword(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity",
                "Enabled",
                0,
            ):
                changes.append("HVCI kapatıldı: HVCI Enabled=0")
                print("      ✅ Memory Integrity (HVCI) kapatıldı")

        # Credential Guard
        if self.disable_credential_guard:
            # LsaCfgFlags:
            # 0 = Disabled
            # 1 = Enabled with UEFI lock
            # 2 = Enabled without lock
            if self._set_reg_dword(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Lsa",
                "LsaCfgFlags",
                0,
            ):
                changes.append("Credential Guard kapatıldı: LsaCfgFlags=0")
                print("      ✅ Credential Guard kapatıldı")

        # Boot-level hypervisor disable (aggressive)
        if self.disable_hypervisor_launch:
            if self._bcdedit_set(["/set", "hypervisorlaunchtype", "off"]):
                changes.append("Hypervisor launch kapatıldı: bcdedit hypervisorlaunchtype=off")
                print("      ✅ Hypervisor launch kapatıldı (WSL2/Hyper-V etkilenebilir)")

        self.changes.extend(changes)
        return changes


