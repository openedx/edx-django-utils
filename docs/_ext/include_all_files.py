"""
A Sphinx extension to allow the inclusion of documents that are outside of the main docs directory.

Before building, look in the entire repository (minus the main docs directory) for any .rst files. Symlink these files
inside the main docs directory so they are visible to Sphinx and can be included in index.rst. After the build, removes
the directory containing all the symlinks.

Requires new config values:
repo_root: the absolute path of the root of the repository
symlink_sub_dir: the name of the subdirectory in which to put the symlinks. Default "symlinks"
"""

import shutil
from os import mkdir, path, symlink, walk

from sphinx.util import logging

logger = logging.getLogger(__name__)


def should_remove_dir(subdir):
    """
    Determine if we should skip a directory

    Parameters:
        subdir - a directory returned from os.walk

    Returns:
        True if the directory is only for generated files or should otherwise be ignored
    """
    return subdir in ["build", "dist", ".tox", ".github", ".git", ".idea", '__pycache__'] or subdir.endswith("egg-info")


def rm_symlinks(app, exception):
    """
    Remove the symlink directory
    """
    srcdir = app.srcdir
    symlink_dir = app.config.symlink_sub_dir
    shutil.rmtree(path.join(srcdir, symlink_dir))


def create_symlinks(app, config):
    """
    Create symlinks
    :param app:
    :param config:
    :return:
    """
    srcdir = app.srcdir
    symlink_dir = config.symlink_sub_dir
    try:
        mkdir(path.join(srcdir, symlink_dir))
    except FileExistsError:
        logger.error(f"Cannot create directory for symlinks. Directory {symlink_dir} already exists in {srcdir}")
        raise
    for root, dirs, files in walk(config.repo_root, topdown=True):
        # if we're in a subdirectory of the root docs folder, we can already access all the docs here, so skip
        if path.commonpath([srcdir, root]) == srcdir:
            continue

        [dirs.remove(d) for d in list(dirs) if should_remove_dir(srcdir, config.repo_root, d)]

        try:
            # if necessary, make the new subdir for these symlinks
            if not root == config.repo_root:
                new_dir = path.join(srcdir, symlink_dir, path.relpath(root, start=config.repo_root))
                mkdir(new_dir)
        except FileExistsError:
            logger.info(f"Not making new subdir for {root}, subdir already exists")
            pass

        for doc_file in files:
            # only adds rsts for now
            if doc_file.endswith('.rst'):
                # full_path will be an absolute path like /path/to/repo/app/docs/mydoc.rst
                full_path = path.join(root, doc_file)

                # eg app/docs/mydoc.rst
                relative_to_repo_root = path.relpath(full_path, start=config.repo_root)

                # add the relative path to the doc source directory, eg docs/app/docs/mydoc.rst
                symlink_path = path.join(srcdir, symlink_dir, relative_to_repo_root)
                try:
                    symlink(full_path, symlink_path)
                except FileExistsError:
                    logger.warn(f"Cannot create {symlink_path}, file already exists")
                    pass


def setup(app):
    """
    Entry point into Sphinx
    """
    app.add_config_value("repo_root", "", 'html', [str])
    app.add_config_value("symlink_sub_dir", "symlinks", 'html', [str])
    app.connect('config-inited', create_symlinks)
    app.connect('build-finished', rm_symlinks)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
