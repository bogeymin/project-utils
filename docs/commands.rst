********
Commands
********

archiveproject
==============

Place a project in the archive.

.. code-block:: plain

    usage: archiveproject [-h] [--force] [-p= PROJECT_HOME] [-v] [--version] project_name

    positional arguments:
      project_name          The name of the project to archive.

    optional arguments:
      -h, --help            show this help message and exit
      --force               Archive the project even if the repo is dirty. Be
                            careful!
      -p= PROJECT_HOME, --path= PROJECT_HOME
                            Path to where projects are stored. Defaults to
                            /Users/shawn/Work
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.

    We first check to see if the repo is dirty and by default the project cannot be placed in the archive without first
    committing the changes.


bumpversion
===========

Increment the version number immediately after checking out a release branch.

.. code-block:: plain

    usage: bumpversion [-h] [-b= BUILD] [-M] [-m] [-n= NAME] [-p] [-P= PATH]
                      [--preview] [-s= STATUS] [-T= TEMPLATE] [-v] [--version]
                      [project_name]

    positional arguments:
      project_name          The name of the project. Typically, the directory name
                            in which the project is stored.

    optional arguments:
      -h, --help            show this help message and exit
      -b= BUILD, --build= BUILD
                            Supply build meta data.
      -M, --major           Increase the major version number when you make
                            changes to the public API that are backward-
                            incompatible.
      -m, --minor           Increase the minor version number when new or updated
                            functionality has been implemented that does not
                            change the public API.
      -n= NAME, --name= NAME
                            Name your release.
      -p, --patch           Increase the patch level when backward-compatible bug-
                            fixes have been implemented.
      -P= PATH, --path= PATH
                            The path to where projects are stored. Defaults to
                            /Users/shawn/Work
      --preview             Preview the output, but don't make any changes.
      -s= STATUS, --status= STATUS
                            Use the status to denote a pre-release version.
      -T= TEMPLATE, --template= TEMPLATE
                            Path to the version.py template you would like to use.
                            Use ? to see the default.
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.


.. tip::
    If you omit the ``project_name`` then ``bumpversion`` will attempt to locate the ``VERSION.txt`` file to
    automatically determine the current project name based on your current working diretory.

When to Use
-----------

Generally, you want to increment the version number immediately after checking out a release branch. However, you may
wish to bump the version any time during development, especially during early development where the MINOR and PATCH
versions are changing frequently.

Here is an example workflow:

.. code-block:: bash

    # Get the current version and check out the next release.
    bumpversion myproject; # get the current version, example 1.2
    git checkout -b release-1.3;

    # Bump automatically sets the next minor version with a status of d.
    bumpversion myproject -m -s d;

    # Commit the bump.
    git commit -am "Version Bump";

    # Go do the final work for the release.
    # ...

    # Merge the release.
    git checkout master;
    git merge --no-ff release-1.3;
    git tag -a 1.3;

    # Merge back to development.
    git checkout development;
    git merge --no-ff release-1.3;

Semantic Versioning
-------------------

This utility makes use of [Semantic Versioning](semver.org). From the documentation:

1. MAJOR version when you make incompatible API changes,
2. MINOR version when you add functionality in a backwards-compatible manner, and
3. PATCH version when you make backwards-compatible bug fixes.

Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.

Status
......

We define the following status codes:

- x Prototype, experimental. Use at your own risk.
- d Development. Unstable, untested.
- a Feature complete.
- b Ready for testing and QA.
- r Release candidate.
- o Obsolete, deprecated, or defect. End of life.

You may of course use whatever status you like.

Release Versus Version
----------------------

Release
.......

A *release* is a collection of updates representing a new version of the product. A release is represented by the full
string of MAJOR.MINOR.PATCH, and may optionally include the status and build until the release is live.

The release is probably never displayed to Customers or Users.

Version
.......

A *version* represents a specific state of the product. The version is represented by the MAJOR.MINOR string of the
release.

The version may be shown to Customers or Users.

checkoutproject
===============

Check out a project from a source code repository.

.. code-block:: plain

    usage: checkoutproject [-h] [-p= PROJECT_HOME] [-v] [--version]
                           project_name [provider]

    positional arguments:
      project_name          The name of the project. Typically, the directory name
                            in which the project is stored.
      provider              The SCM provider. This may be a base URL or one of
                            bitbucket or github.

    optional arguments:
      -h, --help            show this help message and exit
      -p= PROJECT_HOME, --path= PROJECT_HOME
                            Path to where projects are stored. Defaults to
                            /Users/shawn/Work
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.

.. note::
    Only Git repos are currently supported.

Provider is required the first time you run a checkout on the local machine. Afterward, the information is stored for
the project at ``~/.pyprojectutils/repos/project_name.txt``

If ``bitbucket`` or ``github`` is specified, the ``BITBUCKET_USER`` or ``GITHUB_USER`` environment variables will be
used to assemble the URL.

You may also specify the ``DEFAULT_SCM`` environment variable to automatically use Bitbucket or GitHub. For example:

.. code-block:: bash

    export BITBUCKET_USER="develmaycare";
    export GITHUB_USER="develmaycare";
    export DEFAULT_SCM="github";

The ``DEFAULT_SCM`` itself defaults to GITHUB_USER.

enableproject
=============

Re-enable a project from hold or archive.

.. code-block:: plain

    usage: enableproject [-h] [-p= PROJECT_HOME] [-v] [--version] project_name

    positional arguments:
      project_name          The name of the project to restore from hold or
                            archive.

    optional arguments:
      -h, --help            show this help message and exit
      -p= PROJECT_HOME, --path= PROJECT_HOME
                            Path to where projects are stored. Defaults to
                            /Users/shawn/Work
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.

    We first check to see if the repo is dirty and by default the project cannot be placed on hold without first
    committing the changes.

exportgithub
============

Export Github milestones and issues.

.. code-block::

    usage: exportgithub [-h] [--format= {csv,html,markdown,rst,txt}]
                        [-L= LABELS] [-v] [--version]
                        repo_name [output_file]

    positional arguments:
      repo_name             Name of the repository.
      output_file           The file (or path) to which data should be exported.
                            If omitted, the export goes to STDOUT.

    optional arguments:
      -h, --help            show this help message and exit
      --format= {csv,html,markdown,rst,txt}
                            Output format. Defaults to CSV.
      -L= LABELS, --label= LABELS
                            Filter for a specific label.
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.

Environment Variables
=====================

``GITHUB_USER`` and ``GITHUB_PASSWORD`` must be set in your console environment.

Issue Status
============

We look for labels of ``ready``, ``in progress``, ``on hold``, and ``review ``to determine the issue's current position
in the workflow.

Output Formats
==============

CSV (Roadmunk)
--------------

The default output (CSV) may be further parsed by your own scripts. However, it was created to conform with the
excellent `Roadmunk`_ application, which is like a Swiss army knife for displaying road map data.

.. _Roadmunk: http://roadmunk.com

HTML
----

HTML output is for `Bootstrap 3`_ and includes classes for ``table-bordered`` and ``table-striped``. If you don't want
this, use the ``--no-header`` switch.

.. _Bootstrap 3: http://getbootstrap.com

Markdown
--------

Markdown output uses the format for the ``pipe_tables`` extension of `Pandoc`_. The output is *not* pretty, but should
parse well using Pandoc.

.. _Pandoc: http://pandoc.org/MANUAL.html#tables

ReStructuredText
----------------

ReStructuredText output uses the `csv-table`_ directive.

.. _csv-table: http://docutils.sourceforge.net/docs/ref/rst/directives.html#id4

Text
----

The final format available is plain text. This simply outputs the issue title, the URL, and a line feed for each issue.
This is useful for creating a ``TODO.txt`` file.

holdproject
===========

Place a project on hold.

.. code-block:: plain

    usage: holdproject [-h] [--force] [-p= PROJECT_HOME] [-v] [--version]
                       project_name

    positional arguments:
      project_name          The name of the project to place on hold.

    optional arguments:
      -h, --help            show this help message and exit
      --force               Hold the project even if the repo is dirty.
      -p= PROJECT_HOME, --path= PROJECT_HOME
                            Path to where projects are stored. Defaults to
                            /Users/shawn/Work
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.

This does a couple of things for you:

- It checks to see if there are uncommitted changes and by default prevents moving the project if the repo is dirty.
- It moves the project to ``$PROJECTS_ON_HOLD`` which defaults to ``$PROJECT_HOME/.hold``.

initproject
===========

Initialize a project, creating various common files using intelligent defaults. Or at least *some* defaults.

.. code-block:: plain

    usage: initproject [-h] [-b= BUSINESS_NAME] [-B= BUSINESS_CODE]
                       [-c= CATEGORY] [--client= CLIENT_NAME]
                       [--client-code= CLIENT_CODE] [-d= DESCRIPTION]
                       [-L= LICENSE_CODE] [-p= PROJECT_HOME] [--prompt=]
                       [-s= STATUS] [--title= TITLE] [-t= PROJECT_TYPE] [-v]
                       [--version]
                       project_name

    positional arguments:
      project_name          The name of the project. The directory will be created
                            if it does not exist in $PROJECT_HOME

    optional arguments:
      -h, --help            show this help message and exit
      -b= BUSINESS_NAME, --business= BUSINESS_NAME
                            Set the name of the developer organization.
      -B= BUSINESS_CODE     Business code. If omitted it is automatically dervied
                            from the business name.
      -c= CATEGORY, --category= CATEGORY
                            Project category. For example, django or wagtail.
                            Default is "uncategorized".
      --client= CLIENT_NAME
                            Set the name of the client organization.
      --client-code= CLIENT_CODE
                            Client code. If ommited it is automatically dervied
                            from the client name.
      -d= DESCRIPTION, --description= DESCRIPTION
                            A brief description of the project.
      -L= LICENSE_CODE, --license= LICENSE_CODE
                            License code. Use lice --help for list of valid codes.
      -p= PROJECT_HOME, --path= PROJECT_HOME
                            Path to where projects are stored. Defaults to
                            /Users/shawn/Work
      --prompt=             Prompt for options rather than providing them via the
                            command line.
      -s= STATUS, --status= STATUS
                            Filter by project status. Use ? to list available
                            statuses.
      --title= TITLE        Specify the project title. Defaults to the project
                            name.
      -t= PROJECT_TYPE, --type= PROJECT_TYPE
                            Specify the project type. Defaults to "project".
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.

lsdependencies
==============

List the packages for a given project.

.. code-block:: plain

    usage: lspackages [-h]
                      [--env= {base,control,development,testing,staging,live}]
                      [--format= {ansible,command,markdown,plain,rst,table}]
                      [--manager= {apt,brew,gem,npm,pip}] [-O= OUTPUT_FILE]
                      [-p= PROJECT_HOME] [-v] [--version]
                      project_name

    positional arguments:
      project_name          The name of the project.

    optional arguments:
      -h, --help            show this help message and exit
      --env= {base,control,development,testing,staging,live}
                            Filter by environment.
      --format= {ansible,command,markdown,plain,rst,table}
                            Output format.
      --manager= {apt,brew,gem,npm,pip}
                            Filter by package manager.
      -O= OUTPUT_FILE, --output= OUTPUT_FILE
                            Path to the output file, if any.
      -p= PROJECT_HOME, --path= PROJECT_HOME
                            Path to where projects are stored. Defaults to
                            /Users/shawn/Work
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.

Location of the INI
-------------------

The command will look for the ``packages.ini`` file in these locations within project root:

1. ``deploy/requirements/packages.ini``
2. ``requirements/packages.ini``
3. ``requirements.ini``

Format of INI
-------------

The ``packages.ini`` contains a section for each package.

.. code-block:: ini

    [package_name]
    ...

The following options are recognized:

- branch: The branch to use when downloading the package. Not supported by all package managers.
- cmd: The install command. This is generated automatically unless this option is given.
- docs: The URL for package documentation.
- egg: The egg name to use for a Python packackage install.
- env: The environment where this package is used.
- home: The URL for the package home page.
- manager: The package manager to use. Choices are apt, brew, gem, npm, and pip.
- note: Any note regarding the package. For example, how or why you are using it.
- scm: The URL for the package's source code management tool.
- title: A title for the package.
- version: The version spec to use for installs. For example: ``>=1.10``

Output Formats
--------------

Several output formats are supported. All are sent to standard out unless a file is specified using ``--output``.

- ansible: For Ansible deployment.
- command: The install command.
- markdown: For Markdown.
- plain: For requirements files.
- rst: For ReStructuredText.
- table (default): Lists the packages in tabular format.

lsdocumentation
===============

Find, parse, and collect documentation information.

We use the excellent `Dash`_ app for documentation, but some documentation is nice to have on the local machine.
This may even be extended to cover training materials, e-books, etc.

.. _Dash: https://kapeli.com/dash

..code-block:: plain

    usage: lsdocumentationy [-h] [-a] [-d] [-f= CRITERIA]
                            [-p= DOCUMENTATION_HOME] [-v] [--version]

    optional arguments:
      -h, --help            show this help message and exit
      -a, --all             Show documentation even if there is no info.ini file.
      -d, --disk            Calculate disk space. Takes longer to run.
      -f= CRITERIA, --filter= CRITERIA
                            Specify filter in the form of key:value. This may be
                            repeated. Use ? to list available values.
      -p= DOCUMENTATION_HOME, --path= DOCUMENTATION_HOME
                            Path to the documentation library. Defaults to
                            /Users/shawn/Dropbox/Business/Documentation
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.

    FILTERING

    Use the -f/--filter option to by most project attributes:

    - author (partial, case insensitive)
    - category
    - description (partial, case insensitive)
    - name (partial, case insensitive)
    - publisher (partial, case insensitive)
    - tag
    - type



lsprojects
==========

List projects managed on the local machine.

.. code-block:: plain

    usage: lsprojects [-h] [-a] [--archive] [--branch] [--dirty] [-d]
                      [-f= CRITERIA] [--hold] [-p= PROJECT_HOME] [-v]
                      [--version]

    optional arguments:
      -h, --help            show this help message and exit
      -a, --all             Show projects even if there is no project.ini file.
      --archive             Only list projects that are staged for archiving.
      --branch              Show the current SCM branch name for each project.
      --dirty               Only show projects with dirty repos.
      -d, --disk            Calculate disk space. Takes longer to run.
      -f= CRITERIA, --filter= CRITERIA
                            Specify filter in the form of key:value. This may be
                            repeated. Use ? to list available values.
      --hold                Only list projects that are on hold.
      -p= PROJECT_HOME, --path= PROJECT_HOME
                            Path to where projects are stored. Defaults to
                            /Users/shawn/Work
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.

    FILTERING

    Use the -f/--filter option to by most project attributes:

    - category
    - description (partial, case insensitive)
    - name (partial, case insensitive)
    - org (business/client code)
    - scm
    - tag
    - type

Format of INI
-------------

You can provide a ``project.ini`` file to provide detail on the project that
cannot be gleaned from the file system.

.. code-block:: ini

    [project]
    category = django
    description = A description of the project.
    status = development
    tags = CRM, Sales
    title = Project Title
    type = website

    [business]
    code = PTL
    name = Pleasant Tents, LLC

    [client]
    code = ACME
    name = ACME, Inc

    [domain]
    name = example
    tld = com

The ``tags``, ``type``, ``scope``, and ``status`` may be whatever you like.

Sections
--------

Attributes of ``[project]`` section are used as is. ``[business]`` and
``[client]`` are used to identify the beneficiary and/or developer of the
project.

Other sections may be added as you see fit. For example, the ``[domain]``
section above.

Additional Data
---------------

Additional data may be displayed in the list output and when using the
``--name`` switch.

- The SCM and disk usage of the project may be automatically determined.
- The project tree is obtained with the ``tree`` command.

Generating a README
-------------------

The ``--name`` switch searches for a specific project and (if found) outputs
project information in `Markdown`_ format:

.. _Markdown: http://daringfireball.net/projects/markdown/

.. code-block:: bash

    cd example_project;
    lsprojects --name=example_project > README.markdown;

Although you'll likely want to customize the output, this is handy for
creating (or recreating) a README for the project.

Projects On Hold
----------------

The ``$PROJECT_HOME`` directory tends to build up a lot of projects, many of which are not active. You may place
projects on hold with the ``holdproject`` command or simply move the project to ``$PROJECTS_ON_HOLD``.

To display projects that are on hold, use the ``--hold`` option if ``lsprojects``.

lsrepos
=======

List source code repos that have been discovered by the checkoutproject command.

..  code-block:: plain

    usage: lsrepos [-h] [-a] [-f= CRITERIA] [--hold] [-v] [--version]

    optional arguments:
      -h, --help            show this help message and exit
      -a, --all             List all (even remote) repos.
      -f= CRITERIA, --filter= CRITERIA
                            Specify filter in the form of key:value. This may be
                            repeated. Use ? to list available values.
      --hold                Only list projects that are on hold.
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.

    FILTERING

    Use the -f/--filter option to by most project attributes:

    - name (partial, case insensitive)
    - project
    - host (bitbucket, bb, github, gh)
    - type (git, hg, svn)
    - user

randompw
========

Generate a random password.

.. code-block:: plain

    usage: randompw [-h] [--format= [{crypt,md5,plain,htpasswd}]] [--strong]
                    [-U] [-v] [--version]

    optional arguments:
      -h, --help            show this help message and exit
      --format= [{crypt,md5,plain,htpasswd}]
                            Choose the format of the output.
      --strong              Make the password stronger.
      -U                    Avoid ambiguous characters.
      -v                    Show version number and exit.
      --version             Show verbose version information and exit.

We often need to generate passwords automatically. This utility does just
that. Install pyprojectutils during deployment to create passwords on the fly.