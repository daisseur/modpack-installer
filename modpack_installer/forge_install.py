#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import time
import shutil
import tempfile
from .util import download

# https://files.minecraftforge.net/maven/net/minecraftforge/forge/1.12.2-14.23.5.2847/forge-1.12.2-14.23.5.2847-universal.jar

def get_forge_url(mcver, mlver):
    index_url = 'https://files.minecraftforge.net/net/minecraftforge/forge/index_%s.html' \
            % mcver

    # Use tempfile for secure temporary file creation
    fd, outpath = tempfile.mkstemp(prefix='forge-%s-index-' % mcver, suffix='.html')
    os.close(fd)  # Close file descriptor, we'll use the path
    
    try:
        resp = download(index_url, outpath, False)
        if resp != 200:
            print("Got %d error trying to download Forge download index" % resp)
            return ""

        with open(outpath, 'r') as f:
            match = re.search(r"href=\".*(https://maven\.minecraftforge\.net/.*-%s-.*\.jar)\"" % mlver, f.read())
            if match:
                url = match.group(1)
            else:
                print("Could not find Forge download URL for version %s (Minecraft version %s)" % (mlver, mcver))
                return ""
        return url
    finally:
        # Clean up temporary file
        if os.path.exists(outpath):
            os.unlink(outpath)

def guess_forge_url(mcver, mlver):
    forge_fullver = mcver + '-' + mlver
    return 'https://maven.minecraftforge.net/net/minecraftforge/forge/%s/forge-%s-installer.jar' % (forge_fullver, forge_fullver)

def main(manifest, mcver, mlver, packname, mc_dir, manual):
    url_providers = [guess_forge_url, get_forge_url]

    # Use tempfile for secure temporary file creation
    fd, outpath = tempfile.mkstemp(prefix='forge-%s-%s-installer-' % (mcver, mlver), suffix='.jar')
    os.close(fd)  # Close file descriptor, we'll use the path

    try:
        for provider in url_providers:
            url = provider(mcver, mlver)
            if not url:
                continue

            resp = download(url, outpath, True)
            if resp == 200:
                break  # Success
            print("Got %d error trying to download Forge" % resp)

        if not os.path.exists(outpath) or os.path.getsize(outpath) == 0:
            print("Failed to download the Forge installer.")
            sys.exit(2)

        # Run the Forge auto-install hack
        if manual:
            print("Using the manual installer!")
            print("***** NEW: INSTALL TO THE MAIN .MINECRAFT DIRECTORY *****")
            print("*****   (Just hit 'OK' with the default settings)   *****")
            for i in range(20):
                print("^ ", end="", flush=True)
                time.sleep(0.05)

            subprocess.run(['java', '-jar', outpath])
        else:
            # Find the ForgeHack.java file location
            import importlib.resources
            try:
                # Python 3.9+
                if hasattr(importlib.resources, 'files'):
                    package_dir = str(importlib.resources.files('modpack_installer'))
                else:
                    # Python 3.7-3.8
                    import pkg_resources
                    package_dir = pkg_resources.resource_filename('modpack_installer', '')
            except:
                # Fallback to current directory
                package_dir = os.path.dirname(os.path.abspath(__file__))
            
            forge_hack_src = os.path.join(package_dir, 'ForgeHack.java')
            
            # Use a secure temporary directory for compilation
            # This prevents potential security issues if the package directory is writable by others
            compile_dir = tempfile.mkdtemp(prefix='forge_hack_')
            try:
                # Copy source to temp directory
                temp_src = os.path.join(compile_dir, 'ForgeHack.java')
                shutil.copy2(forge_hack_src, temp_src)
                
                # Compile in temp directory
                result = subprocess.run(['javac', temp_src], cwd=compile_dir, capture_output=True)
                if result.returncode != 0:
                    print("Error compiling ForgeHack:")
                    print(result.stderr.decode())
                    sys.exit(3)
                
                # Run from temp directory
                exit_code = subprocess.run(['java', '-cp', compile_dir, 'ForgeHack', outpath, mc_dir]).returncode
                if exit_code != 0:
                    print("Error running the auto-installer, try using --manual.")
                    sys.exit(3)
            finally:
                # Clean up temp directory
                shutil.rmtree(compile_dir, ignore_errors=True)

        ver_id = get_version_id(mcver, mlver)
        if not os.path.exists(mc_dir + '/versions/' + ver_id):
            print("Forge installation not found.")
            if manual:
                print("Make sure you browsed to the correct minecraft directory.")
            print("Expected to find a directory named %s in %s" % (ver_id, mc_dir + '/versions'))
            print("If a similarly named directory was created in the expected folder, please submit a")
            print("bug report.")
            sys.exit(3)
    finally:
        # Clean up installer jar
        if os.path.exists(outpath):
            os.unlink(outpath)


def get_version_id(mcver, mlver):
    mcv_split = mcver.split('.')
    mcv = int(mcv_split[0]) * 1000 + int(mcv_split[1])
    mlv_split = mlver.split('.')
    mlv = int(mlv_split[-1]) # modloader patch version

    if mcv < 1008:
        # 1.7 (and possibly lower, haven't checked)
        return '%s-Forge%s-%s' % (mcver, mlver, mcver)
    elif mcv < 1010:
        # 1.8, 1.9
        return '%s-forge%s-%s-%s' % (mcver, mcver, mlver, mcver)
    elif mcv < 1012 or (mcv == 1012 and mlv < 2851):
        # 1.10, 1.11, 1.12 (up to 1.12.2-14.23.5.2847)
        return '%s-forge%s-%s' % (mcver, mcver, mlver)
    else:
        # 1.12.2-14.23.5.2851 and above
        return '%s-forge-%s' % (mcver, mlver)
        
