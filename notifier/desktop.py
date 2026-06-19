import subprocess


def send_desktop(title: str, body: str) -> bool:
    """Send a macOS desktop notification via osascript."""
    safe_title = title.replace('"', '\\"').replace("'", "'\\''")
    safe_body = body.replace('"', '\\"').replace("'", "'\\''")
    script = f'display notification "{safe_body}" with title "{safe_title}" sound name "default"'
    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5,
        )
        return True
    except Exception:
        return False
