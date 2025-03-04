import ctypes
from ctypes import wintypes

# Dictionnaire des Virtual Key Codes
VIRTUAL_KEY_CODES = {
    0x08: "BackSpace", 0x09: "Tab", 0x0D: "Enter", 0xA0: "LeftShift", 0xA1: "RightShift",
    0xA2: "LeftControl", 0xA3: "RightControl", 0xA4: "LeftAlt", 0xA5: "RightAlt",
    0x13: "Pause", 0x14: "CapsLock", 0x1B: "Escape", 0x20: "SpaceBar", 0x21: "PageUp",
    0x22: "PageDown", 0x23: "End", 0x24: "Home", 0x25: "Left", 0x26: "Up", 0x27: "Right",
    0x28: "Down", 0x2D: "Insert", 0x2E: "Delete", 0x30: "Zero", 0x31: "One", 0x32: "Two",
    0x33: "Three", 0x34: "Four", 0x35: "Five", 0x36: "Six", 0x37: "Seven", 0x38: "Eight",
    0x39: "Nine", 0x41: "A", 0x42: "B", 0x43: "C", 0x44: "D", 0x45: "E", 0x46: "F", 0x47: "G",
    0x48: "H", 0x49: "I", 0x4A: "J", 0x4B: "K", 0x4C: "L", 0x4D: "M", 0x4E: "N", 0x4F: "O",
    0x50: "P", 0x51: "Q", 0x52: "R", 0x53: "S", 0x54: "T", 0x55: "U", 0x56: "V", 0x57: "W",
    0x58: "X", 0x59: "Y", 0x5A: "Z", 0x60: "NumPadZero", 0x61: "NumPadOne", 0x62: "NumPadTwo",
    0x63: "NumPadThree", 0x64: "NumPadFour", 0x65: "NumPadFive", 0x66: "NumPadSix",
    0x67: "NumPadSeven", 0x68: "NumPadEight", 0x69: "NumPadNine", 0x6A: "Multiply",
    0x6B: "Add", 0x6D: "Subtract", 0x6E: "Decimal", 0x6F: "Divide", 0x70: "F1", 0x71: "F2",
    0x72: "F3", 0x73: "F4", 0x74: "F5", 0x75: "F6", 0x76: "F7", 0x77: "F8", 0x78: "F9",
    0x79: "F10", 0x7A: "F11", 0x7B: "F12", 0x90: "NumLock", 0x91: "ScrollLock",
    0xBA: "Semicolon", 0xBB: "Equals", 0xBC: "Comma", 0xBD: "Underscore", 0xBE: "Period",
    0xBF: "Slash", 0xC0: "Tilde", 0xDB: "LeftBracket", 0xDC: "Backslash",
    0xDD: "RightBracket", 0xDE: "Quote"
}

# Définition de la classe pour le hook clavier
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
    ]

# Fonction pour capturer un appui unique de touche
def get_keypress():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    key_name = None  # Variable pour stocker le nom de la touche détectée
    def low_level_keyboard_proc(nCode, wParam, lParam):
        nonlocal key_name
        if nCode == 0 and wParam == 0x0100:  # WM_KEYDOWN
            kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk_code = kb_struct.vkCode
            key_name = VIRTUAL_KEY_CODES.get(vk_code, None)  # Associe ou retourne None
            user32.PostQuitMessage(0)  # Quitte la boucle
        return user32.CallNextHookEx(None, nCode, wParam, ctypes.byref(ctypes.c_void_p(lParam)))

    # Définir et installer le hook clavier
    HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
    hook = HOOKPROC(low_level_keyboard_proc)
    hook_handle = user32.SetWindowsHookExA(13, hook, None, 0)  # WH_KEYBOARD_LL

    try:
        msg = wintypes.MSG()
        user32.GetMessageA(ctypes.byref(msg), None, 0, 0)
    finally:
        user32.UnhookWindowsHookEx(hook_handle)

    return key_name  # Retourne le nom de la touche ou None

# Test de la fonction
if __name__ == "__main__":
    print("Appuyez sur une touche pour obtenir son Virtual Key Code et son nom.")
    key = get_keypress()
    print(key)

