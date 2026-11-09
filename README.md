# FreeXed releases

Download builds of **FreeXed** for macOS, and check them before you open them.

Drop it. FRX it. FreeXed removes the macOS quarantine flag from trusted downloads you select
and confirm, and explains why an item may not open. It does not disable Gatekeeper, repair
damaged or incompatible software, or certify a download as safe; verify the source first.

This repository holds **builds and documentation only**. The source code is private. Each
release carries the app archive, its SHA-256 checksum, a software bill of materials (SBOM)
and the build record from the private build. A workflow in this repository checks every file,
blocks personal build details, and signs an attestation for it.

- Product page: https://freexstudio.com/downloads#freexstudio-freexed
- Releases: see **Releases** on the right
- Report a bug or ask for a feature: **Issues**
- Ideas and questions: **Discussions**
- Report a security problem privately: see [SECURITY.md](SECURITY.md)

## Current release

| | |
|---|---|
| Version | 2.0.0-beta.8 (beta) |
| Platform | macOS 13 or later, Intel and Apple silicon (universal) |
| Signature | Ad-hoc. No Apple Developer ID, not notarised |
| Built | GitHub-hosted macOS runner, by the private repository's release workflow, after 42 SwiftPM and 45 Xcode tests |

The file name says `unnotarized` on purpose. Because it is not notarised, macOS shows a
warning the first time you open it. Read [How to verify a build](#how-to-verify-a-build)
before you approve it.

## How to verify a build

Download the files from the release into one folder, then run these commands in Terminal from
that folder. Replace `VERSION` with the release version, for example `2.0.0-beta.8`.

**1. The checksum matches.** Every line must end in `OK`.

```sh
shasum -a 256 -c SHA256SUMS
```

**2. This repository published the file.** Needs the GitHub CLI (`brew install gh`).

```sh
gh attestation verify FreeXed-VERSION-unnotarized-macOS.zip --repo FreeXStudio-Platform/freexed-releases
```

The attestation is signed through Sigstore and recorded in its public transparency log. It
proves the file is byte-for-byte the one this repository's release workflow checked and
published. It does **not** prove which source code produced it: the build record
(`.provenance.json`) states the source commit and toolchain from the private build.

**3. The contents match the SBOM.** The SBOM lists every file in the archive with its SHA-256,
and every system library the app links. Regenerate it with the script in this repository and
compare:

```sh
S=FreeXed-VERSION-unnotarized-macOS.sbom.cdx.json
python3 tools/sbom.py FreeXed-VERSION-unnotarized-macOS.zip --version VERSION \
  --timestamp "$(python3 -c "import json;print(json.load(open('$S'))['metadata']['timestamp'])")" \
  | diff - "$S" && echo "SBOM matches"
```

**4. The signature is what we say it is.**

```sh
unzip -q FreeXed-VERSION-unnotarized-macOS.zip
codesign -dv --verbose=2 FreeXed.app 2>&1 | grep -E 'Signature|Identifier|Format'
```

You should see `Signature=adhoc` until a notarised release ships. If you see anything else, do
not open it and report it.

**5. Its behaviour matches the list.** [NETWORK.md](NETWORK.md) lists what FreeXed touches; it
makes no network connections, which you can confirm with LuLu (free, open source) or Little
Snitch.

## What this does and does not prove

Without the source, you can confirm that a download is intact, that it is the file this
repository published, what it contains, which system libraries it uses, and that it does not
use the network. You cannot prove from a binary alone that it has no hidden behaviour. If you
need that level of assurance, wait for an independent security review or for a notarised
release, and tell us in Discussions; it helps us decide what to do next.

## Help make it better

- **Bugs:** open an issue with the bug form. Include your macOS version and Mac model.
- **Features:** open an issue with the feature form, or start a Discussion.
- **Security:** never in a public issue. Use the private report described in [SECURITY.md](SECURITY.md).

Pull requests are not accepted here, because this repository has no source code. Issues and
Discussions reach the people who build the app.

## Terms

Use of the app is covered by the notices at https://freexstudio.com/legal.
