#include <windows.h>
#include <iostream>

// ---------- Window procedure ----------
LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam) {
    if (message == WM_INPUT) {
        UINT dwSize = 0;
        GetRawInputData((HRAWINPUT)lParam, RID_INPUT, NULL, &dwSize, sizeof(RAWINPUTHEADER));
        LPBYTE lpb = new BYTE[dwSize];
        if (lpb == NULL) return 0;

        if (GetRawInputData((HRAWINPUT)lParam, RID_INPUT, lpb, &dwSize, sizeof(RAWINPUTHEADER)) == dwSize) {
            RAWINPUT* raw = (RAWINPUT*)lpb;

            if (raw->header.dwType == RIM_TYPEKEYBOARD) {
                USHORT vkey = raw->data.keyboard.VKey;
                HANDLE device = raw->header.hDevice;
                USHORT flags = raw->data.keyboard.Flags;

                const char* state = (flags & RI_KEY_BREAK) ? "up" : "down";
                std::cout << device << " " << vkey << " " << state << std::endl;
            }
        }
        delete[] lpb;
    }

    return DefWindowProc(hWnd, message, wParam, lParam);
}

int main() {
    HINSTANCE hInstance = GetModuleHandle(NULL);

    // ---------- Register window class ----------
    WNDCLASSA wc = {0};
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = "MyRawInputWindow";

    if (!RegisterClassA(&wc)) {
        std::cerr << "Error: failed to register window class" << std::endl;
        return 1;
    }

    // ---------- Create hidden message-only window ----------
    HWND hwnd = CreateWindowExA(
        0, "MyRawInputWindow", "HiddenRawInputWindow",
        0, 0, 0, 0, 0,
        HWND_MESSAGE, // message-only window
        NULL, hInstance, NULL
    );

    if (!hwnd) {
        std::cerr << "Error: failed to create window" << std::endl;
        return 1;
    }

    // ---------- Register keyboards ----------
    RAWINPUTDEVICE rid[1];
    rid[0].usUsagePage = 0x01; // Generic desktop controls
    rid[0].usUsage = 0x06;     // Keyboard
    rid[0].dwFlags = RIDEV_INPUTSINK; // receive input even when in background
    rid[0].hwndTarget = hwnd;

    if (!RegisterRawInputDevices(rid, 1, sizeof(rid[0]))) {
        std::cerr << "Error: failed to register RAW Input (code "
                  << GetLastError() << ")" << std::endl;
        return 1;
    }

    std::cout << "Program started. Press keys..." << std::endl;

    // ---------- Message loop ----------
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg); 
    }

    return 0;
}
