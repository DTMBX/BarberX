#Requires AutoHotkey v2.0
#SingleInstance Force

; ============================================================
; Approve Pad — UNIVERSAL FINAL
; Works for Copilot CLI + Copilot Chat + any yes/no/choice prompt
; - Buttons send: y/n/1/2/3/a + Enter
; - No is protected: double-click within 650ms
; - Targets last active window (terminal/editor/chat) automatically
; - Optional Lock Target + Pause
; ============================================================

; ---- Guard ----
try {
    if (VerCompare(A_AhkVersion, "2.0") < 0)
        throw Error("AutoHotkey v2 required")
} catch {
    MsgBox("Approve Pad requires AutoHotkey v2. You'll be redirected to install it.", "AutoHotkey v2 Required", "Icon!")
    Run("https://www.autohotkey.com/")
    ExitApp
}

; ---- Performance ----
SendMode("Input")
SetKeyDelay(-1, -1)
SetControlDelay(-1)
SetWinDelay(0)
SetMouseDelay(-1)

; ---- State ----
global padGui := 0
global padHwnd := 0
global lastTargetHwnd := 0
global lockedTargetHwnd := 0
global sendEnabled := true

; Safety: No must be double-clicked
global noConfirmWindowMs := 650
global lastNoClickTick := 0

; ---- Theme ----
global THEME := Map()
DetectTheme()

; ---- GUI ----
padGui := Gui("+AlwaysOnTop +Resize +MinimizeBox +MaximizeBox", "Approve Pad")
padGui.SetFont("s10", THEME["Font"])
padGui.BackColor := THEME["Bg"]

global txtTitle := padGui.AddText("xm ym", "Approve Pad — Universal approvals")
global btnHelp  := padGui.AddButton("x+m w36", "?")
global btnLock  := padGui.AddButton("x+m w120", "Lock Target")
global btnPause := padGui.AddButton("x+m w120", "Pause")

global txtStatus := padGui.AddText("xm", "")

; Primary
global btnEnter := padGui.AddButton("xm", "Enter")

global btnYes := padGui.AddButton("xm", "Yes (y)")
global btnNo  := padGui.AddButton("x+m", "No (n)")

; Common “all/always” choice
global btnAll := padGui.AddButton("xm", "Approve All (a)")
global btnAllow := padGui.AddButton("x+m", "Allow (y)")

; Choice buttons
global btn1 := padGui.AddButton("xm", "1")
global btn2 := padGui.AddButton("x+m", "2")
global btn3 := padGui.AddButton("x+m", "3")

global txtHint := padGui.AddText("xm", "")

ApplyTheme()

; ---- Events ----
btnHelp.OnEvent("Click", (*) => ShowHelp())
btnLock.OnEvent("Click", (*) => ToggleLock())
btnPause.OnEvent("Click", (*) => ToggleSendEnabled())

btnEnter.OnEvent("Click", (*) => SendToTargetSmart("{Enter}"))
btnYes.OnEvent("Click", (*) => SendToTargetSmart("y{Enter}"))
btnAllow.OnEvent("Click", (*) => SendToTargetSmart("y{Enter}"))
btnAll.OnEvent("Click", (*) => SendToTargetSmart("a{Enter}"))

btnNo.OnEvent("Click", (*) => SafeNoSend())

btn1.OnEvent("Click", (*) => SendToTargetSmart("1{Enter}"))
btn2.OnEvent("Click", (*) => SendToTargetSmart("2{Enter}"))
btn3.OnEvent("Click", (*) => SendToTargetSmart("3{Enter}"))

; Hotkeys (optional)
^!l::ToggleLock()          ; Ctrl+Alt+L
^!p::ToggleSendEnabled()   ; Ctrl+Alt+P

padGui.OnEvent("Size", PadResized)
padGui.OnEvent("Close", (*) => ExitApp())

; Start
padGui.Show("w460 h360")
padHwnd := padGui.Hwnd

SetTimer(TrackActiveWindow, 75)
SetTimer(UpdateStatus, 150)

; ===============================
; Functions
; ===============================

DetectTheme() {
    global THEME
    isLight := 1
    try {
        v := RegRead("HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme")
        isLight := (v = 1)
    } catch {
        isLight := 1
    }
    if (isLight) {
        THEME["Bg"] := "F3F3F3", THEME["Text"] := "111111", THEME["Muted"] := "444444", THEME["Font"] := "Segoe UI"
    } else {
        THEME["Bg"] := "1F1F1F", THEME["Text"] := "EAEAEA", THEME["Muted"] := "B9B9B9", THEME["Font"] := "Segoe UI"
    }
}

ApplyTheme() {
    global THEME
    global txtTitle, txtStatus, txtHint
    global btnHelp, btnLock, btnPause
    global btnEnter, btnYes, btnNo, btnAllow, btnAll, btn1, btn2, btn3

    txtTitle.SetFont("s10 c" THEME["Text"], THEME["Font"])
    txtStatus.SetFont("s9 c" THEME["Muted"], THEME["Font"])
    txtHint.SetFont("s9 c" THEME["Muted"], THEME["Font"])

    for btn in [btnHelp, btnLock, btnPause, btnEnter, btnYes, btnNo, btnAllow, btnAll, btn1, btn2, btn3]
        btn.SetFont("s10", THEME["Font"])
}

TrackActiveWindow() {
    global padHwnd, lastTargetHwnd, lockedTargetHwnd
    hwnd := WinExist("A")
    if (!hwnd || hwnd = padHwnd)
        return
    if (lockedTargetHwnd)
        return
    lastTargetHwnd := hwnd
}

GetTargetHwnd() {
    global lastTargetHwnd, lockedTargetHwnd
    return lockedTargetHwnd ? lockedTargetHwnd : lastTargetHwnd
}

SendToTargetSmart(keys) {
    global sendEnabled
    if (!sendEnabled) {
        SoundBeep(650, 60)
        return
    }

    hwnd := GetTargetHwnd()
    if (!hwnd || !WinExist("ahk_id " hwnd)) {
        SoundBeep(1200, 80)
        return
    }

    exe := ""
    try exe := WinGetProcessName("ahk_id " hwnd)

    ; VS Code prefers activation + Send (chat input reliability)
    if (exe = "Code.exe") {
        WinActivate("ahk_id " hwnd)
        Sleep(25)
        Send(keys)
        return
    }

    ; Others: ControlSend best-effort, fallback to Send
    try {
        ControlSend(keys, , "ahk_id " hwnd)
        WinActivate("ahk_id " hwnd)
    } catch {
        WinActivate("ahk_id " hwnd)
        Send(keys)
    }
}

SafeNoSend() {
    global lastNoClickTick, noConfirmWindowMs
    now := A_TickCount
    if (now - lastNoClickTick <= noConfirmWindowMs) {
        lastNoClickTick := 0
        SendToTargetSmart("n{Enter}")
    } else {
        lastNoClickTick := now
        SoundBeep(850, 40)
    }
}

ToggleLock() {
    global lockedTargetHwnd, lastTargetHwnd, btnLock
    if (lockedTargetHwnd) {
        lockedTargetHwnd := 0
        btnLock.Text := "Lock Target"
        SoundBeep(900, 60)
        return
    }
    if (!lastTargetHwnd || !WinExist("ahk_id " lastTargetHwnd)) {
        SoundBeep(1200, 80)
        return
    }
    lockedTargetHwnd := lastTargetHwnd
    btnLock.Text := "Unlock Target"
    SoundBeep(1000, 60)
}

ToggleSendEnabled() {
    global sendEnabled, btnPause
    sendEnabled := !sendEnabled
    btnPause.Text := sendEnabled ? "Pause" : "Enable"
    SoundBeep(sendEnabled ? 1000 : 550, 60)
}

UpdateStatus() {
    global txtStatus, sendEnabled, lockedTargetHwnd
    global lastNoClickTick, noConfirmWindowMs

    hwnd := GetTargetHwnd()
    lockTag := lockedTargetHwnd ? "LOCKED" : "TRACKING"
    state := sendEnabled ? "ENABLED" : "PAUSED"

    if (!hwnd || !WinExist("ahk_id " hwnd)) {
        txtStatus.Value := "Target: (none) | " lockTag " | " state
        return
    }

    title := WinGetTitle("ahk_id " hwnd)
    if (title = "")
        title := "(untitled)"
    if (StrLen(title) > 52)
        title := SubStr(title, 1, 49) "…"

    armed := (lastNoClickTick && (A_TickCount - lastNoClickTick <= noConfirmWindowMs)) ? " | NO ARMED" : ""
    txtStatus.Value := "Target: " title " | " lockTag " | " state armed
}

ShowHelp() {
    MsgBox(
        "Universal Approve Pad`n`n" .
        "This pad answers prompts fast in terminals and chats:`n" .
        "• Yes / Allow = y + Enter`n" .
        "• No = n + Enter (double-click to prevent mistakes)`n" .
        "• 1 / 2 / 3 = choice + Enter`n" .
        "• Approve All = a + Enter`n`n" .
        "Targeting:`n" .
        "• Sends to your last active window automatically.`n" .
        "• Lock Target freezes the destination (Ctrl+Alt+L).`n" .
        "• Pause disables sending (Ctrl+Alt+P).",
        "Help",
        "Iconi"
    )
}

PadResized(guiObj, minMax, width, height) {
    global txtTitle, btnHelp, btnLock, btnPause, txtStatus
    global btnEnter, btnYes, btnNo, btnAllow, btnAll, btn1, btn2, btn3
    global txtHint

    if (minMax = -1)
        return

    margin := Max(8, Min(12, Floor(width * 0.04)))
    gap := Max(8, Min(10, Floor(width * 0.03)))
    compactW := (width < 420)
    compactH := (height < 320)
    compact := compactW || compactH

    rowW := Max(10, width - (2 * margin))
    y := margin

    titleH := compact ? 18 : 22
    smallH := titleH + 6

    helpW := 36
    lockW := compact ? 104 : 120
    pauseW := compact ? 104 : 120
    rightW := helpW + lockW + pauseW + gap*2

    if (rowW < rightW + 140) {
        txtTitle.Move(margin, y, rowW, titleH)
        y += titleH + gap
        btnHelp.Move(margin, y, helpW, smallH)
        btnLock.Move(margin + helpW + gap, y, lockW, smallH)
        btnPause.Move(margin + helpW + gap + lockW + gap, y, pauseW, smallH)
        y += smallH + gap
    } else {
        txtTitle.Move(margin, y, rowW - rightW - gap, titleH)
        btnHelp.Move(margin + rowW - rightW, y - 2, helpW, smallH)
        btnLock.Move(margin + rowW - (lockW + pauseW + gap), y - 2, lockW, smallH)
        btnPause.Move(margin + rowW - pauseW, y - 2, pauseW, smallH)
        y += smallH + gap
    }

    statusH := compact ? 18 : 20
    txtStatus.Move(margin, y, rowW, statusH)
    y += statusH + gap

    bottomStripH := compact ? 44 : 48
    txtHint.Value := compact
        ? "Tip: Click in the prompt you want to answer • No is double-click"
        : "Tip: Click in the prompt you want to answer • No is double-click • Ctrl+Alt+L Lock • Ctrl+Alt+P Pause"

    bottomY := height - margin - bottomStripH

    remaining := bottomY - y - margin
    if (remaining < 140)
        remaining := 140

    enterH := compact ? 52 : 64
    ynH := compact ? 40 : 46
    helperH := compact ? 34 : 38
    numH := compact ? 30 : 34

    desired := enterH + ynH + helperH + numH + gap*3
    if (remaining < desired && desired > 0) {
        scale := remaining / desired
        enterH := Max(42, Floor(enterH * scale))
        ynH := Max(32, Floor(ynH * scale))
        helperH := Max(28, Floor(helperH * scale))
        numH := Max(26, Floor(numH * scale))
    }

    btnEnter.Move(margin, y, rowW, enterH)
    y += enterH + gap

    if (compactW && width < 320) {
        btnYes.Move(margin, y, rowW, ynH), y += ynH + gap
        btnNo.Move(margin, y, rowW, ynH), y += ynH + gap
    } else {
        btnW2 := Max(120, Floor((rowW - gap) / 2))
        btnYes.Move(margin, y, btnW2, ynH)
        btnNo.Move(margin + btnW2 + gap, y, rowW - (btnW2 + gap), ynH)
        y += ynH + gap
    }

    if (compactW && width < 320) {
        btnAll.Move(margin, y, rowW, helperH), y += helperH + gap
        btnAllow.Move(margin, y, rowW, helperH), y += helperH + gap
    } else {
        btnW2 := Max(140, Floor((rowW - gap) / 2))
        btnAll.Move(margin, y, btnW2, helperH)
        btnAllow.Move(margin + btnW2 + gap, y, rowW - (btnW2 + gap), helperH)
        y += helperH + gap
    }

    if (compactW && width < 320) {
        btn1.Move(margin, y, rowW, numH), y += numH + gap
        btn2.Move(margin, y, rowW, numH), y += numH + gap
        btn3.Move(margin, y, rowW, numH), y += numH + gap
    } else {
        btnW3 := Max(70, Floor((rowW - (2 * gap)) / 3))
        btn1.Move(margin, y, btnW3, numH)
        btn2.Move(margin + btnW3 + gap, y, btnW3, numH)
        btn3.Move(margin + (btnW3 + gap) * 2, y, rowW - (btnW3*2 + gap*2), numH)
        y += numH + gap
    }

    txtHint.Move(margin, bottomY, rowW, bottomStripH)
}
