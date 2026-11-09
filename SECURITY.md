# Security policy

## Report a vulnerability privately

Use **Security → Report a vulnerability** on this repository. That opens a private advisory
that only the maintainers can read. Please include:

- the app version and your macOS version,
- what you did, what happened, and what you expected,
- whether it needs local access or user approval.

Do not open a public issue or Discussion for a security problem.

If you cannot use GitHub, write to admin@freexstudio.com with "Security" in the subject.

## What happens next

We reply in the advisory, keep you updated while we work on a fix, and, if you agree, credit you
in the release notes. Please give us reasonable time to ship a fix before you publish details.

## Supported versions

Only the latest release receives security fixes.

## Scope

In scope: the app and its FreeXedWorker helper published in this repository's releases, the
FRX It Finder Quick Action it installs, and how it removes the quarantine flag from files you
choose (see [NETWORK.md](NETWORK.md) for what it touches).

Out of scope: problems that need an attacker who already controls your macOS user account,
and the absence of a Developer ID signature or notarisation, which is a known limitation of
the current beta.
