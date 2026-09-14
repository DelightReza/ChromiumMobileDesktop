import sys
import requests

CDN_BASE = "https://googleapis.com"
PREFIX = "AndroidDesktop_arm64"
ZIP_FILENAME = "chrome-android-desktop.zip"
WEB_VIEWER_URL = "https://googleapis.com/index.html"

def get_latest_chromium_link():
    print("🤖 Fetching latest build number from public storage stream...")
    lc_url = f"{CDN_BASE}/{PREFIX}/LAST_CHANGE"
    
    try:
        response = requests.get(lc_url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to reach storage path. HTTP Status: {response.status_code}")
            sys.exit(1)
            
        latest_version = int(response.text.strip())
        print(f"🔄 Latest revision found: {latest_version}. Verification check...")
        
        checked_builds = 0
        while checked_builds < 50:
            direct_download_url = f"{CDN_BASE}/{PREFIX}/{latest_version}/{ZIP_FILENAME}"
            check = requests.head(direct_download_url, timeout=5)
            
            if check.status_code == 200:
                directory_viewer_url = f"{WEB_VIEWER_URL}?prefix={PREFIX}/{latest_version}/"
                
                # Write results to a file for GitHub Actions to capture
                with open("latest_chromium_links.txt", "w") as f:
                    f.write(f"BUILD_VERSION={latest_version}\n")
                    f.write(f"DOWNLOAD_URL={direct_download_url}\n")
                    f.write(f"WEB_URL={directory_viewer_url}\n")
                
                print(f"✅ Success! Links saved for build: {latest_version}")
                return
                
            latest_version -= 1
            checked_builds += 1
            
        print("❌ Timeout: No matching live files discovered.")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    get_latest_chromium_link()
