# Imports

from collections import OrderedDict
import commands
import os
from .config import Config, Section
from .constants import DEVELOPER_CODE, DEVELOPER_NAME, ENVIRONMENTS, PROJECT_HOME
from .organizations import Business, Client
from .packaging import PackageConfig
from .shortcuts import parse_template, read_file, write_file, print_info

# Constants

GITIGNORE_TEMPLATE = """*.pyc
.DS_Store
.idea
tmp.*
tmp
"""

PROJECT_INI_TEMPLATE = """[project]
category = $category
description = $description
status = $status
title = $title
type = $type

[business]
code = $business_code
name = $business_name

[client]
code = $client_code
name = $client_name

[domain]
name = example
tld = com

"""

README_TEMPLATE = """# $title

$description

"""

# Exports

__all__ = (
    "autoload_project",
    "get_projects",
    "initialize_project",
    "Project",
)

# Functions


def autoload_project(name, include_disk=False, path=None):
    """Attempt to automatically load the project configuration based on the name and path.

    :param name: The project name, or possible name.
    :type name: str

    :param include_disk: Whether to calculate disk space.
    :type include_disk: bool

    :param path: The path where projects are located.
    :type path: str

    :rtype: Project
    :returns: A ``Project`` instance or ``None`` if the project could not be found.

    """
    name = name.lower()
    names = (
        name,
        name.replace(".", "_"),
        name.replace(" ", "-"),
        name.replace(" ", "_"),
    )

    for name in names:
        root_path = os.path.join(path or PROJECT_HOME, name)
        if os.path.exists(root_path):
            project = Project(name, path=path)
            project.load(include_disk=include_disk)
            return project

    return Project(name, path=path)


def get_clients(path):
    d = dict()
    projects = get_projects(path)

    for p in projects:
        client = p.get_client()

        if client.code in d.keys():
            d[client.code].projects.append(p)
        else:
            client.projects.append(p)
            d[client.code] = client

    return OrderedDict(sorted(d.items(), key=lambda t: t[0]))


def get_distinct_project_attributes(attribute, path=PROJECT_HOME):
    """Get distinct values of the named attribute.

    .. versionadded:: 0.16.0-d

    :param attribute: The name of the attribute.
    :type attribute: str

    :param path: The path to where projects are stored.
    :type path: str

    :rtype: OrderedDict
    :returns: Returns a dictionary where each distinct values is a dictionary key and the total project count is the
              dictionary value. Keys are sorted alphabetically.

    .. note::
        If the given ``attribute`` does not exist on the :py:class:`Project`, the resulting ``AttributeError`` is
        trapped and ``{'Invalid Project Attribute': attribute}`` is returned.

    """
    d = dict()
    projects = get_projects(path)
    for p in projects:
        try:
            value = getattr(p, attribute)
        except AttributeError:
            return {'Invalid Project Attribute': attribute}

        if value in d.keys():
            d[value] += 1
        else:
            d[value] = 1

    return OrderedDict(sorted(d.items(), key=lambda t: t[0]))


def get_projects(path, criteria=None, include_disk=False, show_all=False):
    """Get a list of projects.

    :param path: Path to where projects are stored.
    :type path: str

    :param criteria: Criteria used to filter the list, if any.
    :type criteria: dict

    :param include_disk: Whether to calculate disk space used by the project.
    :type include_disk: bool

    :param show_all: By default, projects without a ``project.ini`` file are omitted. Set this to ``True`` to show all
                     projects.

    :type show_all: bool

    :rtype: list

    .. versionchanged:: 0.16.0-d
        When filtering criteria includes ``name`` or ``description``, these are handled using partial rather than full
        matching. The matching is also case insensitive.

    """
    names = list()
    projects = list()

    entries = os.listdir(path)

    for project_name in entries:

        # Get the project root path.
        project_root = os.path.join(path, project_name)

        # Projects are always stored as sub directories of path.
        if not os.path.isdir(project_root):
            continue

        # Skip projects we've already found.
        if project_name in names:
            continue

        # Load the project.
        project = Project(project_name, path)
        project.load(include_disk=include_disk)
        # print(project)

        # We skip the display of the project if a project config does not exist and show_all is False.
        if not project.config_exists and not show_all:
            continue

        # Filter based on criteria, which should be a dict.
        if criteria:
            for field, search in criteria.items():

                # Handle the name and description attributes differently.
                if field in ("description", "name"):
                    value = getattr(project, field).lower()
                    search = search.lower()
                    if search in value:
                        projects.append(project)
                elif field == "tag":
                    tags = getattr(project, "tags")
                    if search in tags:
                        projects.append(project)
                else:
                    value = getattr(project, field)
                    if search == value:
                        projects.append(project)
        else:
            projects.append(project)

    return projects


# Classes


class Project(Config):

    def __init__(self, name, path=None):
        """Initialize a project object.

        :param name: The name of the project.
        :type name: str

        :param path: The path to the project.
        :type path: str

        """
        self.business = None
        self.category = None or "uncategorized"
        self.client = None
        self.config_exists = None
        self.description = None
        self.disk = "TBD"
        self.is_dirty = None
        self.is_loaded = False
        self.license = None
        self.name = name
        self.org = "Unknown"
        self.root = os.path.join(path or PROJECT_HOME, name)
        self.scm = None
        self.status = "unknown"
        self.tags = list()
        self.title = None
        self.type = "project"
        self._requirements = list()

        # Handle config file. We have to do this here in order to call super() below.
        config_path = os.path.join(self.root, "project.ini")
        if os.path.exists(config_path):
            self.config_exists = True
        else:
            self.config_exists = False

        super(Project, self).__init__(config_path)

    def __str__(self):
        return self.title or self.name or "Untitled Project"

    @property
    def exists(self):
        """Indicates whether the project root exists.

        :rtype: bool

        .. note::
            We've made this a dynamic property because it is possible for the root to be created after the project
            instance has been created.

        """
        return os.path.exists(self.root)

    def get_business(self):
        """Get the project business instance.

        :rtype: Business

        .. note::
            This method exists because we don't always know if ``business`` has been populated. This allows us to return
            a default even if the client has not been defined.

        """
        if self.has_business:
            return self.business

        return Business(DEVELOPER_NAME, code=DEVELOPER_CODE)

    def get_client(self):
        """Get the project client instance.

        :rtype: Client

        .. note::
            This method exists because we don't always know if ``client`` has been populated. This allows us to return a
            default even if the client has not been defined.

        """
        if self.has_client:
            return self.client

        return Client("Unidentified", code="UNK")

    def get_context(self):
        """Get project data as a dictionary.

        :rtype: dict

        """
        d = {
            'config_exists': self.config_exists,
            'description': self.description,
            'disk': self.disk,
            'name': self.name,
            'org': self.org,
            'root': self.root,
            'scm': self.scm,
            'status': self.status,
            'title': self.title,
            'type': self.type,
            'version': self.version,
        }

        for section_name in self._sections:
            d[section_name] = getattr(self, section_name)

        return d

    def get_requirements(self, env=None, manager=None):
        """Get project requirements (dependencies).

        :param env: Filter by environment.
        :type env: str

        :param manager: Filter by package manager.
        :type manager: str

        :rtype: list

        """
        locations = (
            os.path.join("deploy", "requirements", "packages.ini"),
            os.path.join("requirements/packages.ini"),
            os.path.join("requirements.ini"),
        )

        for i in locations:
            if self.path_exists(i):
                path = os.path.join(self.root, i)

                config = PackageConfig(path)
                if config.load():
                    return config.get_packages(env=env, manager=manager)

        return list()

    @property
    def has_business(self):
        """Indicates whether the project has a business (developer).

        :rtype: bool

        """
        return self.business is not None

    @property
    def has_client(self):
        """Indicates whether the project has a client.

        :rtype: bool

        """
        return self.client is not None

    @property
    def has_scm(self):
        return self._get_scm() is not None

    def initialize(self, display=True):
        """Initialize the project, creating various meta files as needed.

        :param display: Display output or not.
        :type display: bool

        This method does the following:

        - Creates the project root if it does not exist.
        - Writes ``DESCRIPTION.txt`` if one does not exist and ``description`` is set.
        - Writes a starter ``.gitignore`` file if one does not exist.
        - Writes a default (and very bare) ``README.markdown`` file if one does not exist.
        - Creates an empty ``requirements.pip`` file if one does not exist.
        - Creates a ``LICENSE.txt`` file if one does not exist and ``license`` is set.
        - Writes a starter ``project.ini`` file if one does not exist.

        .. note::
            It is safe to run this method multiple times.

        .. versionadded:: 0.16.0-d

        """
        if not os.path.exists(self.root):
            if display:
                print_info("Creating project directory: %s" % self.root)

            os.makedirs(self.root)

        description_path = os.path.join(self.root, "DESCRIPTION.txt")
        if self.description and not os.path.exists(description_path):
            if display:
                print_info("Writing DESCRIPTION.txt file: %s" % description_path)

            write_file(description_path, self.description)

        gitignore_path = os.path.join(self.root, ".gitignore")
        if not os.path.exists(gitignore_path):
            if display:
                print_info("Creating .gitignore file: %s" % gitignore_path)

            write_file(gitignore_path, GITIGNORE_TEMPLATE)

        license_path = os.path.join(self.root, "LICENSE.txt")
        if self.license and not os.path.exists(license_path):
            print_info("Creating %s license file: %s" % (self.license, license_path))

            if self.has_client:
                org = self.client.name
            elif self.has_business:
                org = self.business.name
            else:
                org = DEVELOPER_NAME

            cmd = 'lice --org="%s" --proj="%s" %s > %s' % (org, self.title, self.license, license_path)
            # print(cmd)
            commands.getstatusoutput(cmd)

        ini_path = os.path.join(self.root, "project.ini")
        if not os.path.exists(ini_path):
            print_info("Creating default project.ini file: %s" % ini_path)

            business = self.get_business()
            client = self.get_client()

            context = {
                'business_code': business.code,
                'business_name': business.name,
                'category': self.category,
                'client_code': client.code,
                'client_name': client.name,
                'description': self.description or "",
                'status': self.status or "development",
                'title': self.title or self.name,
                'type': self.type,
            }
            # print context

            content = parse_template(context, PROJECT_INI_TEMPLATE)
            write_file(ini_path, content)

        readme_path = os.path.join(self.root, "README.markdown")
        if not os.path.exists(readme_path):
            print_info("Writing default README.markdown file: %s" % readme_path)
            context = {
                'description': self.description or "",
                'title': self.title or self.name,
            }
            content = parse_template(context, README_TEMPLATE)
            write_file(readme_path, content)

        requirements_path = os.path.join(self.root, "requirements.pip")
        if not os.path.exists(requirements_path):
            print_info("Creating empty requirements file.")
            commands.getstatusoutput("touch %s" % requirements_path)

        version_path = os.path.join(self.root, "VERSION.txt")
        if not os.path.exists(version_path):
            print_info("Writing initial version file: %s" % version_path)
            write_file(version_path, self.version)

        return True

    def load(self, include_disk=False):
        """Load the project.

        :param include_disk: Whether to calculate disk usage.
        :type include_disk: bool

        :rtype: bool
        :returns: Returns ``True`` if the project was found and loaded successful. This also sets ``is_loaded`` to
                  ``True``.

        """
        # We can't do anything if the project root doesn't exist.
        if not self.exists:
            self.is_loaded = False
            self._error = "Project root does not exist: %s" % self.root
            return False

        # Let the underlying Config do it's thing.
        super(Project, self).load()

        # Make sure we always have title.
        if not self.title:
            self.title = self.name

        # Get meta data.
        self.org = self._get_org()
        self.scm = self._get_scm()
        self._load_version()

        # Calculate disk space.
        if include_disk:
            self.disk = self._get_disk()

        return self.is_loaded

    def path_exists(self, *args):
        """Determine if a given file or directory exists relative to the project's root."""
        path = os.path.join(self.root, *args)
        return os.path.exists(path)

    def to_markdown(self):
        """Output the project as Markdown.

        :rtype: str

        """
        # TODO: Create a TEMPLATE for markdown export and make this configurable from a switch.

        # Build the top/main section of the output.
        a = list()
        a.append("# %s" % self.title)
        a.append("")

        a.append("**Version**: %s  " % self.version)
        a.append("**Status**: %s  " % self.status)
        a.append("**Category**: %s  " % self.category)
        a.append("**Type**: %s  " % self.type)
        a.append("**Disk Usage**: %s  " % self._get_disk())
        a.append("**Source Code Management**: %s  " % self._get_scm())

        if self.tags:
            a.append("**Tags**: %s" % ",".join(self.tags))

        a.append("")

        # Add the description.
        if self.description:
            a.append(self.description)
            a.append("")

        # Add each section to the output.
        context = self.get_context()
        for key, value in context.items():
            if isinstance(value, Section):
                a.append(value.to_markdown())
            else:
                pass

        # List the dependencies.
        a.append("## Requirements")
        a.append("")
        for env in ENVIRONMENTS:
            a.append("### %s" % env)
            a.append("")

            packages = self.get_requirements(env=env)
            if len(packages) == 0:
                continue

            for p in packages:
                a.append(p.to_markdown())

        # Include the project tree.
        a.append("## Tree")
        a.append("")
        status, output = commands.getstatusoutput("cd %s && tree" % self.root)
        for line in output.split("\n"):
            a.append("    %s" % line)

        a.append("")

        return "\n".join(a)

    def _get_disk(self):
        cmd = "du -hs %s | awk -F ' ' '{print $1}'" % self.root
        (status, output) = commands.getstatusoutput(cmd)
        return output.strip()

    def _get_org(self):
        """Get the organization identifier.

        :rtype: str

        .. note::
            The client is checked first, then the business. The ``code`` attribute is returned.

        """
        if self.has_client:
            return self.client.code
        elif self.has_business:
            return self.business.code
        else:
            return "???"

    def _get_path(self, name):
        return os.path.join(self.root, name)

    def _get_scm(self):
        """Determine the SCM in use and get the current state.

        :rtype: str | None
        :returns: Returns the type of SCM in use or ``None`` if no SCM is recognized.

        """
        if self.path_exists(".git"):
            # See http://stackoverflow.com/a/5737794/241720
            cmd = '(cd %s && test -z "$(git status --porcelain)")' % self.root
            (status, output) = commands.getstatusoutput(cmd)
            if status >= 1:
                self.is_dirty = True
            else:
                self.is_dirty = False

            return "git"
        elif self.path_exists(".hg"):
            # See http://stackoverflow.com/a/11012582/241720
            cmd = '(cd %s && hg identify --id | grep --quiet + ; echo $?)' % self.root
            (status, output) = commands.getstatusoutput(cmd)
            if status >= 1:
                self.is_dirty = True
            else:
                self.is_dirty = False

            return "hg"
        elif self.path_exists(".svn"):
            cmd = 'test -z "`(cd %s && svn status)`"' % self.root
            (status, output) = commands.getstatusoutput(cmd)
            if status >= 1:
                self.is_dirty = True
            else:
                self.is_dirty = False

            return "svn"
        else:
            return None

    def _load_section(self, name, values):
        """Overridden to add business, client, and project section values to the current instance."""
        if name == "buiness":
            section = Business(values.pop('name'), **values)
            setattr(self, name, section)
        elif name == "client":
            section = Client(values.pop('name'), **values)
            setattr(self, name, section)
        elif name == "project":
            for key in values.keys():
                setattr(self, key, values[key])
        else:
            super(Project, self)._load_section(name, values)

    def _load_version(self):
        """Get project version info.

        :rtype: str
        :returns: Returns the version string.

        .. note::
            This method sets the ``version``, ``version_py``, and ``version_txt`` attributes.

        """
        # Always set version_txt whether it exists or not. This allows it to be created if it does not already exist.
        self.version_txt = os.path.join(self.root, "VERSION.txt")
        if os.path.exists(self.version_txt):
            self.version = read_file(self.version_txt)
        else:
            self.version = "0.1.0-d"

        # Set the path to the version.py file.
        self.version_py = None
        locations = (
            os.path.join(self.root, "version.py"),
            os.path.join(self.root, self.name, "version.py"),
            os.path.join(self.root, "source", "main", "version.py"),
        )
        for i in locations:
            if os.path.exists(i):
                self.version_py = i
                break
