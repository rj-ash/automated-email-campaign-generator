

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