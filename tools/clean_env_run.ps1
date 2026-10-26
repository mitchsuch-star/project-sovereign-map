# PREPARED October 26, 2026 (Pre-Deploy S15) — UNTESTED until the release build runs: the build and the
# clean-machine run are held behind the third DD-B measure's rows (SYSTEMS_REFERENCE.md §153.4). Owner: the
# deploy session after S14h, which runs this on the built zip and writes docs/audits/RELEASE_<version>.md
# from docs/audits/RELEASE_TEMPLATE.md. This is a clean-ENVIRONMENT run on one machine (no VM on Home),
# never to be recorded as a clean machine.

# S15 — the clean-machine run, as near as this one machine allows (no second
# machine, no VM on Home): the zip is unpacked OUTSIDE the repo, run with a PATH
# that holds no Python and no Godot, no .env, an APPDATA of its own (so the
# tester's %APPDATA%\InkAndIron road is exercised without touching the user's
# saves), and launch.bat is the one door. The exe is a GUI window; it is read
# by PrintWindow (no focus taken) and driven by messages posted to its own
# window handle (no global input: the user is at the machine).
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File clean_run.ps1 -Zip <zip> -Work <dir> -Phase unpack|launch|shot|type|click|key|stop
param(
    [string]$Zip = "",
    [string]$Work = "",
    [string]$Phase = "unpack",
    [string]$Text = "",
    [int]$X = 0,
    [int]$Y = 0,
    [string]$Key = "",
    [string]$Out = ""
)
$ErrorActionPreference = "Stop"

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class W32 {
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdc, uint flags);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT r);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hwnd, out RECT r);
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hwnd, uint msg, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr hwnd, uint msg, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern short VkKeyScanW(char c);
    [DllImport("user32.dll")] public static extern uint MapVirtualKeyW(uint code, uint mapType);
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
    public static IntPtr found = IntPtr.Zero;
    public static uint wantPid = 0;
    public static bool Cb(IntPtr h, IntPtr l) {
        uint pid; GetWindowThreadProcessId(h, out pid);
        if (pid == wantPid && IsWindowVisible(h)) { found = h; return false; }
        return true;
    }
    public static IntPtr FindByPid(uint pid) { found = IntPtr.Zero; wantPid = pid; EnumWindows(Cb, IntPtr.Zero); return found; }
}
"@ -ReferencedAssemblies System.Drawing

function Get-GameWindow {
    $p = Get-Process -Name "InkAndIron" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $p) { throw "no InkAndIron.exe process" }
    $h = [W32]::FindByPid([uint32]$p.Id)
    if ($h -eq [IntPtr]::Zero) { throw "InkAndIron.exe has no visible window yet" }
    return $h
}

function Shot($h, $path) {
    $r = New-Object W32+RECT
    [void][W32]::GetWindowRect($h, [ref]$r)
    $w = $r.R - $r.L; $hh = $r.B - $r.T
    Add-Type -AssemblyName System.Drawing
    $bmp = New-Object System.Drawing.Bitmap $w, $hh
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $hdc = $g.GetHdc()
    $ok = [W32]::PrintWindow($h, $hdc, 2)   # PW_RENDERFULLCONTENT
    $g.ReleaseHdc($hdc)
    $g.Dispose()
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    "shot: $path ($w x $hh) ok=$ok"
}

switch ($Phase) {
    "unpack" {
        if (Test-Path $Work) { Remove-Item -Recurse -Force $Work }
        New-Item -ItemType Directory -Force $Work | Out-Null
        Expand-Archive -Path $Zip -DestinationPath $Work -Force
        Get-ChildItem $Work -Recurse -Depth 1 | Select-Object FullName, Length | Format-Table -AutoSize
    }
    "launch" {
        # The tester's road: launch.bat, from the unpacked folder, with a PATH of
        # the system alone (no Python, no Godot), no .env, an APPDATA of its own.
        $bundle = Get-ChildItem $Work -Directory | Select-Object -First 1
        $appdata = Join-Path $Work "appdata"
        New-Item -ItemType Directory -Force $appdata | Out-Null
        $env:APPDATA = $appdata
        $env:LOCALAPPDATA = Join-Path $Work "localappdata"
        New-Item -ItemType Directory -Force $env:LOCALAPPDATA | Out-Null
        $env:PATH = "C:\Windows\System32;C:\Windows;C:\Windows\System32\WindowsPowerShell\v1.0"
        Remove-Item Env:\PYTHONPATH -ErrorAction SilentlyContinue
        Remove-Item Env:\ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
        Remove-Item Env:\LLM_MODE -ErrorAction SilentlyContinue
        Remove-Item Env:\SOVEREIGN_PORT -ErrorAction SilentlyContinue
        $log = Join-Path $Work "launcher.log"
        $p = Start-Process -FilePath "cmd.exe" -ArgumentList @("/c", "launch.bat > `"$log`" 2>&1 < NUL") -WorkingDirectory $bundle.FullName -WindowStyle Minimized -PassThru
        "launcher pid: $($p.Id); bundle: $($bundle.FullName); log: $log"
    }
    "park" {
        # Move the game window off the desktop the moment it exists, so the
        # user's own screen is not covered (SWP_NOACTIVATE | SWP_NOZORDER).
        $h = Get-GameWindow
        [void][W32]::SetWindowPos($h, [IntPtr]::Zero, $X, $Y, 0, 0, 0x0001 -bor 0x0010 -bor 0x0004)
        $r = New-Object W32+RECT; [void][W32]::GetWindowRect($h, [ref]$r)
        "window $h at $($r.L),$($r.T) size $($r.R - $r.L)x$($r.B - $r.T)"
    }
    "shot" { $h = Get-GameWindow; Shot $h $Out }
    "type" {
        # WM_CHAR per character, posted to the window: no focus, no global input.
        $h = Get-GameWindow
        foreach ($ch in $Text.ToCharArray()) {
            [void][W32]::PostMessage($h, 0x0102, [IntPtr][int][char]$ch, [IntPtr]1)
            Start-Sleep -Milliseconds 15
        }
        "typed $($Text.Length) chars"
    }
    "key" {
        # A named key: WM_KEYDOWN / WM_KEYUP with the scan code in lParam.
        $vk = switch ($Key) { "Enter" { 0x0D } "Escape" { 0x1B } "F1" { 0x70 } "Tab" { 0x09 } default { [int][W32]::VkKeyScanW([char]$Key) -band 0xFF } }
        $sc = [W32]::MapVirtualKeyW([uint32]$vk, 0)
        $h = Get-GameWindow
        $down = [IntPtr]([int64](1 + ($sc -shl 16)))
        $up = [IntPtr]([int64](1 + ($sc -shl 16) + 0xC0000000))
        [void][W32]::PostMessage($h, 0x0100, [IntPtr]$vk, $down)
        if ($Key -eq "Enter") { [void][W32]::PostMessage($h, 0x0102, [IntPtr]0x0D, $down) }
        Start-Sleep -Milliseconds 40
        [void][W32]::PostMessage($h, 0x0101, [IntPtr]$vk, $up)
        "key $Key (vk=$vk sc=$sc)"
    }
    "click" {
        # A left click at client coordinates: WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP.
        $h = Get-GameWindow
        $l = [IntPtr]([int64]($X + ($Y -shl 16)))
        [void][W32]::PostMessage($h, 0x0200, [IntPtr]0, $l)
        Start-Sleep -Milliseconds 60
        [void][W32]::PostMessage($h, 0x0201, [IntPtr]1, $l)
        Start-Sleep -Milliseconds 60
        [void][W32]::PostMessage($h, 0x0202, [IntPtr]0, $l)
        "click at $X,$Y"
    }
    "stop" {
        Get-Process -Name "InkAndIron" -ErrorAction SilentlyContinue | Stop-Process -Force
        Start-Sleep -Seconds 3
        Get-Process -Name "ink_iron_server" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        "stopped"
    }
}
