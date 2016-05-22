# vim:fileencoding=utf-8:et

from collections import Counter
from powerline.segments import Segment, with_docstring
from powerline.theme import requires_segment_info
from subprocess import PIPE, Popen
import re

@requires_segment_info
class SvnStatusSegment(Segment):

    default_branch_re = '/(trunk)(?:/|$)|/(?:tags|branch(?:es)?)/([^/]+)'

    '''
    Executes `svn info` in the current working directory,
    and returns the lines from stdout and stderr.
    '''
    def execute_info(self, pl, segment_info):
        cwd = segment_info['getcwd']()
        if not cwd: return ''

        proc = Popen(['svn', 'info'], stdout=PIPE, stderr=PIPE)
        out, err = [item.decode('utf-8') for item in proc.communicate()]
        return out.splitlines(), err.splitlines()

    '''
    Searches `svn info` text for "URL: https://example.com/svn/foo/trunk" line;
    then matches `branch_re` against that line,
    and returns all matches as a single string (like 'foo/trunk' or 'ticket123').
    '''
    def parse_info(self, lines, branch_re):
        url = next((x for x in lines if x.startswith('URL: ')), '')
        if not url: return ''

        if not branch_re: branch_re = self.default_branch_re
        match = re.search(branch_re, re.sub(r'^URL: ', '', url))

        return ''.join(match.groups('')) if match else ''

    '''
    Executes `svn status` in the current working directory,
    and returns the lines from stdout and stderr.
    '''
    def execute_status(self, pl, segment_info):
        cwd = segment_info['getcwd']()
        if not cwd: return ''

        proc = Popen(['svn', 'status'], stdout=PIPE, stderr=PIPE)
        out, err = [item.decode('utf-8') for item in proc.communicate()]
        return out.splitlines(), err.splitlines()

    '''
    Extracts from `svn status` the first 7 chars from each line,
    strips the spaces from that, and counts the unique status,
    returning them as a map of status chars to counts
    (like {'A+': 2, '!C': 1, 'D': 3}).
    '''
    def parse_status(self, lines):
        return Counter([re.sub(r' +', '', x[0:7]) for x in lines if not x.startswith('       ')])

    '''
    Returns a segment dictionary, given a status char, count pair ('A+', 2).
    '''
    def build_status_segment(self, pair):
        specific_group = 'svnstatus_%s' % pair[0]
        general_group = 'svnstatus_%s' % pair[0][0] if pair else 'svnstatus_'
        return {
            'contents': '%s %d' % (pair[0], pair[1]),
            'highlight_groups': [
                specific_group, general_group,
                'svnstatus_unknown', 'svnstatus_dirty',
                'branch_dirty', 'svnstatus', 'branch'
            ],
            'draw_inner_divider': True
        }

    '''
    Segment entry point; returns a list of segment dictionaries.
    '''
    def __call__(self, pl, segment_info, branch_re=None):
        segments = []

        out, err = self.execute_info(pl, segment_info)
        if err: return

        # if `svn info` doesn't error, display segment for branch
        branch = self.parse_info(out, branch_re)
        segments.append({
            'contents': u'\ue0a0 %s' % branch,
            'highlight_groups': ['svnstatus_clean', 'branch_clean', 'svnstatus', 'branch'],
            'draw_inner_divider': True
        })

        out, err = self.execute_status(pl, segment_info)
        if err: return
        if not out: return segments

        # if `svn status` returns something, display the branch as dirty
        segments[0]['highlight_groups'] = ['svnstatus_dirty', 'branch_dirty', 'svnstatus', 'branch']

        # add the count of each status type as a separate segment
        counts = self.parse_status(out)
        return segments + [self.build_status_segment(x) for x in counts.items()]

svnstatus = with_docstring(SvnStatusSegment(),
'''Return the status of the Subversion working directory.

Returns a segment showing the branch/tag name of the working directory,
and additional segments for each type of modification
(ie A for Addded, C for Conflicted, D for Deleted, etc)
with the count of files which have that modification type.

:param str branch_re:
    Regex to use to convert URL from `svn info` into short branch name.
    The capturing groups of the regex are concatonated together
    to create the branch name. The default regex is this:
    '/(trunk)(?:/|$)|/(?:tags|branch(?:es)?)/([^/]+)'.

Highlight groups used: ``svnstatus_clean``, ``svnstatus_dirty``, ``svnstatus_unknown``, ``svnstatus``. Also will use per-modification-type groups if available, such as ``svnstatus_A``, ``svnstatus_C``, ``svnstatus_D``, etc.
''')
