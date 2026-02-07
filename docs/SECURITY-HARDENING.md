**Security & Dependency Hardening**

- **Automated dependency updates**: We added Dependabot at `.github/dependabot.yml` to open PRs for npm package updates daily.
- **CI dependency scanning**: A workflow `.github/workflows/dependency-scan.yml` runs `npm ci` and `npm audit --audit-level=moderate` on pushes and PRs.

Recommended next steps to harden supply chain and acquire high-assurance processing:

1. Use GitHub Advanced Security or a 3rd-party SCA (Snyk, Sonatype) for continuous monitoring and PR blocking when severe vulnerabilities are detected.
2. Enable lockfile signing with Sigstore (cosign) for releases, and publish signed `package-lock.json` artifacts.
3. Add Dependabot configuration for versioning rules and security-only updates if desired.
4. For high-assurance compute, prefer cloud providers' government/compliant regions (AWS GovCloud, Azure Government, Google Assured Workloads) and use FedRAMP/CMMC-compliant services.
5. For HPC-style workloads: consider managed services (AWS Batch, Azure Batch, GCP Dataproc) or on-prem HPC with Slurm; use containerized images pinned to digest and scan images with Trivy.
6. Use only public/open datasets (data.gov, NOAA, USGS, Census, SEC EDGAR) unless you have explicit governance for restricted datasets.

Legal & ethical note: do not attempt to procure classified or restricted access channels. Follow lawful procurement and approvals for any government-level access.
