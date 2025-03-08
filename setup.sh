

#!/bin/bash
sudo apt-get update
sudo apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    libgl1 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    python3-pip \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xinput0 \
    libxcb-xfixes0
sudo ln -s /usr/bin/chromium-browser /usr/bin/chrome
sudo ln -s /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver


# Install Chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -yf

# Install ChromeDriver (match the version with Chrome)
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1)
CHROMEDRIVER_URL="https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}"
CHROMEDRIVER_VERSION=$(curl -s "$CHROMEDRIVER_URL")
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/