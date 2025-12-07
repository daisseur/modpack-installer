import os
import shutil
import pathlib
import json

from .util import get_user_preference

def make_global(dir, gdir):
    if not os.path.exists(gdir):
        os.mkdir(gdir)
    
    if not os.path.islink(dir):
        print("Converting %s to a global directory" % dir)
        if os.path.isdir(dir):
            shutil.rmtree(dir) # safe for downloaded things, but not for user created content
        elif os.path.exists(dir):
            os.remove(dir)
        os.symlink(os.path.abspath(gdir), dir, True)
        return True
    return False

def main(override_mcdir=None, override_inst_root=None):
    # TODO add command line arguments to override minecraft/modpack directories
    print("Modpack Maintenance v1.1.0")

    mods = set()

    moved = 0
    deleted = 0

    sandbox = get_user_preference("sandbox")
    mcdir = get_user_preference("minecraft_dir")
    if sandbox and mcdir:
        install_root = str(pathlib.Path(mcdir).parent) + '/modpack'
    else:
        install_root = '.'

    if override_mcdir is not None:
        mcdir = override_mcdir
    if override_inst_root is not None:
        install_root = override_inst_root
        
    print("Using user Minecraft path %s" % mcdir)
    print("Using modpack path %s" % install_root)

    packs_dir = install_root + '/packs'
    if not os.path.exists(packs_dir):
        print("No modpacks directory found at %s" % packs_dir)
        print("Nothing to clean.")
        return

    for packdirn in os.listdir(packs_dir):
        packdir = packs_dir + '/' + packdirn
        upd = make_global(packdir + '/.minecraft/assets', 'global/assets')
        moved += upd
        mods_dir = packdir + '/.minecraft/mods'
        if os.path.exists(mods_dir):
            for mod in os.listdir(mods_dir):
                mods.add(mod)

    modcache_dir = install_root + '/.modcache'
    if os.path.exists(modcache_dir):
        for mod in os.listdir(modcache_dir):
            if mod not in mods:
                print("cleaning up %s" % mod)
                deleted += os.stat(modcache_dir + '/' + mod).st_size
                os.remove(modcache_dir + '/' + mod)

    # clean up launcher profiles
    if mcdir and os.path.exists(mcdir + '/launcher_profiles.json'):
        with open(mcdir + '/launcher_profiles.json', 'r') as f:
            launcher_profiles = json.load(f)

        abs_packdir = pathlib.Path(os.path.abspath(install_root + '/packs'))
        to_remove = []
        for profname in launcher_profiles["profiles"]:
            prof = launcher_profiles["profiles"][profname]
            if "gameDir" in prof:
                abs_dir = pathlib.Path(prof["gameDir"])
                if abs_packdir in abs_dir.parents:
                    # is modpack directory
                    if not os.path.isdir(prof["gameDir"]):
                        # does not exist anymore
                        print("removing profile %s" % profname)
                        to_remove.append(profname)

        for profname in to_remove:
            launcher_profiles["profiles"].pop(profname)

        with open(mcdir + '/launcher_profiles.json', 'w') as f:
            json.dump(launcher_profiles, f, indent=2)

    print("Done! Deleted %.3f MiB of mods and migrated %d data folders" % \
        (deleted / 1048576, moved))

if __name__ == "__main__":
    main()
