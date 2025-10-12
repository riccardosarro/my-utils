#!/bin/bash

# Script to automatically set ownership and permissions for Burp Suite's chrome-sandbox.

# --- Configuration ---
BURP_BASE_DIR="/home/inxpire/ctftools/BurpSuiteCommunity"
TARGET_FILE="chrome-sandbox"
REQUIRED_OWNER="root"
REQUIRED_MODE="4755"

# --- Functions ---

# Check for root privileges
check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo "Error: This script must be run with root privileges (e.g., using 'sudo')."
        echo "Usage: sudo $0"
        exit 1
    fi
}

# --- Main Script Logic ---

check_root

echo "--- Setting Burp Suite Chrome Sandbox Permissions ---"

# 1. Find the chrome-sandbox file
echo "Searching for '$TARGET_FILE' within '$BURP_BASE_DIR/burpbrowser/...'..."
SANDBOX_PATH=$(find "$BURP_BASE_DIR/burpbrowser" -type f -name "$TARGET_FILE" 2>/dev/null | head -n 1)

if [[ -z "$SANDBOX_PATH" ]]; then
    echo "Error: '$TARGET_FILE' not found in '$BURP_BASE_DIR/burpbrowser/'."
    echo "Please ensure Burp Suite Community is installed correctly or update BURP_BASE_DIR."
    exit 1
else
    echo "Found '$TARGET_FILE' at: $SANDBOX_PATH"
fi

# 2. Get current file details
if [[ -f "$SANDBOX_PATH" ]]; then
    stat_output=$(stat -c "%U %a" "$SANDBOX_PATH" 2>/dev/null)
    CURRENT_OWNER=$(echo "$stat_output" | awk '{print $1}')
    CURRENT_MODE=$(echo "$stat_output" | awk '{print $2}')
else
    echo "Error: File '$SANDBOX_PATH' does not exist after finding. This should not happen."
    exit 1
fi

echo "Current Owner: $CURRENT_OWNER, Current Mode: $CURRENT_MODE"

# 3. Apply required ownership if different
if [[ "$CURRENT_OWNER" != "$REQUIRED_OWNER" ]]; then
    echo "Changing ownership to '$REQUIRED_OWNER'..."
    if ! chown "$REQUIRED_OWNER" "$SANDBOX_PATH"; then
        echo "Error: Failed to change ownership. Check permissions."
        exit 1
    fi
    echo "Ownership set to '$REQUIRED_OWNER'."
else
    echo "Ownership is already '$REQUIRED_OWNER'."
fi

# 4. Apply required permissions if different
if [[ "$CURRENT_MODE" != "$REQUIRED_MODE" ]]; then
    echo "Changing permissions to '$REQUIRED_MODE'..."
    if ! chmod "$REQUIRED_MODE" "$SANDBOX_PATH"; then
        echo "Error: Failed to change permissions. Check installation."
        exit 1
    fi
    echo "Permissions set to '$REQUIRED_MODE'."
else
    echo "Permissions are already '$REQUIRED_MODE'."
fi

# Final verification
echo "--- Verification ---"
stat_output=$(stat -c "%U %a" "$SANDBOX_PATH" 2>/dev/null)
FINAL_OWNER=$(echo "$stat_output" | awk '{print $1}')
FINAL_MODE=$(echo "$stat_output" | awk '{print $2}')

if [[ "$FINAL_OWNER" == "$REQUIRED_OWNER" && "$FINAL_MODE" == "$REQUIRED_MODE" ]]; then
    echo "Success: '$TARGET_FILE' is correctly owned by '$REQUIRED_OWNER' and has mode '$REQUIRED_MODE'."
else
    echo "Warning: Final check failed. Expected owner: $REQUIRED_OWNER, mode: $REQUIRED_MODE. Actual owner: $FINAL_OWNER, mode: $FINAL_MODE."
fi

echo "----------------------------------------------------"
