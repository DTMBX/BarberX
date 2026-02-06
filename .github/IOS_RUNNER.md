Required macOS runner setup for iOS builds

This repository's iOS/MAUI builds target .NET for iOS that requires a recent Xcode installation.

Required Xcode version: 26.2

If you need to run the iOS build workflow (`.github/workflows/ios-build.yml`) on GitHub Actions, ensure one of the following:

- Use a self-hosted macOS runner that has Xcode 26.2 installed and selected.
- Use a hosted runner with Xcode 26.2 (if/when GitHub provides that image).
- Alternatively, change your project/workload to target an older .NET for iOS workload compatible with the runner's Xcode (not recommended unless you understand the SDK implications).

Notes:
- The workflow contains a pre-check that queries `xcodebuild -version`. If the installed Xcode does not match 26.2, the workflow will skip the iOS build and emit a warning.
- To force a run on a known-good machine, use `workflow_dispatch` and select a self-hosted runner tagged to match the required environment.

Guidance for maintainers:
- Prefer upgrading runner images to match SDKs to keep parity with latest toolchains.
- If you must downgrade the SDK, update `global.json` and project SDK references accordingly and test on local macOS before applying in CI.
