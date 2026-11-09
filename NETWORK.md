# Network activity and permissions: FreeXed

FreeXed makes **no network connections**. It has no account, no analytics, no crash reporting
and no update check, and it contains no networking code.

Links in the app open in your browser or mail app only when you click them:
`https://freexstudio.com`, `mailto:admin@freexstudio.com`, Apple support pages, and a support
link on the welcome screen when a build includes one. FreeXed itself sends nothing.

## What it touches on your Mac

| What | When |
|---|---|
| Removes the `com.apple.quarantine` attribute from items you select | Only after you confirm each batch in the app, or run FRX It on files you selected in Finder |
| Reads code-signing, Gatekeeper and archive status of the selected items with a fixed set of read-only macOS tools (`codesign`, `spctl`, `xattr`, `lipo`, `otool`, `pkgutil`, `hdiutil verify`, `unzip -t`, `shasum`) | When you ask why an item may not open |
| Installs the FRX It Finder Quick Action | Only after you agree to it |

It never asks for an administrator password, changes Gatekeeper, SIP, TCC or XProtect, replaces
signatures, runs installers or opens the items it processes.

## Confirm it yourself

With an outbound firewall such as LuLu or Little Snitch running, use FreeXed and the FRX It
Quick Action normally. You should see **no** connection from FreeXed or FreeXedWorker. If you
do, report it privately as described in [SECURITY.md](SECURITY.md).
