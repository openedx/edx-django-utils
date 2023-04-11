from docutils import nodes
import shutil

from docutils.parsers.rst import Directive
from os import path, walk, symlink, path, mkdir
import sys

from sphinx.builders import Builder
from sphinx.util import logging

logger = logging.getLogger(__name__)

def should_remove_dir(doc_root, repo_root, subdir):
    always_remove = subdir in ["build", "dist", ".tox", ".github", ".git", ".idea", '__pycache__']
    egg = subdir.endswith("egg-info")
    if always_remove or egg:
        return True
    is_doc_root = path.abspath(subdir) == path.abspath(doc_root)
    return is_doc_root

def rm_symlinks(app, exception):
    srcdir = app.srcdir
    symlink_dir = app.config.symlink_sub_dir
    shutil.rmtree(path.join(srcdir, symlink_dir))

def symlink_a_lot(app, config):
    srcdir = app.srcdir
    symlink_dir = config.symlink_sub_dir
    try:
        mkdir(path.join(srcdir, symlink_dir))
    except FileExistsError:
        pass
    logger.info(f"{srcdir=}")

    for root, dirs, files in walk(config.repo_root, topdown=True):

        if path.commonpath([srcdir, root]) == srcdir:
            continue
        try:
            if not root == config.repo_root:
                new_dir = path.join(srcdir, symlink_dir, path.relpath(root, start=config.repo_root))
                logger.info(f"============{root=}================")
                logger.info(f"============{new_dir=}=============")
                mkdir(new_dir)
        except FileExistsError:
            pass
        [dirs.remove(d) for d in list(dirs) if should_remove_dir(srcdir, config.repo_root, d)]
        for afile in files:
            if afile.endswith('.rst'):
                full_path = path.join(root, afile)
                the_symlink = path.join(srcdir, symlink_dir, path.relpath(path.join(root, afile), start=config.repo_root))
                logger.info(f"============== {full_path=}, {the_symlink=} ===========")
                try:
                    symlink(full_path, the_symlink)
                except FileExistsError:
                    pass

    
    
def setup(app):
    app.add_config_value("repo_root", "", 'html', [str])
    app.add_config_value("symlink_sub_dir", "symlinks", 'html', [str])


    app.connect('config-inited', symlink_a_lot)
    app.connect('build-finished', rm_symlinks)


    return {

        'version': '0.1',

        'parallel_read_safe': True,

        'parallel_write_safe': True,

    }
