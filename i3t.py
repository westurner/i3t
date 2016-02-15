#!/usr/bin/env python
"""
id_list.py -- list i3wm windows, get next window id, wrap/loop around



History
===========

Version 0.0.1
+++++++++++++++
* The original source of this script is this answer to "How can I
  configure i3wm to make Alt+Tab action just like in Windows?" by
  @michaelschaefer:
  https://faq.i3wm.org/question/1773/how-can-i-configure-i3wm-to-make-alttab-action-just-like-in-windows/?answer=1807#post-id-1807

License
=========
This code is licensed with CC-By-SA 3.0:
    https://creativecommons.org/licenses/by-sa/3.0/legalcode
"""


import collections
import json
import subprocess
import logging
logging.basicConfig()
log = logging.getLogger()

def command_output(cmd, shell=False):
    """
    Execute the given command and return the
    output as a list of lines

    Args:
        cmd (str or list): subprocess.Popen(cmd=cmd)
    Kwargs:
        shell (bool): subprocess.Popen(shell=shell)
    Returns:
        list: list of strings from stdout
    """
    output = []
    if (cmd):
        p = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            output.append(line.rstrip())
    return output


def output_to_dict(output_list):
    """
    Args:
        output_list:
    Returns:
        dict: tree_dict #TODO: ordered_pairs_hook
    """
    output_string = ""
    for line in output_list:
        output_string += line
    return json.loads(output_string)


def find_windows(tree_dict, window_list):
    """
    Args:
        tree_dict: dict of i3 nodes
        window_list: window list to append to
    Returns:
        list: list of windows nodes
    """
    if ("nodes" in tree_dict and len(tree_dict["nodes"]) > 0):
        for node in tree_dict["nodes"]:
            find_windows(node, window_list)
    else:
        if (tree_dict["layout"] != "dockarea"
            and not tree_dict["name"].startswith("i3bar for output")
            and not tree_dict["window"] == None):
            window_list.append(tree_dict)
    return window_list


def get_i3_window_state():
    """
    determine a window id of the 'next' or TODO 'previous' window
    """
    cmd = ("i3-msg", "-t", "get_tree")
    output = subprocess.check_output(cmd)
    tree = output_to_dict(output)
    window_list = find_windows(tree, [])

    # find the current window
    next_index = None
    prev_index = None
    cur_index = None
    for i in range(len(window_list)):
        if (window_list[i]["focused"] == True):
            cur_index = i
            next_index = i+1
            prev_index = i-1
            break

    next_id = None
    if next_index == len(window_list):
        next_index = 0
    if prev_index == -1:
        prev_index = len(window_list)-1

    next_id = window_list[next_index]["window"]
    prev_id = window_list[prev_index]["window"]
    state = collections.OrderedDict((
        ('prev', prev_id),
        ('current', cur_index),
        ('next', next_id)))
    log.debug(('state', state))
    return 0, state

def i3_change_window(window_id):
    """
    Args:
        window_id (int): i3 window id to change window to
    Returns:
        int: output from ``i3-msg [id="0123"] focus``
    """
    cmd = ('i3-msg', '[id="{0:d}"] focus'.format(window_id))
    return subprocess.check_call(cmd)


def main(argv=None):
    argv_len = len(argv)
    if argv_len == 1:
        cmd = argv[0]
        if cmd[0].lower() == 'n':
            cmd = 'next'
        elif cmd[0].lower() == 'p':
            cmd = 'prev'
    elif argv_len == 0:
        cmd = 'next'
    else:
        raise ValueError("specify [n]ext or [p]rev")
    retcode, state = get_i3_window_state()
    new_window_id = state[cmd]
    _ = i3_change_window(new_window_id)
    return retcode


if __name__ == "__main__":
    import sys
    sys.exit(main(argv=sys.argv[1:]))
