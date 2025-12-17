# Scrypted Subtitles Plugin

A Scrypted NVR plugin that provides **real-time subtitles** and **searchable transcripts** for your camera streams. Designed to run efficiently on low-power hardware like the Intel N100.

![Scrypted Subtitles](https://raw.githubusercontent.com/k2-fsa/sherpa-onnx/master/docs/source/_static/sherpa-onnx-logo.png)

## Features

- ⚡ **Real-time Transcription**: Uses `sherpa-onnx` for high-performance, low-latency speech-to-text.
- 🚀 **Low Power Optimized**: Runs smoothly on Intel N100 and other entry-level CPUs using int8 quantized models.
- 💾 **Searchable History**: Stores all transcripts in a local SQLite database.
- 🔍 **Instant Search & Seek**: Built-in web interface to search for spoken words and instantly jump to that moment in the video.
- 🔌 **Native Integration**: Exposes text as a Scrypted Sensor for use in automations.

## Installation

1.  **Access your Scrypted LXC**:
    SSH into your Proxmox host and enter the Scrypted LXC container (usually ID 100 or similar):
    ```bash
    pct enter <container-id>
    ```
2.  **Navigate to Plugins Directory**:
    ```bash
    cd ~/.scrypted/volume/plugins
    ```
3.  **Create Scope Directory & Clone**:
    It is best practice to use a scope folder (like other plugins).
    ```bash
    mkdir -p @damustermann
    cd @damustermann
    git clone https://github.com/daMustermann/scrypted-subtitles.git scrypted-subtitles
    cd scrypted-subtitles
    ```
4.  **Install Dependencies**:
    First, ensure `pip` is installed (it is often missing in the LXC):
    ```bash
    apt-get update && apt-get install -y python3-pip
    ```
    Then install the required packages:
    ```bash
    pip install scrypted-sdk sherpa-onnx numpy aiohttp
    ```
5.  **Restart Scrypted**: Restart your Scrypted service to load the new plugin.
    ```bash
    systemctl restart scrypted
    ```

## Configuration

1.  Open the Scrypted Management Console.
2.  Go to **Plugins** and select **Scrypted Subtitles**.
3.  **Enable** the plugin for the specific cameras you want to transcribe.
4.  (Optional) Configure the STT model path if you wish to use a custom model (defaults to a downloaded lightweight model).

## Usage

### Viewing Subtitles
- **Live**: Subtitles are published to the camera's sensor value. You can view them in the Scrypted dashboard or use them in automations (e.g., "If camera hears 'help', send notification").

### Searching Transcripts
1.  Navigate to the plugin's web interface: `http://<your-scrypted-ip>:10080/`
2.  Enter a keyword in the search bar.
3.  Click on any result to **play the video** starting from that exact timestamp.

## Technical Details

- **Engine**: [Sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) (Streaming Transducer).
- **Database**: SQLite with FTS5 (Full-Text Search) for millisecond-fast queries.
- **Server**: Asyncio HTTP server (aiohttp) embedded within the plugin.

## Requirements

- Scrypted NVR
- Python 3.9+
- Intel N100 or better recommended (runs on Raspberry Pi 4 with lighter models).

## Troubleshooting

### Plugin Not Showing Up?
If the plugin does not appear in the Scrypted Plugins list after restarting:

1.  **Check Directory**: Ensure you cloned the repo into the correct `plugins` folder.
    ```bash
    ls -l ~/.scrypted/volume/plugins/scrypted-subtitles
    ```
    You should see `package.json` and `plugin.py` directly in this folder.

2.  **Check Logs**: View the Scrypted logs to see if there were errors loading the plugin.
    ```bash
    # In the LXC
    journalctl -u scrypted -f
    ```
    Look for "scrypted-subtitles" or Python syntax errors.

3.  **Manual Reload**: Sometimes Scrypted needs a hard refresh.
    - Restart the service: `systemctl restart scrypted`
    - Refresh your browser cache (Ctrl+Shift+R).

4.  **Permissions**: Ensure the files are owned by the user running Scrypted (usually root in LXC, but check if running as another user).

## License

MIT
