# Pinterest Video Pipeline — launchd Troubleshooting

The pipeline runs as a user LaunchAgent (`com.socialmediaempire.videopipeline`)
that fires every 8 hours and at login. Source-of-truth plist lives at
`scripts/com.socialmediaempire.videopipeline.plist`; deploy with
`bash scripts/install_video_pipeline.sh`.

## Symptom: PermissionError [Errno 1] Operation not permitted

```
/Library/Developer/CommandLineTools/usr/bin/python3: can't open file
'/Users/.../Desktop/social-media-empire/scripts/local_video_pipeline.py':
[Errno 1] Operation not permitted
```

Followed by:

```
Fatal Python error: init_fs_encoding: failed to get the Python codec
of the filesystem encoding
```

### Root cause

macOS Transparency, Consent, and Control (TCC) is denying
`/usr/bin/python3` access to files in `~/Desktop/`. launchd-invoked
binaries do **not** inherit Terminal/iTerm/Claude Code's Full Disk
Access grant — TCC is per-binary. When this happens, Python literally
cannot read its own stdlib codecs from the script's working tree, hence
the misleading `init_fs_encoding` error.

This typically gets triggered by:

- A macOS update that resets the TCC database
- Rotating Command Line Tools
- The first install of the LaunchAgent on a new machine

### Fix

Grant Full Disk Access to `/usr/bin/python3`:

1. **System Settings** → **Privacy & Security** → **Full Disk Access**
2. Click the **+** button
3. **⌘⇧G** ("Go to Folder") → type `/usr/bin` → Enter
4. Select `python3` → **Open**
5. Toggle the entry **ON**

macOS may resolve this to
`/Library/Developer/CommandLineTools/usr/bin/python3` — same binary,
either path is fine.

Then reload the LaunchAgent:

```bash
bash scripts/install_video_pipeline.sh        # idempotent reinstall
launchctl start com.socialmediaempire.videopipeline   # trigger now
```

Confirm:

```bash
launchctl list com.socialmediaempire.videopipeline
# LastExitStatus should read 0 after the next run completes
tail -f logs/video_pipeline.log
```

## Symptom: ModuleNotFoundError on google.genai or supabase

The plist deliberately points at `/usr/bin/python3` because the repo's
`requirements.txt` is installed against the system Python. If you've
switched to homebrew or pyenv Python, those modules won't be on the
sys.path. Fix by reinstalling against system Python:

```bash
/usr/bin/python3 -m pip install -r requirements.txt --user
```

## Manual one-shot run (for debugging)

```bash
cd /Users/homefolder/Desktop/social-media-empire
/usr/bin/python3 scripts/local_video_pipeline.py --test
```

`--test` uses stub content and skips the Supabase write — safe to run
anytime. Drop `--test` for a real drain of pending pins.
