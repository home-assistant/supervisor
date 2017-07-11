"""Util addons functions."""
import hashlib
import shutil


def create_id(name, date_str):
    """Generate a hash from name & date as id."""
    key = "{} - {}".format(date_str, name).lower().encode()
    return hashlib.sha1(key).hexdigest()[:8]


def remove_folder(folder):
    """Remove folder data but not the folder itself."""
    for obj in folder.iterdir():
        try:
            if obj.is_dir():
                shutil.rmtree(str(obj), ignore_errors=True)
            else:
                obj.unlink()
        except (OSError, shutil.Error):
            pass
