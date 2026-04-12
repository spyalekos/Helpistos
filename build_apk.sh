#!/bin/bash
# Helpistos — Android APK Build Script
# Σύμφωνα με AI-Instructions: ΠΑΝΤΟΤΕ χρησιμοποιούμε αυτό το script για APK build.

set -e

export JAVA_HOME="$HOME/.cache/briefcase/tools/java17"
export ANDROID_HOME="$HOME/.cache/briefcase/tools/android_sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export GRADLE_OPTS="-Xmx2g -Dorg.gradle.daemon=false"

# Chaquopy needs python3.12 in PATH for cross-compiling pip packages
UV_PYTHON_DIR="$HOME/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/bin"
if [ -d "$UV_PYTHON_DIR" ]; then
    export PATH="$UV_PYTHON_DIR:$PATH"
fi

# Use dedicated briefcase venv with Python 3.12
# (avoids uv sync trying to build pygobject for GTK on Linux)
BRIEFCASE="$(dirname "$0")/.briefcase-venv/bin/briefcase"

echo "=== Helpistos APK Build ==="
echo "JAVA_HOME: $JAVA_HOME"
echo "ANDROID_HOME: $ANDROID_HOME"
echo "GRADLE_OPTS: $GRADLE_OPTS"
echo "Briefcase: $BRIEFCASE"
echo "Python3.12: $(which python3.12 2>/dev/null || echo 'NOT FOUND')"
echo "=========================="

# Check if build dir exists; if not, create first
if [ ! -d "build/helpistos/android" ]; then
    echo ">>> No existing Android build found. Running: briefcase create android"
    "$BRIEFCASE" create android
fi

echo ">>> Updating and Building APK..."

# Sync version in build.gradle
GRADLE_FILE="build/helpistos/android/gradle/app/build.gradle"
APP_VERSION="1.33"
if [ -f "$GRADLE_FILE" ]; then
    echo ">>> Syncing version in build.gradle to $APP_VERSION"
    sed -i "s/versionName \".*\"/versionName \"$APP_VERSION\"/" "$GRADLE_FILE"
fi

"$BRIEFCASE" update android -r
"$BRIEFCASE" build android

echo ">>> Build complete!"
echo ">>> Renaming APK..."
ORIGINAL_APK=$(find build -name "app-debug.apk" -type f | head -n 1)
if [ -n "$ORIGINAL_APK" ]; then
    CLEAN_VER=$(echo $APP_VERSION | tr -d '.')
    MV_DEST="build/helpistos-v${CLEAN_VER}.apk"
    cp "$ORIGINAL_APK" "$MV_DEST"
    echo ">>> APK renamed to: $MV_DEST"
else
    echo ">>> ERROR: app-debug.apk not found!"
fi
