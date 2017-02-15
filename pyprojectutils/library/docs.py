"""
.. versionadded:: 0.24.11-d

We use the excellent `Dash`_ app for documentation, but some documentation is nice to have on the local machine.
This may even be extended to cover training materials, e-books, etc.

.. _Dash: https://kapeli.com/dash

"""

# Imports

from collections import OrderedDict
import commands
import os
from .config import Config, Section
from .constants import AUTHOR, DOCUMENTATION_HOME, PUBLISHER
from .organizations import BaseOrganization

# Exports

__all__ = (
    "Author",
    "Entry",
    "Publisher",
)

# Classes


class Author(BaseOrganization):
    """An author creates and maintains a documentation entry."""

    def __init__(self, name, code=None, contact=None, email=None, phone=None, projects=None, url=None):
        self.code = code or self.get_default_code(name)
        self.contact = contact
        self.email = email
        self.name = name
        self.phone = phone
        self.projects = projects or list()
        self.url = url

        super(Author, self).__init__(name, code=code, contact=contact, projects=projects)

    def get_type(self):
        return AUTHOR

    def to_markdown(self):
        """Output publisher info as Markdown.

        :rtype: str

        """
        a = list()

        a.append("## Author")
        a.append("")

        if self.name:
            a.append("Name: %s" % self.name)
            a.append("")

        if self.email:
            a.append("Email: %s" % self.email)
            a.append("")

        if self.url:
            a.append("Web: [%s](%s)" % (self.url, self.url))
            a.append("")

        return "\n".join(a)

    def to_text(self):
        """Get info as plain text.

        :rtype: str

        """
        a = list()

        a.append("Author:")

        if self.name:
            a.append(self.name)

        if self.email:
            a.append("<%s>" % self.email)

        if self.url:
            a.append(self.url)

        return " ".join(a)


class Entry(Config):
    """An entry represents any work of documentation stored in a pre-determined location."""

    def __init__(self, name, path=None):
        """Initialize a documentation object.

        :param name: The name of the work. This is the name as it exists on disk. Case is handled automatically.
        :type name: str

        :param path: The path to where documentation is stored. Defaults to the ``DOCUMENTATION_HOME`` environment
                     variable.
        :type path: str

        """
        self.author = None
        self.category = None or "uncategorized"
        self.config_exists = None
        self.description = None
        self.disk = "TBD"
        self.is_loaded = False
        self.license = None
        self.name = name
        self.org = None
        self.publisher = None
        self.root = os.path.join(path or DOCUMENTATION_HOME, name)
        self.subtitle = None
        self.tags = list()
        self.title = None
        self.type = "documentation"

        # Handle config file. We have to do this here in order to call super() below.
        config_path = os.path.join(self.root, "info.ini")
        if os.path.exists(config_path):
            self.config_exists = True
        else:
            self.config_exists = False

        super(Entry, self).__init__(config_path)

    def __str__(self):
        return self.title or self.name or "Untitled Documentation"

    @property
    def exists(self):
        """Indicates whether the entry root exists.

        :rtype: bool

        .. note::
            We've made this a dynamic property because it is possible for the root to be created after the entry
            instance has been created.

        """
        return os.path.exists(self.root)

    @staticmethod
    def fetch(criteria=None, include_disk=False, path=DOCUMENTATION_HOME, show_all=False):
        """Get a list of documentation.

        :param criteria: Criteria used to filter the list, if any.
        :type criteria: dict

        :param include_disk: Whether to calculate disk usage.
        :type include_disk: bool

        :param path: Path to where documentation entries are stored.
        :type path: str

        :param show_all: By default, documentation without a ``info.ini`` file are omitted. Set this to ``True`` to show
                         all entries.

        :type show_all: bool

        :rtype: list

        """
        entries = os.listdir(path)
        names = list()
        results = list()
        for entry_name in entries:

            # Get the entry root path.
            entry_root = os.path.join(path, entry_name)

            # Projects are always stored as sub directories of path.
            if not os.path.isdir(entry_root):
                continue

            # Skip entries we've already found.
            if entry_name in names:
                continue

            # Load the entry.
            entry = Entry(entry_name, path=path)
            entry.load(include_disk=include_disk)
            # print(entry)

            # We skip the display of the entry if a entry config does not exist and show_all is False.
            if not entry.config_exists and not show_all:
                continue

            # Filter based on criteria, which should be a dict.
            if criteria:
                for field, search in criteria.items():

                    # Handle the name and description attributes differently.
                    if field in ("description", "name", "title"):
                        value = getattr(entry, field).lower()
                        search = search.lower()
                        if search in value:
                            results.append(entry)
                    elif field == "tag":
                        tags = getattr(entry, "tags")
                        if search in tags:
                            results.append(entry)
                    else:
                        value = getattr(entry, field)
                        if search == value:
                            results.append(entry)
            else:
                results.append(entry)

        return results

    @staticmethod
    def find(name, include_disk=False, path=DOCUMENTATION_HOME):
        """Find an entry by name or title.

        :param name: Name or title of the entry.

        :param include_disk: Whether to calculate disk usage.
        :type include_disk: bool

        :param path: The path to where documentation entries are stored.
        :type path: str

        :rtype: Entry

        """
        names = (
            name,
            name.replace(".", "-"),
            name.replace(" ", "-"),
        )
        for name in names:
            root_path = os.path.join(path, name)
            if os.path.exists(root_path):
                entry = Entry(name, path=path)
                entry.load(include_disk=include_disk)
                return entry

        return Entry(name, path=path)

    def get_context(self):
        """Get entry data as a dictionary.

        :rtype: dict

        """
        d = {
            'config_exists': self.config_exists,
            'description': self.description,
            'disk': self.disk,
            'name': self.name,
            'org': self.org,
            'root': self.root,
            'subtitle': self.subtitle,
            'title': self.title,
            'type': self.type,
        }

        for section_name in self._sections:
            d[section_name] = getattr(self, section_name)

        return d

    @staticmethod
    def get_distinct_attribute_values(attribute, path=DOCUMENTATION_HOME):
        """Get distinct values of the named attribute.

        :param attribute: The name of the attribute.
        :type attribute: str

        :param path: The path to where documentation entries are stored.
        :type path: str

        :rtype: OrderedDict
        :returns: Returns a dictionary where each distinct values is a dictionary key and the total documentation count
                  is the dictionary value. Keys are sorted alphabetically.

        .. note::
            If the given ``attribute`` does not exist on the :py:class:`Entry`, the resulting ``AttributeError`` is
            trapped and ``{'Invalid Documentation Attribute': attribute}`` is returned.

        """
        d = dict()
        entries = Entry.fetch(path=path)
        for e in entries:
            try:
                value = getattr(e, attribute)
            except AttributeError:
                return {'Invalid Documentation Attribute': attribute}

            if value in d.keys():
                d[value] += 1
            else:
                d[value] = 1

        return OrderedDict(sorted(d.items(), key=lambda t: t[0]))

    @property
    def has_author(self):
        """Indicates whether the entry has author info.

        :rtype: bool

        """
        return self.author is not None

    @property
    def has_publisher(self):
        """Indicates whether the entry has publiser info.

        :rtype: bool

        """
        return self.publisher is not None

    def load(self, include_disk=False):
        """Load documentation info.

        :param include_disk: Whether to calculate disk usage.
        :type include_disk: bool

        :rtype: bool
        :returns: Returns ``True`` if the documentation was found and loaded successful. This also sets ``is_loaded`` to
                  ``True``.

        """
        # We can't do anything if the root doesn't exist.
        if not self.exists:
            self.is_loaded = False
            self._error = "Documentation root does not exist: %s" % self.root
            return False

        # Let the underlying Config do it's thing.
        super(Entry, self).load()

        # Make sure we always have title.
        if not self.title:
            self.title = self.name

        # Get meta data.
        self.org = self._get_org()

        if include_disk:
            self.disk = self._get_disk()

        # Return the load status.
        return self.is_loaded

    def to_markdown(self):
        """Export the documentation info as Markdown.

        :rtype: str

        """
        # TODO: Create a TEMPLATE for documentation entry markdown export and make this configurable from a switch.

        # Build the top/main section of the output.
        a = list()
        a.append("# %s" % self.title)
        a.append("")

        if self.subtitle:
            a.append("**%s**" % self.subtitle)
            a.append("")

        a.append("**Category**: %s  " % self.category)
        a.append("**Type**: %s  " % self.type)
        a.append("**Disk Usage**: %s  " % self.disk)

        if self.tags:
            a.append("**Tags**: %s" % ", ".join(self.tags))

        a.append("")

        # Add the description.
        if self.description:
            a.append(self.description)
            a.append("")

        # Add the author.
        if self.has_author:
            a.append(self.author.to_markdown())
            a.append("")

        # Add the publisher.
        if self.has_publisher:
            a.append(self.publisher.to_markdown())
            a.append("")

        # Add each section to the output.
        context = self.get_context()
        for key, value in context.items():
            if isinstance(value, Section):
                a.append(value.to_markdown())
            else:
                pass

        # Include the manifest.
        a.append("## Manifest")
        a.append("")
        a.append("The files below are included in the package:")
        a.append("")
        status, output = commands.getstatusoutput("cd %s && tree" % self.root)
        for line in output.split("\n"):
            a.append("    %s" % line)

        a.append("")

        return "\n".join(a)

    def to_text(self):
        """Export the documentation info as plain text.

        :rtype: str

        """
        a = list()
        a.append(self.title)

        if self.subtitle:
            a.append(self.subtitle)

        a.append("")

        a.append("Category: %s" % self.category)
        a.append("Type: %s" % self.type)
        a.append("Disk Usage: %s" % self.disk)

        if self.tags:
            a.append("Tags: %s" % ", ".join(self.tags))

        # Add the author.
        if self.has_author:
            a.append(self.author.to_text())

        # Add the publisher.
        if self.has_publisher:
            a.append(self.publisher.to_text())

        # Add each section to the output.
        context = self.get_context()
        for key, value in context.items():
            if isinstance(value, Section):
                a.append(value.to_text())
            else:
                pass

        # Add the description.
        if self.description:
            a.append(self.description)
            a.append("")

        # Include the manifest.
        status, output = commands.getstatusoutput("cd %s && tree" % self.root)
        a.append("")
        a.append(output)
        a.append("")

        # Return the output.
        return "\n".join(a)

    def _get_disk(self):
        cmd = "du -hs %s | awk -F ' ' '{print $1}'" % self.root
        (status, output) = commands.getstatusoutput(cmd)
        return output.strip()

    def _get_org(self):
        """Get the organization identifier.

        :rtype: str

        .. note::
            The author is checked first, then the publisher. The ``name`` attribute is returned.

        """
        if self.has_author:
            return self.author.name
        elif self.has_publisher:
            return self.publisher.name
        else:
            return "???"

    def _load_section(self, name, values):
        """Overridden to add author and publisher section values to the current instance."""

        if name == "author":
            section = Author(values.pop('name'), **values)
            setattr(self, name, section)
        elif name == "publisher":
            section = Publisher(values.pop('name'), **values)
            setattr(self, name, section)
        elif name == "entry":
            for key in values.keys():
                setattr(self, key, values[key])
        else:
            super(Entry, self)._load_section(name, values)


class Publisher(BaseOrganization):
    """A publisher produces a documentation entry."""

    def __init__(self, name, code=None, contact=None, email=None, phone=None, projects=None, url=None):
        self.code = code or self.get_default_code(name)
        self.contact = contact
        self.email = email
        self.name = name
        self.phone = phone
        self.projects = projects or list()
        self.url = url

        super(Publisher, self).__init__(name, code=code, contact=contact, projects=projects)

    def get_type(self):
        return PUBLISHER

    def to_markdown(self):
        """Output publisher info as Markdown.

        :rtype: str

        """
        a = list()

        a.append("## Publisher")
        a.append("")

        if self.name:
            a.append("Name: %s" % self.name)
            a.append("")

        if self.email:
            a.append("Email: %s" % self.email)
            a.append("")

        if self.url:
            a.append("Web: [%s](%s)" % (self.url, self.url))
            a.append("")

        return "\n".join(a)

    def to_text(self):
        """Get info as plain text.

        :rtype: str

        """
        a = list()

        a.append("Publisher:")

        if self.name:
            a.append(self.name)

        if self.email:
            a.append("<%s>" % self.email)

        if self.url:
            a.append(self.url)

        return " ".join(a)
