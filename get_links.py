import os
import sys
import requests

# Public Storage CDN Paths
CDN_BASE = "https://commondatastorage.googleapis.com/chromium-browser-snapshots"
PREFIX = "AndroidDesktop_arm64"
ZIP_FILENAME = "chrome-android-desktop.zip"
WEB_VIEWER_URL = "https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html"

def get_latest_chromium_link():
    print("🤖 Fetching latest build number from public storage stream...")
    
    # Target the completely open unauthenticated file path directly
    lc_url = f"{CDN_BASE}/{PREFIX}/LAST_CHANGE"
    
    try:
        response = requests.get(lc_url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to reach storage path. HTTP Status: {response.status_code}")
            sys.exit(1)
            
        # Extract the raw revision number text cleanly
        latest_version = int(response.text.strip())
        print(f"🔄 Latest revision found: {latest_version}. Verification check...")
        
        # Backtrack slightly to find the newest iteration active on the web index CDN
        checked_builds = 0
        while checked_builds < 50:
            direct_download_url = f"{CDN_BASE}/{PREFIX}/{latest_version}/{ZIP_FILENAME}"
            
            # Fire an empty quick HEAD request to ensure the zip archive container is fully live
            check = requests.head(direct_download_url, timeout=5)
            
            if check.status_code == 200:
                directory_viewer_url = f"{WEB_VIEWER_URL}?prefix={PREFIX}/{latest_version}/"
                
                print(f"\n✅ Found Latest Web-Synced Build: {latest_version}")
                print("-" * 65)
                print(f"📦 DIRECT ZIP DOWNLOAD LINK:\n{direct_download_url}")
                print("-" * 65)
                print(f"🌐 WEB DIRECTORY BROWSER LINK:\n{directory_viewer_url}")
                print("-" * 65)

                # 🌟 NEW: If running inside GitHub Actions, pass variables to the workflow environment
                if "GITHUB_ENV" in os.environ:
                    with open(os.environ["GITHUB_ENV"], "a") as env_file:
                        env_file.write(f"BUILD_VERSION={latest_version}\n")
                        env_file.write(f"DOWNLOAD_URL={direct_download_url}\n")
                        env_file.write(f"WEB_URL={directory_viewer_url}\n")
                return
                
            latest_version -= 1
            checked_builds += 1
            
        print("❌ Timeout: No matching live files discovered within the immediate historical range.")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Connection or parsing runtime exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    get_latest_chromium_link()
