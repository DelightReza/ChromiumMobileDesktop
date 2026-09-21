import os
import sys

import requests

# Public Chromium snapshot storage paths
CDN_BASE = (
    "https://commondatastorage.googleapis.com/"
    "chromium-browser-snapshots"
)
PREFIX = "AndroidDesktop_arm64"
ZIP_FILENAME = "chrome-android-desktop.zip"
WEB_VIEWER_URL = (
    "https://commondatastorage.googleapis.com/"
    "chromium-browser-snapshots/index.html"
)


def write_github_environment(build_version, download_url, web_url):
    """Export values for GitHub Actions when running in a workflow."""
    github_env = os.environ.get("GITHUB_ENV")

    if not github_env:
        return

    with open(github_env, "a", encoding="utf-8") as env_file:
        env_file.write(f"BUILD_VERSION={build_version}\n")
        env_file.write(f"DOWNLOAD_URL={download_url}\n")
        env_file.write(f"WEB_URL={web_url}\n")


def get_latest_chromium_link():
    print("🤖 Fetching latest build number from public storage stream...")

    last_change_url = f"{CDN_BASE}/{PREFIX}/LAST_CHANGE"

    try:
        response = requests.get(last_change_url, timeout=10)
        response.raise_for_status()

        latest_version = int(response.text.strip())
        print(f"🔄 Latest revision found: {latest_version}. Verification check...")

        checked_builds = 0

        while checked_builds < 50:
            direct_download_url = (
                f"{CDN_BASE}/{PREFIX}/{latest_version}/{ZIP_FILENAME}"
            )

            # Check that the archive is available before publishing it.
            check = requests.head(
                direct_download_url,
                timeout=5,
                allow_redirects=True,
            )

            if check.status_code == 200:
                directory_viewer_url = (
                    f"{WEB_VIEWER_URL}"
                    f"?prefix={PREFIX}%2F{latest_version}%2F"
                )

                print(f"\n✅ Found Latest Web-Synced Build: {latest_version}")
                print("-" * 65)
                print(f"📦 DIRECT ZIP DOWNLOAD LINK:\n{direct_download_url}")
                print("-" * 65)
                print(f"🌐 WEB DIRECTORY BROWSER LINK:\n{directory_viewer_url}")
                print("-" * 65)

                write_github_environment(
                    latest_version,
                    direct_download_url,
                    directory_viewer_url,
                )
                return

            latest_version -= 1
            checked_builds += 1

        print(
            "❌ Timeout: No matching live files discovered "
            "within the immediate historical range."
        )
        sys.exit(1)

    except (requests.RequestException, ValueError) as error:
        print(f"❌ Connection or parsing runtime exception: {error}")
        sys.exit(1)


if __name__ == "__main__":
    get_latest_chromium_link()
