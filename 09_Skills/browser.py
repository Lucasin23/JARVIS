import subprocess
import urllib.parse


def open_browser(target=None):
    """Open Safari or a website."""

    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "spotify": "https://open.spotify.com",
    }

    try:
        if target:
            target = websites.get(target.strip().lower(), target.strip())

            if not target.startswith("http"):
                target = "https://" + target

            subprocess.run(
                ["open", "-a", "Safari", target],
                
            )
        else:
            subprocess.run(
                ["open", "-a", "Safari"],
            
        )

        return True

    except subprocess.CalledProcessError:
        return False


def search_web(query):
    """Search the web using Google in Safari."""

    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded_query}"

    return open_browser(url)