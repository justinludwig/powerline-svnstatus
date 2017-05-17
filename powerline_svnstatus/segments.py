# vim:fileencoding=utf-8:et

from collections import Counter
from powerline.segments import Segment, with_docstring
from powerline.theme import requires_segment_info
from subprocess import PIPE, Popen
import re

@requires_segment_info
class SvnStatusSegment(Segment):

    default_branch_format = u'\ue0a0 %s'
    default_branch_re = '/(trunk)(?:/|$)|/(?:tags|branch(?:es)?)/([^/]+)'
    default_line_start = 'URL: '

    '''
    Creates environment settings with base locale to use for svn info/status.
    '''
    def make_env(self, segment_info):
        myenv = segment_info['environ'].copy()
        myenv['LANG'] = 'C'
        myenv['LC_MESSAGES'] = 'C'
        return myenv

    '''
    Executes `svn info` in the current working directory,
    and returns the lines from stdout and stderr.
    '''
    def execute_info(self, pl, segment_info):
        cwd = segment_info['getcwd']()
        if not cwd: return ''

        proc = Popen(['svn', 'info', cwd], stdout=PIPE, stderr=PIPE, env=self.make_env(segment_info))
        out, err = [item.decode('utf-8') for item in proc.communicate()]
        return out.splitlines(), err.splitlines()

    '''
    Searches `svn info` text for "URL: https://example.com/svn/foo/trunk" line;
    then matches `branch_re` against that line,
    and returns all matches as a single string (like 'foo/trunk' or 'ticket123').
    When `line_start` is anything other than the default (`None`), a line starting
    with that string is selected and `branch_re` is used on that line.
    '''
    def parse_info(self, lines, branch_re, line_start):
        if not line_start: line_start = self.default_line_start
        url = next((x for x in lines if x.startswith(line_start)), '')
        if not url: return ''

        if not branch_re: branch_re = self.default_branch_re
        match = re.search(branch_re, url[len(line_start):])

        return ''.join(match.groups('')) if match else ''

    '''
    Executes `svn status` in the current working directory,
    and returns the lines from stdout and stderr.
    '''
    def execute_status(self, pl, segment_info):
        cwd = segment_info['getcwd']()
        if not cwd: return ''

        proc = Popen(['svn', 'status', cwd], stdout=PIPE, stderr=PIPE, env=self.make_env(segment_info))
        out, err = [item.decode('utf-8') for item in proc.communicate()]
        return out.splitlines(), err.splitlines()

    '''
    Extracts from `svn status` the first 7 chars from each line,
    strips the spaces from that, and counts the unique status,
    returning them as a map of status chars to counts
    (like {'A+': 2, '!C': 1, 'D': 3}).
    '''
    def parse_status(self, lines):
        return Counter([re.sub(r' +', '', x[0:7]) for x in lines if not re.match(r'       |$|Performing|^Summary of conflicts|^  Text conflicts', x)])

    '''
    Returns true if the parsed status chars from `svn status` indicate
    at least one dirty file.
    '''
    def is_dirty(self, counts):
        return True if [x for x in counts if not x[0] in ['S', 'X']] else False

    '''
    Returns a segment dictionary, given a status char, count pair ('A+', 2).
    '''
    def build_status_segment(self, pair):
        specific_group = 'svnstatus_%s' % pair[0]
        general_group = 'svnstatus_%s' % pair[0][0] if pair[0] else 'svnstatus_'
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
    def __call__(self, pl, segment_info, branch_format=None, branch_re=None,
                 line_start=None):
        segments = []

        out, err = self.execute_info(pl, segment_info)
        if err:
            for e in err:
                if not e.endswith('is not a working copy'):
                    pl.error(e)
            return

        # if `svn info` doesn't error, display segment for branch
        if not branch_format:
            branch_format = self.default_branch_format
        branch = self.parse_info(out, branch_re, line_start)
        segments.append({
            'contents': branch_format % branch,
            'highlight_groups': ['svnstatus_clean', 'branch_clean', 'svnstatus', 'branch'],
            'draw_inner_divider': True
        })

        out, err = self.execute_status(pl, segment_info)
        if err:
            for e in err:
                if not e.endswith('is not a working copy'):
                    pl.error(e)
            return
        if not out: return segments

        counts = self.parse_status(out)
        if not counts: return segments

        # if `svn status` returned dirty results, display the branch as dirty
        if self.is_dirty(counts):
            segments[0]['highlight_groups'] = ['svnstatus_dirty', 'branch_dirty', 'svnstatus', 'branch']

        # add the count of each status type as a separate segment
        return segments + [self.build_status_segment(x) for x in counts.items()]

svnstatus = with_docstring(SvnStatusSegment(),
'''Return the status of the Subversion working directory.

Returns a segment showing the branch/tag name of the working directory,
and additional segments for each type of modification
(ie A for Addded, C for Conflicted, D for Deleted, etc)
with the count of files which have that modification type.

:param str branch_format:
    Format string for segment content. One string argument (`%%s`) is
    substituted by the matched groups of below `branch_re`. Defaults to
    a branch symbol followed by that string.

:param str branch_re:
    Regex to use to convert URL from `svn info` into short branch name.
    The capturing groups of the regex are concatenated together
    to create the branch name. The default regex is this:
    '/(trunk)(?:/|$)|/(?:tags|branch(?:es)?)/([^/]+)'.

:param str line_start:
    String that line of interest from `svn info` output should start
    with. The above regular expression is used on this particular line.
    By default, this is 'URL: ', so that the URL of the repository is
    targeted. The line of output minus this prefix is fed to the
    `branch_re` regular expression.

Highlight groups used: ``svnstatus_clean``, ``svnstatus_dirty``, ``svnstatus_unknown``, ``svnstatus``. Also will use per-modification-type groups if available, such as ``svnstatus_A``, ``svnstatus_C``, ``svnstatus_D``, etc.
''')
