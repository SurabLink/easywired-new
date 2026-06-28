# SSH Deploy Setup

This repository uses a single, isolated GitHub Actions workflow for SSH/Rsync deploys:

- Workflow: [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)
- Automatic trigger: push to `main` or `master`
- Manual trigger: `workflow_dispatch`
- Manual default: `rsync --dry-run`

## Required GitHub Secrets

Create these secrets in the repository:

- `STRATO_HOST`
- `STRATO_USER`
- `STRATO_SSH_KEY`

`STRATO_SSH_KEY` must contain the private OpenSSH key for the Strato login.

## Optional GitHub Secrets

These secrets can be added later:

- `STRATO_PORT`, default: `22`
- `STRATO_TARGET_DIR`, default: `/srv/easywired-new`

## Server Side

The public key must already be present in `/home/surab/.ssh/authorized_keys` on the STRATO server.

The workflow does not rely on a local SSH alias such as `strato-server`. It uses the
host, user, and private key from GitHub Secrets and prepares `known_hosts` inside the runner
with `ssh-keyscan`.

The workflow refuses to run if `STRATO_TARGET_DIR` is anything other than `/srv/easywired-new`.
This keeps `rsync --delete` limited to the intended new project directory.

## Behavior

The workflow mirrors the repository with `rsync --delete --itemize-changes`.
Manual runs default to `dry_run=true`, so you can review the exact changes before a real manual deploy.
Pushes to `main` or `master` run the real deploy.

Documentation and GitHub metadata, including `.github/`, are excluded from the server sync.

## First Test

Run the workflow manually with the default `dry_run=true`. If the preview looks right,
pushes to `main` or `master` can deploy the project to `/srv/easywired-new`.
