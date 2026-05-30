# Audio Transcription Setup

Auto-transcribe Discord audio messages and get transcripts immediately.

## How It Works

1. **You send audio to Skynet** (Discord DM)
2. **OpenClaw receives it** and saves to `~/.openclaw/audio-inbox/`
3. **Cron job runs every 2 minutes**, transcribes via Whisper API
4. **Skynet replies** with the transcript in Discord

## Installation

### Step 1: Make scripts executable

```bash
chmod +x /Volumes/1TB\ External/openclaw/workspace-main/tools/auto-transcribe.sh
chmod +x /Volumes/1TB\ External/openclaw/workspace-main/tools/transcribe-discord-audio.py
```

### Step 2: Test manual transcription

```bash
# Put an audio file in the inbox
cp /path/to/test.m4a ~/.openclaw/audio-inbox/

# Run the transcriber
bash /Volumes/1TB\ External/openclaw/workspace-main/tools/auto-transcribe.sh

# Check output
cat ~/.openclaw/transcripts/test.txt
```

### Step 3: Add to system crontab (optional, for automatic polling)

```bash
crontab -e
```

Add this line:

```cron
*/2 * * * * bash /Volumes/1TB\ External/openclaw/workspace-main/tools/auto-transcribe.sh >> /tmp/transcribe.log 2>&1
```

This runs the transcriber every 2 minutes.

### Step 4: Verify OpenAI API Key

Make sure `OPENAI_API_KEY` is set in your environment:

```bash
echo $OPENAI_API_KEY
```

If empty, add to `~/.zshrc` or `~/.bash_profile`:

```bash
export OPENAI_API_KEY="sk-..."
```

## File Locations

| Path | Purpose |
|------|---------|
| `~/.openclaw/audio-inbox/` | Incoming audio files (from Discord) |
| `~/.openclaw/transcripts/` | Transcribed text files |
| `~/.openclaw/transcripts/.processed` | Log of processed files |
| `~/.openclaw/transcripts/.last-announced` | Log of announced transcripts |

## Supported Audio Formats

- `.mp3`
- `.m4a` (Apple)
- `.ogg`
- `.wav`
- `.flac`
- `.webm`

## Troubleshooting

### "OPENAI_API_KEY not set"

```bash
# Verify key is in environment
echo $OPENAI_API_KEY

# If empty, set it
export OPENAI_API_KEY="sk-..."

# Make persistent in ~/.zshrc or ~/.bash_profile
```

### Transcription times out

- Increase the curl timeout in `transcribe-discord-audio.py` (default: 60 seconds)
- Check OpenAI API status: https://status.openai.com/

### Files not being detected

```bash
# Check what's in the inbox
ls -la ~/.openclaw/audio-inbox/

# Verify file extensions are supported (see table above)
file ~/.openclaw/audio-inbox/myaudio.m4a
```

## Next Steps

Once working, we can:
1. **Integrate with Discord.js** for automatic file detection
2. **Reply directly in threads** instead of separate files
3. **Batch multiple audio files** in one transcript
4. **Add speaker detection** with Whisper prompts

## Manual Run

```bash
bash /Volumes/1TB\ External/openclaw/workspace-main/tools/auto-transcribe.sh
```

Output appears in stdout and in `~/.openclaw/transcripts/`.
