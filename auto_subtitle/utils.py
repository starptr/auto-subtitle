import os
from typing import Iterator, TextIO
import json
from importlib.metadata import Distribution
import pkg_resources

import git

pkg_is_editable = None
def is_editable():
    global pkg_is_editable
    if pkg_is_editable is None:
        direct_url = Distribution.from_name("auto_subtitle").read_text("direct_url.json")
        pkg_is_editable = json.loads(direct_url).get("dir_info", {}).get("editable", False)
    return pkg_is_editable

def project_dir():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

global_repo = None
def repo():
    global global_repo
    if global_repo is None:
        global_repo = git.Repo(project_dir())
    return global_repo

def get_sha_readable():
    sha = repo().head.object.hexsha
    return sha[:7]

def get_release_version():
    version = pkg_resources.require("auto_subtitle")[0].version
    return version

def get_version():
    if not is_editable():
        return get_release_version()
    is_dirty = repo().is_dirty()
    return f"{get_sha_readable()}{'+dirty' if is_dirty else ''}"


def str2bool(string):
    string = string.lower()
    str2val = {"true": True, "false": False}

    if string in str2val:
        return str2val[string]
    else:
        raise ValueError(
            f"Expected one of {set(str2val.keys())}, got {string}")


def format_timestamp(seconds: float, always_include_hours: bool = False):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def write_srt(transcript: Iterator[dict], file: TextIO):
    for i, segment in enumerate(transcript, start=1):
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True)}\n"
            f"{segment['text'].strip().replace('-->', '->')}\n",
            file=file,
            flush=True,
        )


def filename(path):
    return os.path.splitext(os.path.basename(path))[0]
