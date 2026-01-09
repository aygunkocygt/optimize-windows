#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Startup / Scheduled Task trimming (oyun odaklı, dev-safe)

Hedef:
- CPU/RAM kullanan gereksiz Windows task'larını kapatmak (telemetry, CEIP, GameDVR task'ları gibi)
- İstenmeyen startup girdilerini kapatmak (örn. Teams)

Notlar:
- Üçüncü parti launcher'lara dokunmayız (Steam/Epic/EA/Battle.net/Discord/GFE/RGB yazılımları).
- Task disable işlemi sadece belirli güvenli hedeflerde yapılır.
"""

from __future__ import annotations

import json
import subprocess
import winreg
from typing import Any, Dict, List, Optional, Tuple


class StartupTasksOptimizer:
    def __init__(self):
        self.changes: List[str] = []

        # Kullanıcı tercihleri (optimize.py tarafından set edilir)
        self.disable_telemetry_tasks: bool = True
        self.disable_gamedvr_tasks: bool = True
        self.disable_xbox_tasks: bool = True
        self.disable_teams_startup: bool = True
        self.disable_onedrive_startup: bool = False
        self.disable_onedrive_tasks: bool = False

        # Backup
        self.backup: Dict[str, Any] = {
            "startup_entries": [],
            "scheduled_tasks": [],
        }

    # ---------- Startup (Run keys) ----------
    def _iter_run_values(self, root, subkey: str) -> List[Tuple[str, str]]:
        values: List[Tuple[str, str]] = []
        try:
            key = winreg.OpenKey(root, subkey, 0, winreg.KEY_READ)
        except FileNotFoundError:
            return values
        try:
            i = 0
            while True:
                name, value, _typ = winreg.EnumValue(key, i)
                if isinstance(value, str):
                    values.append((name, value))
                i += 1
        except OSError:
            pass
        finally:
            winreg.CloseKey(key)
        return values

    def _delete_run_value(self, root, subkey: str, name: str) -> bool:
        try:
            key = winreg.OpenKey(root, subkey, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def _should_disable_startup_entry(self, name: str, value: str) -> bool:
        hay = f"{name} {value}".lower()
        if self.disable_teams_startup and ("teams" in hay):
            return True
        if self.disable_onedrive_startup and ("onedrive" in hay):
            return True
        return False

    def trim_startup_entries(self) -> List[str]:
        changes: List[str] = []
        print("   📋 Startup (Run) girdileri kontrol ediliyor...")

        targets = [
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKCU"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKLM"),
        ]

        for root, subkey, hive_name in targets:
            for name, value in self._iter_run_values(root, subkey):
                if not self._should_disable_startup_entry(name, value):
                    continue
                # Backup
                self.backup["startup_entries"].append({
                    "hive": hive_name,
                    "path": subkey,
                    "name": name,
                    "value": value,
                })
                if self._delete_run_value(root, subkey, name):
                    msg = f"Startup devre dışı: {hive_name}\\{subkey}\\{name}"
                    changes.append(msg)
                    print(f"      ✅ {name} (startup) kapatıldı")

        return changes

    # ---------- Scheduled Tasks ----------
    def _powershell_json(self, command: str, timeout: int = 60) -> Optional[Any]:
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                return None
            out = (result.stdout or "").strip()
            if not out:
                return None
            return json.loads(out)
        except Exception:
            return None

    def _disable_scheduled_tasks(self) -> List[str]:
        changes: List[str] = []
        print("   📋 Scheduled Tasks kontrol ediliyor...")

        # Filtreler (dev-safe): telemetry/CEIP + GameDVR/Xbox task'ları
        filters: List[str] = []
        if self.disable_telemetry_tasks:
            filters.extend([
                r'($_.TaskPath -like "\Microsoft\Windows\Customer Experience Improvement Program\*")',
                r'($_.TaskPath -like "\Microsoft\Windows\Application Experience\*")',
                r'($_.TaskPath -like "\Microsoft\Windows\Autochk\*") -and ($_.TaskName -like "*Proxy*")',
                r'($_.TaskPath -like "\Microsoft\Windows\DiskDiagnostic\*")',
                r'($_.TaskPath -like "\Microsoft\Windows\Feedback\*") -or ($_.TaskPath -like "\Microsoft\Windows\FeedbackHub\*")',
            ])
        if self.disable_gamedvr_tasks:
            filters.append(r'($_.TaskPath -like "\Microsoft\Windows\GameDVR\*")')
        if self.disable_xbox_tasks:
            filters.append(r'($_.TaskPath -like "\Microsoft\XblGameSave\*")')
        if self.disable_onedrive_tasks:
            filters.append(r'($_.TaskPath -like "\Microsoft\Windows\OneDrive\*")')
        # Windows Error Reporting tasks (agresif, genelde güvenli)
        filters.append(r'($_.TaskPath -like "\Microsoft\Windows\Windows Error Reporting\*")')

        if not filters:
            return changes

        where = " -or ".join(filters)
        # 1) hedef task'ları JSON olarak al
        query_cmd = (
            f'$t = Get-ScheduledTask | Where-Object {{ {where} }} | '
            'Select-Object TaskName,TaskPath,State; '
            '$t | ConvertTo-Json -Depth 4'
        )
        tasks = self._powershell_json(query_cmd, timeout=90)
        if tasks is None:
            return changes
        if isinstance(tasks, dict):
            tasks = [tasks]
        if not isinstance(tasks, list):
            return changes

        # 2) disable et (Disabled değilse)
        for t in tasks:
            try:
                task_name = t.get("TaskName")
                task_path = t.get("TaskPath")
                state = (t.get("State") or "").strip()
                if not task_name or not task_path:
                    continue

                # Backup
                self.backup["scheduled_tasks"].append({
                    "task_name": task_name,
                    "task_path": task_path,
                    "state": state,
                })

                if state.lower() == "disabled":
                    continue

                disable_cmd = f'Disable-ScheduledTask -TaskName "{task_name}" -TaskPath "{task_path}" | Out-Null'
                subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", disable_cmd],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                changes.append(f"Task devre dışı: {task_path}{task_name}")
            except Exception:
                continue

        if changes:
            print(f"      ✅ {len(changes)} task devre dışı bırakıldı")
        return changes

    def optimize(self) -> List[str]:
        changes: List[str] = []
        changes.extend(self.trim_startup_entries())
        changes.extend(self._disable_scheduled_tasks())
        self.changes.extend(changes)
        return changes


