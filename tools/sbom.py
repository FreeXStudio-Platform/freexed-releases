#!/usr/bin/env python3
"""Make a CycloneDX 1.5 SBOM for a macOS app archive (ZIP) without its source.

It lists every file in the archive with its SHA-256, the app and helper bundles
(from Info.plist), the system libraries and frameworks each executable links
(from Mach-O load commands), and bundled fonts. Output is deterministic, so the
release workflow can regenerate it and compare it with the published copy.

Usage: sbom.py ARCHIVE.zip --version VERSION --timestamp YYYY-MM-DDTHH:MM:SSZ
"""
import argparse, hashlib, io, json, plistlib, struct, sys, uuid, zipfile

FAT_MAGIC, FAT_MAGIC_64 = 0xCAFEBABE, 0xCAFEBABF
MH_MAGIC_64, MH_MAGIC = 0xFEEDFACF, 0xFEEDFACE
LOAD_DYLIB_CMDS = {0xC, 0x80000018, 0x8000001F, 0x80000023}  # LOAD, LOAD_WEAK, REEXPORT, LOAD_UPWARD
CPU = {0x01000007: "x86_64", 0x0100000C: "arm64"}


def macho_slices(data):
    magic = struct.unpack(">I", data[:4])[0]
    if magic in (FAT_MAGIC, FAT_MAGIC_64):
        n = struct.unpack(">I", data[4:8])[0]
        out, off = [], 8
        for _ in range(n):
            if magic == FAT_MAGIC:
                cputype, _, offset, size, _ = struct.unpack(">iiIII", data[off:off + 20]); off += 20
            else:
                cputype, _, offset, size, _, _ = struct.unpack(">iiQQII", data[off:off + 32]); off += 32
            out.append((CPU.get(cputype & 0xFFFFFFFF, hex(cputype & 0xFFFFFFFF)), data[offset:offset + size]))
        return out
    le = struct.unpack("<I", data[:4])[0]
    if le in (MH_MAGIC_64, MH_MAGIC):
        cputype = struct.unpack("<i", data[4:8])[0]
        return [(CPU.get(cputype & 0xFFFFFFFF, hex(cputype & 0xFFFFFFFF)), data)]
    return []


def linked_libraries(slice_data):
    magic = struct.unpack("<I", slice_data[:4])[0]
    header = 32 if magic == MH_MAGIC_64 else 28
    ncmds = struct.unpack("<I", slice_data[16:20])[0]
    off, libs = header, []
    for _ in range(ncmds):
        cmd, size = struct.unpack("<II", slice_data[off:off + 8])
        if cmd in LOAD_DYLIB_CMDS:
            name_off = struct.unpack("<I", slice_data[off + 8:off + 12])[0]
            raw = slice_data[off + name_off:off + size]
            libs.append(raw.split(b"\0", 1)[0].decode())
        off += size
    return libs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archive")
    ap.add_argument("--version", required=True)
    ap.add_argument("--timestamp", required=True)
    a = ap.parse_args()

    raw = open(a.archive, "rb").read()
    zf = zipfile.ZipFile(io.BytesIO(raw))
    names = sorted(n for n in zf.namelist() if not n.endswith("/") and "__MACOSX" not in n)
    files, bundles, libraries, fonts = [], [], {}, []
    for n in names:
        info = zf.getinfo(n)
        if (info.external_attr >> 16) & 0o170000 == 0o120000:  # symlink inside the bundle
            continue
        data = zf.read(n)
        files.append({"type": "file", "name": n, "hashes": [{"alg": "SHA-256", "content": hashlib.sha256(data).hexdigest()}]})
        if n.endswith("Contents/Info.plist"):
            p = plistlib.loads(data)
            bundles.append({"type": "application", "name": p.get("CFBundleName") or p.get("CFBundleExecutable"),
                            "version": p.get("CFBundleShortVersionString", ""),
                            "properties": [{"name": "bundle-id", "value": p.get("CFBundleIdentifier", "")},
                                           {"name": "bundle-version", "value": str(p.get("CFBundleVersion", ""))},
                                           {"name": "minimum-macos", "value": p.get("LSMinimumSystemVersion", "")},
                                           {"name": "path", "value": n[: -len("Contents/Info.plist")]}]})
        for arch, sl in macho_slices(data) if len(data) > 8 else []:
            for lib in linked_libraries(sl):
                libraries.setdefault(lib, set()).add(arch)
        if n.lower().endswith((".ttf", ".otf")):
            fonts.append(n)

    components = sorted(bundles, key=lambda c: c["name"] or "")
    for lib in sorted(libraries):
        components.append({"type": "library" if lib.endswith(".dylib") else "framework", "name": lib,
                           "properties": [{"name": "architectures", "value": ",".join(sorted(libraries[lib]))},
                                          {"name": "provided-by", "value": "macOS" if lib.startswith(("/System/", "/usr/lib/")) else "bundled"}]})
    for f in fonts:
        components.append({"type": "file", "name": f, "licenses": [{"license": {"id": "OFL-1.1"}}]})
    components += files

    archive_sha = hashlib.sha256(raw).hexdigest()
    sbom = {
        "bomFormat": "CycloneDX", "specVersion": "1.5",
        "serialNumber": "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "sha256:" + archive_sha)),
        "version": 1,
        "metadata": {"timestamp": a.timestamp,
                     "tools": {"components": [{"type": "application", "name": "tools/sbom.py"}]},
                     "component": {"type": "file", "name": a.archive.rsplit("/", 1)[-1], "version": a.version,
                                   "hashes": [{"alg": "SHA-256", "content": archive_sha}]}},
        "components": components,
    }
    json.dump(sbom, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
