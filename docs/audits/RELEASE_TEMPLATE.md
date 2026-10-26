# Release record — Ink & Iron `{VERSION}` ({DATE})

> Pre-Deploy S15 (`docs/PRE_DEPLOY_PLAN.md` §2 S15). One record per build the testers get: the stamp, the
> zip's hash, the signing, the smoke's transcript, the clean-machine checklist, and what the build waits on.

## The stamp

| Field | Value |
|---|---|
| Version | `{VERSION}` |
| Commit | `{COMMIT}` (master) |
| Built | {BUILT_AT} on the development machine (`deploy\build.bat`) |
| Signed | **{SIGNED}** |
| Zip | `deploy/dist/ink_iron_{VERSION}.zip` |
| SHA-256 | `{ZIP_SHA256}` |
| Size | {ZIP_SIZE} |

## The signing — what the build found on this machine

The build runs the signing seam only when `INK_IRON_SIGNTOOL_ARGS` is set (`deploy/build.bat` `:sign_exe`;
`SYSTEMS_REFERENCE.md` §152.11). On {DATE} the environment held neither variable, the Windows SDK's
`signtool.exe` was not installed (no `C:\Program Files (x86)\Windows Kits`, nothing on PATH), no code-signing
certificate stood in `Cert:\CurrentUser\My` or `Cert:\LocalMachine\My` (the one certificate there is the
"Microsoft Your Phone" self-issued key), no hardware-token middleware (SafeNet / Certum / eSigner) and no Azure
Trusted Signing client (`Azure.CodeSigning.Dlib.dll`) were present, and no `.pfx` sat in Downloads, Desktop,
Documents or the repository. **This build is UNSIGNED**; the tester README's SmartScreen note stands.

The day the certificate arrives, nothing in the code moves — two variables and one command:

1. Install the Windows SDK's signing tool (the smallest road is the SDK's "Windows SDK Signing Tools for
   Desktop Apps" feature; `winget install Microsoft.WindowsSDK.10.0.26100` carries it), or set `SIGNTOOL`
   to the `signtool.exe` of any SDK already on the machine.
2. Set `INK_IRON_SIGNTOOL_ARGS` for the session (never in a file):
   - an OV / EV certificate in the user's store:
     `/fd SHA256 /td SHA256 /tr http://timestamp.digicert.com /sha1 <THUMBPRINT>`
   - Azure Trusted Signing:
     `/fd SHA256 /td SHA256 /tr http://timestamp.acs.microsoft.com /dlib "<path>\Azure.CodeSigning.Dlib.dll" /dmdf "<path>\metadata.json"`
     (the `metadata.json` names the endpoint, the account and the certificate profile; `az login` first).
3. `deploy\build.bat` — the banner then reads `BUILD COMPLETE - <version> (signed)`, both executables verified,
   the smoke run with `--expect-signed`.

## The smoke (the frozen server, `tools/release_smoke.py`)

```
{SMOKE_TRANSCRIPT}
```

## The export and the pack

```
{EXPORT_TRANSCRIPT}
```

## The clean-machine run

{CLEAN_RUN}

## The walk (UXR-4, delegated to the session — `docs/UX_UI_REVIEW_PLAN.md` §UXR-4)

{WALK}

## What this build waits on

{WAITS_ON}
