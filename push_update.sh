#!/usr/bin/env bash

set -euo pipefail

# Resolve repository root to the directory where this script lives
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
BRANCH="$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)"

# Options
RETRY_COUNT=0
FORCE_PUSH=false

usage() {
  cat <<EOF
Usage: $(basename "$0") [--retry N] [--force]

  --retry N   Retry push up to N times on non-fast-forward (default 0)
  --force     Force push with lease on final attempt
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --retry)
      shift
      RETRY_COUNT=${1:-0}
      if ! [[ "$RETRY_COUNT" =~ ^[0-9]+$ ]]; then
        echo "[push_update] Invalid retry count: $RETRY_COUNT" >&2
        exit 1
      fi
      ;;
    --force)
      FORCE_PUSH=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[push_update] Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift || true
done

# Stage all changes and commit if needed
echo "[push_update] Staging changes..."
git -C "$REPO_ROOT" add -A
if ! git -C "$REPO_ROOT" diff --cached --quiet; then
  echo "[push_update] Generating AI commit message..."
  COMMIT_MSG=$(OPENCODE_DISABLE_MODELS_FETCH=1 bun run --cwd packages/opencode script/ai-msg.ts)
  if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="update"
  fi
  echo "[push_update] Committing changes with message: $COMMIT_MSG"
  git -C "$REPO_ROOT" commit -m "$COMMIT_MSG"
else
  echo "[push_update] No changes to commit."
fi

# Fetch latest and rebase (if remote branch exists)
echo "[push_update] Fetching from origin..."
git -C "$REPO_ROOT" fetch --prune origin

if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
  echo "[push_update] Rebasing onto origin/$BRANCH..."
  git -C "$REPO_ROOT" pull --rebase --autostash origin "$BRANCH"
else
  echo "[push_update] Remote branch origin/$BRANCH does not exist. Will create it on push."
fi

# Push to the current branch (set upstream if missing)
echo "[push_update] Pushing to origin/$BRANCH..."

attempt=0
while true; do
  set +e
  git -C "$REPO_ROOT" push -u origin "$BRANCH"
  status=$?
  set -e

  if [[ $status -eq 0 ]]; then
    echo "[push_update] Push succeeded."
    break
  fi

  if [[ $attempt -lt $RETRY_COUNT ]]; then
    attempt=$((attempt + 1))
    echo "[push_update] Push failed (attempt $attempt/$RETRY_COUNT). Fetching and rebasing, then retrying..."
    git -C "$REPO_ROOT" fetch --prune origin
    git -C "$REPO_ROOT" pull --rebase --autostash origin "$BRANCH" || true
    continue
  fi

  if [[ "$FORCE_PUSH" == true ]]; then
    echo "[push_update] Final attempt with force-with-lease..."
    git -C "$REPO_ROOT" push --force-with-lease -u origin "$BRANCH"
    echo "[push_update] Push succeeded (force-with-lease)."
    break
  fi

  echo "[push_update] Push failed and retries exhausted. Consider using --force." >&2
  exit 1
done

echo "[push_update] Done."


