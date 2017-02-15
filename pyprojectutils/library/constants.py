import os

__all__ = (
    "AUTHOR",
    "BASE_ENVIRONMENT",
    "BITBUCKET_ENABLED",
    "BITBUCKET_SCM",
    "BITBUCKET_USER",
    "BUSINESS",
    "CLIENT",
    "CONTROL_ENVIRONMENT",
    "DEFAULT_SCM",
    "DEVELOPMENT",
    "DEVELOPER_CODE",
    "DEVELOPER_NAME",
    "DEVELOPMENT_ENVIRONMENT",
    "DOCUMENTATION_HOME",
    "ENVIRONMENTS",
    "EXIT_ENV",
    "EXIT_INPUT",
    "EXIT_OK",
    "EXIT_OTHER",
    "EXIT_USAGE",
    "EXPERIMENTAL",
    "GITHUB_ENABLED",
    "GITHUB_PASSWORD",
    "GITHUB_SCM",
    "GITHUB_USER",
    "LICENSE_CHOICES",
    "LIVE",
    "LIVE_ENVIRONMENT",
    "PROJECT_ARCHIVE",
    "PROJECT_HOME",
    "PROJECTS_ON_HOLD",
    "PUBLISHER",
    "REPO_META_PATH",
    "STAGING",
    "STAGING_ENVIRONMENT",
    "TESTING",
    "TESTING_ENVIRONMENT",
)

# The developer name is the name of an individual or company that creates and manages projects. The code is merely a
# short form of the name, such as an abbreviation. For example, we abbreviate Devel May Care as DMC.
DEVELOPER_CODE = os.environ.get("DEVELOPER_CODE", "UNK")
DEVELOPER_NAME = os.environ.get("DEVELOPER_NAME", "Unidentified")

# Organization types help identify who is involved in a project.
BUSINESS = "business"
CLIENT = "client"

# Documentation may have an author and publisher.
AUTHOR = "author"
PUBLISHER = "publisher"

# Documentation is stored in a specific location.
DOCUMENTATION_HOME = os.environ.get("DOCUMENTATION_HOME", os.path.expanduser("~/Dropbox/Business/Documentation"))

# Standard stage identifiers.
EXPERIMENTAL = "experimental"
PLANNING = "planning"
DEVELOPMENT = "development"
TESTING = "testing"
STAGING = "staging"
RELEASE = "release"
LIVE = "live"

# Standard environments.
BASE_ENVIRONMENT = "base"
CONTROL_ENVIRONMENT = "control"
DEVELOPMENT_ENVIRONMENT = "development"
TESTING_ENVIRONMENT = "testing"
STAGING_ENVIRONMENT = "staging"
LIVE_ENVIRONMENT = "live"

ENVIRONMENTS = (
    BASE_ENVIRONMENT,
    CONTROL_ENVIRONMENT,
    DEVELOPMENT_ENVIRONMENT,
    TESTING_ENVIRONMENT,
    STAGING_ENVIRONMENT,
    LIVE_ENVIRONMENT,
)

# Exit codes.
EXIT_OK = 0
EXIT_USAGE = 1
EXIT_INPUT = 2
EXIT_ENV = 3
EXIT_OTHER = 4

# Location of projects. User home is automatically expanded.
PROJECT_HOME = os.environ.get("PROJECT_HOME", os.path.expanduser("~/Work"))

# Location of archived projects.
PROJECT_ARCHIVE = os.environ.get("PROJECT_ARCHIVE", os.path.join(PROJECT_HOME, ".archive"))

# Location of projects on hold.
PROJECTS_ON_HOLD = os.environ.get("PROJECTS_ON_HOLD", os.path.join(PROJECT_HOME, ".hold"))

# Support for source code repo meta data.
BITBUCKET_SCM = "bitbucket.org"
GITHUB_SCM = "github.com"
REPO_META_PATH = os.environ.get("REPO_META_PATH", os.path.join(PROJECT_HOME, ".repos"))

# License options for the lice command.
LICENSE_CHOICES = (
    "afl3",
    "agpl3",
    "apache",
    "bsd2",
    "bsd3",
    "cc0",
    "cc_by",
    "cc_by_nc",
    "cc_by_nc_nd",
    "cc_by_nc_sa",
    "cc_by_nd",
    "cc_by_sa",
    "cddl",
    "epl",
    "gpl2",
    "gpl3",
    "isc",
    "lgpl",
    "mit",
    "mpl",
    "wtfpl",
    "zlib",
)

# Bitbucket integration requires a user name and password.
BITBUCKET_USER = os.environ.get("BITBUCKET_USER", None)
BITBUCKET_PASSWORD = os.environ.get("BITBUCKET_PASSWORD", None)

if BITBUCKET_USER and BITBUCKET_USER:
    BITBUCKET_ENABLED = True
else:
    BITBUCKET_ENABLED = False

# GitHub integration is only possible if the user sets a user and password in the local environment.
GITHUB_USER = os.environ.get("GITHUB_USER", None)
GITHUB_PASSWORD = os.environ.get("GITHUB_PASSWORD", None)

if GITHUB_USER and GITHUB_PASSWORD:
    GITHUB_ENABLED = True
else:
    GITHUB_ENABLED = False

# The default SCM is the user's preferred provider (host) for repos.
DEFAULT_SCM = os.environ.get("DEFAULT_SCM", "github")
