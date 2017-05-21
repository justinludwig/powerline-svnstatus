Powerline SVN Status
====================

A [Powerline](https://github.com/powerline/powerline) segment for showing the status of a [Subversion](https://subversion.apache.org/) working directory. Inspired by Jasper N. Brouwer's [Powerline Gitstatus](https://github.com/jaspernbrouwer/powerline-gitstatus) segment.

![screenshot](https://github.com/justinludwig/powerline-svnstatus/blob/master/screenshot.png)

It includes a segment for the Subversion trunk/branch/tag you're working on, as well as individual segments that summarize the status of your current working directory. For example, if you have a clean working copy, you'll just see a segment with the trunk/branch/tag name as its text; if you create a new untracked file, you'll see an additional segment with the text `? 1` (signifying 1 untracked file); if you stage that file for addition, you'll see a different segment in its place with the text `A 1` (signifying 1 added file).

Installation
------------

Once you have Powerline set up and running, you can install this segment via Pip:

```
pip install powerline-svnstatus
```

Then add the `powerline_status.svnstatus` segment to your Powerline configuration; this is what I use in my `~/.config/powerline/themes/shell/default_leftonly.json`:

```json
            {
                "function": "powerline_svnstatus.svnstatus",
                "priority": 40
            },
```

Configuration
-------------

You can adjust what this segment displays for a "branch". By default, it runs the following regular expression against the URL returned by the `svn info` command, and concatenates the matching groups from the regular expression: `/(trunk)(?:/|$)|/(?:tags|branch(?:es)?)/([^/]+)`. So for example, if the URL of your working copy was `https://repo.example.com/svn/foo/trunk`, it would display `trunk` as the "branch"; if the URL was `https://repo.example.com/svn/foo/branches/xyz`, it would display `xyz` as the "branch".

You can use the `branch_re` argument in this segment's configuration to customize the branch regular expression. So for example, if you wanted to also show the "project" that the branch was a part of (so as to show `foo/trunk` for an URL like `https://repo.example.com/svn/foo/trunk`, or `foo/1.2.3` for an URL like `https://repo.example.com/svn/foo/tags/1.2.3`), you could adjust your segment configuration to this:

```json
            {
                "function": "powerline_svnstatus.svnstatus",
                "args": {
                    "branch_re": "([^/]+)(?:(/trunk)(?:/|$)|/(?:tags|branch(?:es)?)(/[^/]+))"
                },
                "priority": 40
            },
```

By default, the segment will display a branch symbol () followed by the matched groups from the regular expression. You can change this using the `branch_format` option. This is expected to be a format string, in which `%s` is replaced by the matched groups from the `banch_re` regular expression. You can override the default ` %s` in the same manner shown above.

Finally, if you would like to display information coming from a different line of `svn info` output than the URL, you can change the line to extract by specifying the `line_start` option. The `branch_re` regular expression is run on the line of `svn info` output that starts with this string, after the string has been removed from it. It defaults to `URL: `, as you might expect. Thus, if one line of the `svn info` would be `Repository Root: https://repo.example.com/svn/foo`, you could specify that you are interested in it by setting `"line_start": "Repository Root: "`. The `branch_re` expression would then be run on `https://repo.example.com/svn/foo`.

You can use the above options to display the current revision in the segment, instead of a branch, as follows:

```json
            {
                "function": "powerline_svnstatus.svnstatus",
                "args": {
                    "branch_format": "r%s",
                    "branch_re": "(\\d+)",
                    "line_start": "Revision: "
                },
                "priority": 40
            },
```

As you can see, this specifies that we are interested in the revision (`line_start`), parses out the revision number (`branch_re`) and finally displays it prefixed with a lowercase r (`branch_format`). Your segment could now display `r42`, for example.

Colorization
------------

You can customize this segment's colors. By default, it uses Powerline's vcs `branch_clean` highlight group to show segments when your working directory is clean, and `branch_dirty` when your working directory is dirty (with `branch:divider` to show dividers between segments). But you can also define custom `svnstatus_clean` and `svn_status_dirty` groups for the same purpose, plus a `svnstatus_[character]` for each individual status code for the counting segments (like `svnstatus_A` for the added file count, `svnstatus_?` for the untracked file count, etc). You can also define `svnstatus_unknown` as a fallback for segments with a status character you haven't explicitly defined.

So for example, these are the colors for various highlight groups I use, defined in my `~/.config/powerline/colorschemes/default.json`:

```json
        "svnstatus_clean":           { "bg": "brightgreen", "fg": "black", "attrs": [] },
        "svnstatus_dirty":           { "bg": "brightorange", "fg": "black", "attrs": [] },
        "svnstatus_unknown":         { "bg": "brightred", "fg": "white", "attrs": [] },
        "svnstatus_A":               { "bg": "brightgreen", "fg": "black", "attrs": [] },
        "svnstatus_A+":              { "bg": "mediumgreen", "fg": "black", "attrs": [] },
        "svnstatus_C":               { "bg": "brightestred", "fg": "black", "attrs": [] },
        "svnstatus_D":               { "bg": "mediumorange", "fg": "white", "attrs": [] },
        "svnstatus_I":               { "bg": "gray9", "fg": "black", "attrs": [] },
        "svnstatus_M":               { "bg": "brightyellow", "fg": "black", "attrs": [] },
        "svnstatus_R":               { "bg": "mediumgreen", "fg": "black", "attrs": [] },
        "svnstatus_S":               { "bg": "mediumcyan", "fg": "black", "attrs": [] },
        "svnstatus_X":               { "bg": "mediumpurple", "fg": "black", "attrs": [] },
        "svnstatus_?":               { "bg": "brightestorange", "fg": "black", "attrs": [] },
```

The `svnstatus_unknown` group will apply to statuses I haven't defined, like `!` or `~`. And the `svnstatus_A+` group applies to files with added with a history (I could have omitted this group, and `A+` segments would simply use the `svnstatus_A` group).
