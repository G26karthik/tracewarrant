# Autonomous project completion prompt

Copy the following into a coding session opened in this repository:

```text
Work in this exact folder:
C:\Users\saita\OneDrive\Desktop\AI Everyday\Context - Aware

Take ownership of TraceWarrant, an experimental Python toolkit for content-free
telemetry conformance and simulator-neutral performance-model validation. Complete
the remaining scoped work end to end in this session, using an autonomous
inspect -> act -> verify -> checkpoint -> repeat loop. Start now. Do not wait
for a separate "continue" instruction. This supersedes the earlier assessment-only
and wait instruction.

First read CONTINUATION.md, PROJECT_STATUS.md, PROJECT_V3.md, PUBLIC_RELEASE.md,
HUMAN_ACTION_REQUIRED.md and README.md. Follow the linked contracts, qualification
instructions and inspection evidence when needed. Verify local Git status,
branch/HEAD, tags and code against the notes. Inspect the existing GitHub
repository, existing releases and CI using the available authenticated access.
Treat the documents as leads; current source, tests, artifacts and remote state
outrank stale narrative. Build a short checklist of remaining completion gates.
If a gate is already satisfied, verify it and move on instead of recreating work.
Give a brief initial progress estimate out of 100 and an ETA for the scoped
release, clearly labeled as estimates based on remaining gates, then proceed
without waiting for a reply. Update estimates only when new evidence warrants it.

Objective: finish the experimental v0.3.1 GitHub prerelease, qualify and verify its
public assets, and close out the active documentation with evidence. Stronger
scientific results, production readiness and adoption are not completion gates.

Authorization: make necessary routine code/documentation/release fixes, run
relevant local checks and hosted CI, make coherent Git commits, push the intended
source to the existing G26karthik/tracewarrant repository, create the new release
tag and publish the experimental GitHub prerelease. Choose routine implementation
details yourself. Do not stop for repeated approval, a plan review or a status
acknowledgment. Use existing authentication; never expose credentials.

Completion loop:
1. Inspect the current checklist and choose the next concrete unfinished gate.
2. Perform the work. Keep changes necessary to the scoped toolkit and release.
3. Run the checks that establish that gate. Inspect actual results. If a check
   fails, diagnose the root cause, fix it and verify again. Change approach when
   an attempt is ineffective; do not repeat an unchanged failing command forever.
4. Review changes and evidence, preserve unrelated user work, commit meaningful
   increments and update CONTINUATION.md with completed/pending items, exact
   source SHAs and relevant artifact/run references. Keep raw historical records
   immutable. Use fresh output paths and create their parent directories first.
5. Proceed immediately to the next unfinished gate. Continue this loop while
   useful authorized work remains. Do not end with merely a plan, a partial
   implementation or an offer to continue.

Follow CONTINUATION.md's release checklist in dependency order: choose a clean
final source commit; push it and pass all five CI jobs on that exact SHA; build
fresh wheel/source assets in a clean checkout; run installed-package qualification
and the offline preservation audit; bind checksums and reports to the source;
create the distinct v0.3.1 tag; publish the experimental prerelease; verify remote
asset digests and a public-download installation; record final evidence and URLs.
Recheck whether the release already exists before creating it. Preserve existing
tags; do not force-push, rewrite history or silently replace a published release.

Finish only when all of these are verified:
- The intended source is on remote main and its exact SHA passed required CI.
- v0.3.1 points to the qualified source, and its GitHub release is a published
  experimental prerelease, not an unverified draft.
- Fresh wheel, source distribution, SHA256SUMS and qualification/reproduction
  reports are attached; their uploaded bytes match the recorded checksums.
- A fresh installation from a public download runs the CLI successfully, and
  installed-package qualification reproduces the frozen evaluation.
- Repository/release links and private vulnerability reporting work; active
  documentation records the final URLs, source and evidence accurately.
- Task changes are committed and pushed; historical evidence and unrelated user
  work remain intact. A later documentation commit must not move the release tag.

No PyPI upload, paid calls, cloud provisioning, outreach or unrelated new feature
work is authorized by this prompt. Do not expand the project to invent more work
after the scoped completion gates pass.

Preserve the accepted PIVOT RECOMMENDED conclusion, all 64 protected files,
research-pilot-1, the V3 freeze, original traces and negative findings. Do not
resume the old capacity-planner/native/CUDA/optimizer roadmap. Keep workload_lab
imports, workload-lab compatibility and frozen artifact/telemetry formats.

The V3 core is delivered and all five hosted jobs passed on cede1a4, but the
first GitHub release and final assets were still pending at the checkpoint.
The continuation/status documentation is a later local commit, not yet pushed.
Recheck these facts. Do not upload older candidate files without rebuilding.
Do not report 100/100 for the scoped release until all completion gates pass.
Never equate that completion with production readiness or scientific superiority
to the simple baseline. The FRAMES study retained failed exact-answer quality and
no added intervention-choice value; stronger science and adoption are
unestablished, not prerequisites for this honest experimental release.

Use the existing history and evidence instead of restarting discovery. Send brief
progress updates at meaningful milestones without waiting for replies. Respect
the coding environment's actual tool and permission boundaries.

If a genuine blocker requires my account action or a decision outside this scope,
complete independent work first, record the exact blocker and smallest required
action, then ask only for that input. Never fabricate a result or bypass an access
restriction to satisfy "no intervention". If a hard session/usage/context limit
forces interruption, leave a verified continuation checkpoint and next concrete
step rather than claiming completion. Resume from that checkpoint when possible.

Once every scoped completion gate passes, stop the loop and provide a concise
closeout with repository/release URLs, source/tag, validation evidence and the
unchanged scientific limits. Start by reading the checkpoint and taking the next
authorized action now.
```
