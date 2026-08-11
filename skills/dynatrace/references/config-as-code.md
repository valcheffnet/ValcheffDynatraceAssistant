# Configuration as code — Monaco and Terraform

Two supported tools over the same APIs. Monaco is Dynatrace's own and covers
more of the platform; Terraform fits an estate already managed that way.

Corpus: `deliver/configuration-as-code` (39 files).

## Contents

- Choosing between them
- Monaco
- Monaco authentication
- Order of configurations
- Monaco v1 to v2
- Terraform
- What each can actually manage
- Things worth putting in code

## Choosing between them

`deliver/configuration-as-code/configuration-as-code-concepts` frames the
choice. In practice:

- **Monaco** — Dynatrace's own tool, closest to the platform, handles settings
  objects and the newer platform APIs, and understands configuration ordering.
- **Terraform** — the provider, worth it when Dynatrace is one resource among
  many in an existing Terraform estate.

Both hit the same API surfaces, so both inherit the same permission model. See
`api-map.md`.

## Monaco

`deliver/configuration-as-code/monaco`: `monaco-concepts`, `installation`,
`get-started`, `configuration`, `reference`, `guides`,
`monaco-api-support-and-access-handling`.

The API support page is the one to check first on "can Monaco manage X" — the
answer is per API, not global.

## Monaco authentication

Two paths, both documented as guides:

- `guides/create-platform-token` — platform token
- `guides/create-oauth-client` — OAuth client

With an OAuth client, effective rights are the **intersection** of the client's
and its creator's, so a client made by a restricted user cannot manage what that
user cannot. This surprises people whose pipeline works locally and fails in CI
under a service identity.

## Order of configurations

`guides/order-of-configurations` — configurations have dependencies, and
applying them in the wrong order fails or produces a half-configured
environment. This is the main thing Monaco knows that a naive API script does
not.

## Monaco v1 to v2

- `guides/migrating-to-v2`
- `guides/deprecated-migration`

Both are in the corpus's migration set alongside the OpenPipeline and metric
migrations; see `classic-vs-latest.md`.

`guides/nam-workaround` and
`guides/configuration-as-code-advanced-use-case` cover the awkward cases.

## Terraform

`deliver/configuration-as-code/terraform`: `resources`, `terraform-cli`,
`terraform-cli-commands`, `best-practices`, and
`terraform-api-support-access-permission-handling`.

The same rule applies: check the API support and permission-handling page before
promising a resource exists.

GCP onboarding also ships **Terraform scripts** as a first-class path
(`ingest-from/google-cloud-platform/gcp-terraform-scripts`), which is separate
from the Dynatrace Terraform provider — those scripts configure the *cloud* side
of the connection. See `ingest-cloud.md`.

## What each can actually manage

Rather than guessing, grep the support pages:

```bash
grep -rn "Site Reliability Guardian" \
  {{DOCS_CORPUS}}/deliver/configuration-as-code --include=*.md
```

Things that are explicitly documented as config-as-code manageable:

- **Site Reliability Guardian** — `deliver/site-reliability-guardian/config-as-code-srg`
- **Settings objects** — the 466 `builtin:*` schemas under
  `dynatrace-api/environment-api/settings`
- Dashboards and notebooks are documents, reachable through the document API —
  see `dashboards-notebooks.md`

## Things worth putting in code

In rough order of how much pain manual drift causes:

1. **OpenPipeline pipelines and routing.** The Storage and Permissions stages
   take first match only, so processor *order* is part of the configuration.
   Order drift is invisible until records land in the wrong bucket. See
   `openpipeline.md`.
2. **IAM policies and boundaries.** The 100-statement and 200-policy limits mean
   these get refactored, and a refactor without version control is a guess. See
   `iam-grail-permissions.md`.
3. **Site Reliability Guardians**, which belong next to the pipeline they gate.
4. **Anomaly detection configurations**, especially after transpiling classic
   metric events — the transformation auto-disables the original and the check
   does not verify correctness. See `davis-problems.md`.
5. **Bucket definitions**, because records cannot move between buckets after
   ingest and hundreds of buckets by hand is explicitly an anti-pattern. See
   `grail-and-data-organization.md`.
