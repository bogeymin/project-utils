# Imports

from ConfigParser import ParsingError, RawConfigParser
from os.path import exists as path_exists
from .shortcuts import write_file

# Classes


class Config(object):
    """Generic representation of an INI file."""

    def __init__(self, path):
        self.is_loaded = None
        self.path = path
        self._error = None
        self._sections = list()

    def get_error(self):
        """Get any error that has occurred during ``load()`` or other processing.

        :rtype: str

        """
        return self._error

    def get_section(self, name):
        """Get the named section.

        :param name: Section name.
        :type name: str

        :rtype: Section
        :raises: AttributeError

        """
        return getattr(self, name)

    @property
    def has_error(self):
        """Indicates whether an error has occurred during ``load()`` or other processing.

        :rtype: bool

        """
        return self._error is not None

    def load(self):
        """Attempt to load configuration from the current given path.

        :rtype: bool
        :returns: Returns ``True`` if the path could be loaded. Also sets ``is_loaded``.

        """
        if not path_exists(self.path):
            self.is_loaded = False
            self._error = "Configuration file does not exist: %s" % self.path
            return False

        # Load the config without interpolation.
        ini = RawConfigParser()

        try:
            ini.read(self.path)
        except ParsingError, e:
            self.is_loaded = False
            self._error = e
            return False

        # Iterate through the sections.
        for section_name in ini.sections():

            # Values will be passed as kwargs to the Section instance.
            kwargs = {}

            # Tags are handled specifically for all configurations.
            for key, value in ini.items(section_name):
                if key == "tags":
                    kwargs['tags'] = value.split(",")
                else:
                    kwargs[key] = value

            # Load the section. This allows section initialization to be customized in child classes.
            self._load_section(section_name, kwargs)

        self.is_loaded = True
        return True

    def to_string(self):
        """Get the config as a string.

        :rtype: str

        """
        a = list()
        for name in self._sections:
            section = self.get_section(name)
            a.append(section.to_string())

        return "\n".join(a)

    def write(self):
        """Write the current configuration to disk."""
        write_file(self.path, self.to_string())

    def _load_section(self, name, values):
        """Instantiate a new section.

        :param name: Name of the section.
        :type name: str

        :param values: The values associated with the section.
        :type values: dict

        :rtype: Section
        :returns: Returns the newly created section instance.

        """
        section = Section(name, **values)
        setattr(self, name, section)
        self._sections.append(name)
        return section


class Section(object):
    """Generic representation of a section in an INI file.

    .. note::
        This class is typically only used internally.

    """

    def __init__(self, key, **kwargs):
        self._context = kwargs
        self._name = key

    def __getattr__(self, item):
        return self._context[item]

    def get_context(self):
        """Return the section as a dictionary.

        :rtype: dict

        """
        return self._context.copy()

    def to_markdown(self):
        """Convert the section to Markdown.

        :rtype: str

        """
        a = list()
        a.append("## %s" % self._name.title())
        a.append("")

        context = self.get_context()

        if "description" in context:
            a.append(context.pop("description"))
            a.append("")

        for key, value in context.items():
            if key == "tags":
                a.append("*tags*: %s  " % ",".join(value))
            else:
                a.append("*%s*: %s  " % (key, value))

        a.append("")

        return "\n".join(a)

    def to_text(self):
        """Convert the section to plain text.

        :rtype str

        """
        a = list()

        a.append(self._name.title() + ":")

        context = self.get_context()
        for key, value in context.items():
            if key == "tags":
                a.append("Tags: %s" % ",".join(value))
            else:
                a.append("%s (%s)" % (key, value))

        if "description" in context:
            a.append(context.pop("description"))
            a.append("\n")

        return " ".join(a)

    def to_string(self):
        """Convert the section to a string.


        :rtype: str

        """
        a = list()
        a.append("[%s]" % self._name)
        for key, value, in self._context.items():
            a.append("%s = %s" % (key, value))

        a.append("")

        return "\n".join(a)
