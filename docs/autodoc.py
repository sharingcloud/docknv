"""Autodoc."""

import subprocess
import os
import shutil

# Update docknv modules .rst
print("Updating modules...")
subprocess.call(["sphinx-apidoc", "-f", "-o", ".", "../docknv"])

# Clean build
build_path = os.path.join("_build", "html")
if os.path.exists(build_path):
    print("Removing existing HTML build...")
    shutil.rmtree(build_path)

# Build
print("Building HTML docs...")
if os.name == "nt":
    subprocess.call([".\make.bat", "html"])
else:
    subprocess.call(["make", "html"])
