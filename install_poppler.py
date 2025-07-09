#!/usr/bin/env python3
"""
Helper script to download and setup Poppler for Windows
This enables PDF rendering in the EduGesture application.
"""

import os
import sys
import urllib.request
import zipfile
import shutil

def download_poppler():
    """Download and extract Poppler for Windows"""
    print("=== Poppler Installation Helper ===")
    print("This script will download and install Poppler for PDF rendering.")
    
    # Poppler for Windows download URL (community builds)
    poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip"
    poppler_zip = "poppler-windows.zip"
    install_dir = "C:\\poppler"
    
    try:
        # Check if already installed
        if os.path.exists(os.path.join(install_dir, "bin")):
            print(f"Poppler already installed at {install_dir}")
            return True
        
        print("Downloading Poppler for Windows...")
        print(f"URL: {poppler_url}")
        
        # Download the file
        urllib.request.urlretrieve(poppler_url, poppler_zip)
        print("Download completed.")
        
        # Create installation directory
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
            
        print(f"Extracting to {install_dir}...")
        
        # Extract the zip file
        with zipfile.ZipFile(poppler_zip, 'r') as zip_ref:
            zip_ref.extractall(install_dir)
        
        # Clean up
        os.remove(poppler_zip)
        
        # Check if extraction was successful
        bin_path = os.path.join(install_dir, "poppler-24.02.0", "Library", "bin")
        if os.path.exists(bin_path):
            # Move files to expected location
            target_bin = os.path.join(install_dir, "bin")
            if not os.path.exists(target_bin):
                shutil.move(bin_path, target_bin)
            
            print(f"✅ Poppler installed successfully at {install_dir}")
            print("PDF rendering should now work in EduGesture!")
            return True
        else:
            print("❌ Installation failed - files not found in expected location")
            return False
            
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        print("\n=== Manual Installation Instructions ===")
        print("1. Go to: https://github.com/oschwartz10612/poppler-windows/releases")
        print("2. Download the latest Release zip file")
        print("3. Extract to C:\\poppler\\")
        print("4. Ensure the bin folder is at C:\\poppler\\bin\\")
        return False

def check_poppler():
    """Check if Poppler is properly installed"""
    possible_paths = [
        r"C:\poppler\bin",
        r"C:\Program Files\poppler\bin",
        r"C:\Program Files (x86)\poppler\bin",
        r"C:\tools\poppler\bin"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found Poppler at: {path}")
            return True
    
    print("❌ Poppler not found in standard locations")
    return False

if __name__ == "__main__":
    print("Checking for existing Poppler installation...")
    
    if check_poppler():
        print("Poppler is already installed and ready to use!")
    else:
        print("Poppler not found. Starting installation...")
        
        if download_poppler():
            print("\n=== Installation Complete ===")
            print("You can now run the EduGesture application with PDF support!")
        else:
            print("\n=== Installation Failed ===")
            print("Please install Poppler manually or use text-only mode.")
    
    input("\nPress Enter to continue...") 