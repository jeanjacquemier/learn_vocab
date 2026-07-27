Android app for Learn Vocabulary

This is a minimal Android app skeleton (Kotlin) that implements the same French->English quiz as the CLI/web apps.

How to open

- Open the `android_app` directory in Android Studio (File -> Open) and let Gradle sync.
- Copy your full `data/fra.txt` into `app/src/main/assets/fra.txt` to use the full dataset, or keep the provided `fra.txt` sample for quick testing.
- Run the app on an emulator or device.

What it does

- Loads `fra.txt` from `assets/` (tab-separated: English<TAB>French).
- Keeps per-phrase integer scores in SharedPreferences (reset to 0 on incorrect, +1 on correct).
- Keeps a small persistent "pool" of phrases in preferences and shows a random phrase from the pool.
- When a phrase reaches score >= 5 it is removed from the pool and a replacement is added.

Notes

- This is an app skeleton to get started. You can enhance it with better UI, per-user sessions, syncing, or reading the original `data/` file programmatically.
