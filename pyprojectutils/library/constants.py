import os

__all__ = (
    "BASE_ENVIRONMENT",
    "CONTROL_ENVIRONMENT",
    "DEVELOPMENT",
    "DEVELOPMENT_ENVIRONMENT",
    "ENVIRONMENTS",
    "EXIT_ENV",
    "EXIT_INPUT",
    "EXIT_OK",
    "EXIT_OTHER",
    "EXIT_USAGE",
    "EXPERIMENTAL",
    "LICENSE_CHOICES",
    "PROJECT_HOME",
    "PROJECTS_ON_HOLD",
    "TESTING",
    "TESTING_ENVIRONMENT",
    "STAGING",
    "STAGING_ENVIRONMENT",
    "LIVE",
    "LIVE_ENVIRONMENT",
)

# The developer name is the name of an individual or company that creates and manages projects. The code is merely a
# short form of the name, such as an abbreviation. For example, we abbreviate Devel May Care as DMC.
DEVELOPER_CODE = os.environ.get("DEVELOPER_CODE", "UNK")
DEVELOPER_NAME = os.environ.get("DEVELOPER_NAME", "Unidentified")

# Organization types help identify who is involved in a project.
BUSINESS = "business"
CLIENT = "client"


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
PROJECT_HOME = os.environ.get("PROJECT_HOME", "~/Work")

# Location of projects on hold.
PROJECTS_ON_HOLD = os.environ.get("PROJECTS_ON_HOLD", os.path.join(PROJECT_HOME, ".hold"))

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
