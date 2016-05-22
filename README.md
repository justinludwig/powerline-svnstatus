Powerline SVN Status
====================

A [Powerline](https://github.com/powerline/powerline) segment for showing the status of a [Subversion](https://subversion.apache.org/) working directory. Inspired by Jasper N. Brouwer's [Powerline Gitstatus](https://github.com/jaspernbrouwer/powerline-gitstatus) segment.

It includes a segment for the Subversion trunk/branch/tag you're working on, as well as individual segments that summarize status of your current working directory. For example, if you have a clean working copy, you'll just see a segment with the trunk/branch/tag name as its text; if you create a new untracked file, you'll see an additional segment with the text `? 1` (signifying 1 untracked file); if you stage that file for addition, you'll see a segment with the text `A 1` (signifying 1 added file).

![screenshot][https://github.com/justinludwig/powerline-svnstatus/blob/master/screenshot.png]

Installation
------------

Install Powerline and this segment (say via Pip), then add this to your segment configuration; this is what I use in my `~/.config/powerline/themes/shell/default_leftonly.json`:

```json
			{
				"function": "powerline_svnstatus.svnstatus",
				"priority": 40
			},
```

Configuration
-------------

You can adjust what this segment displays as its "branch". By default, it runs this regular expression against the URL returned by the `svn info` command, and concatenates the matching groups: `/(trunk)(?:/|$)|/(?:tags|branch(?:es)?)/([^/]+)`. So for example, if the URL of your working copy was `https://repo.example.com/svn/foo/trunk`, it would display `trunk` as the "branch"; if the URL was `https://repo.example.com/svn/foo/branches/xyz`, it would display `xyz` as the "branch".

You can use the `branch_re` argument to customize this regular expression. So for example if you wanted to also show the "project" that the branch was a part of (so as to show `foo/trunk` for an URL like `https://repo.example.com/svn/foo/trunk` or `foo/1.2.3` for an URL like `https://repo.example.com/svn/foo/tags/1.2.3`), you could adjust your segment configuration to this:

```json
			{
				"function": "powerline_svnstatus.svnstatus",
                "args": {
                    "branch_re": "([^/]+)(?:(/trunk)(?:/|$)|/(?:tags|branch(?:es)?)(/[^/]+))"
                },
				"priority": 40
			},
```

Colorization
------------

You can adjust the segment colors. By default, it powerline's vcs `branch_clean` group to show the segment when your working directory is clean, and `branch_dirty` when your working directory is dirty (with `branch:divider` to show dividers between segments). But you can also define custom `svnstatus_clean` and `svn_status_dirty` groups for the same purpose, and a `svnstatus_[character]` for each individual status code for the counting segments (`like `svnstatus_A` for the added file count, `svnstatus_?` for the untracked file count, etc). You can also define `svnstatus_unknown` as a fallback for segments with a status character you haven't explicitly defined.

So for example, these are the colors I use, defined in my `~/.config/powerline/colorschemes/default.json`:

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

The `svnstatus_unknown` group will apply to statuses I haven't defined, like `!` or `~`. And the `svnstatus_A+` group applies to added files with history (I could have ommited this, and `A+` segments would simply use the `svnstatus_A` group).
