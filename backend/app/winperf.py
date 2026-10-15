"""Windows 11 的 EcoQoS（效率模式）會把「背景」行程節流：啟動 start.ps1 後切到瀏覽器，
主控台視窗變成背景，約 2～3 秒後 CPU 運算掉到 1/6～1/8，MediaPipe 每幀從 ~25 ms 變成 ~170 ms。
即時辨識是使用者正在看的前景工作，明確告訴系統這個行程不要節流。
"""
from __future__ import annotations

import sys


def disable_power_throttling() -> bool:
    if sys.platform != "win32":
        return False
    import ctypes
    from ctypes import wintypes

    class ProcessPowerThrottlingState(ctypes.Structure):
        _fields_ = [("Version", wintypes.ULONG), ("ControlMask", wintypes.ULONG), ("StateMask", wintypes.ULONG)]

    PROCESS_POWER_THROTTLING_CURRENT_VERSION = 1
    PROCESS_POWER_THROTTLING_EXECUTION_SPEED = 0x1
    ProcessPowerThrottling = 4  # PROCESS_INFORMATION_CLASS

    # ControlMask 指定要控制 EXECUTION_SPEED，StateMask = 0 代表關閉節流
    state = ProcessPowerThrottlingState(PROCESS_POWER_THROTTLING_CURRENT_VERSION, PROCESS_POWER_THROTTLING_EXECUTION_SPEED, 0)
    kernel32 = ctypes.windll.kernel32
    kernel32.SetProcessInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel32.SetProcessInformation.restype = wintypes.BOOL
    return bool(kernel32.SetProcessInformation(kernel32.GetCurrentProcess(), ProcessPowerThrottling,
                                               ctypes.byref(state), ctypes.sizeof(state)))
