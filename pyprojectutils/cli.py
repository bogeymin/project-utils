# Imports

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
import sys
from datetime_machine import DateTime
from library.constants import BASE_ENVIRONMENT, DEVELOPMENT, ENVIRONMENTS, EXIT_OK, EXIT_INPUT, EXIT_OTHER, EXIT_USAGE,\
    GITHUB_ENABLED, GITHUB_PASSWORD, GITHUB_USER, LICENSE_CHOICES, PROJECT_HOME
from library.exceptions import OutputError
from library.projects import autoload_project, get_distinct_project_attributes, get_projects, Project
from library.organizations import BaseOrganization, Business, Client
from library.passwords import RandomPassword
from library.releases import Version
from library.shortcuts import get_input, parse_template, write_file, print_error, print_warning

# Commands


def export_github_command():
    """Export Github milestones and issues."""

    # Define meta data.
    __author__ = "Shawn Davis <shawn@develmaycare.com>"
    __date__ = "2016-12-19"
    __help__ = """
We look for labels of ready, in progress, and review to determine the issue's current position in the workflow.
        """
    __version__ = "0.1.1-d"

    # Define options and arguments.
    parser = ArgumentParser(description=__doc__, epilog=__help__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument(
        "repo_name",
        help="Name of the repository."
    )

    parser.add_argument(
        "-L=",
        "--label=",
        default="enhancement",
        dest="label",
        help='The label used to identify road map items. Defaults to "enhancement".'
    )

    # Access to the version number requires special consideration, especially
    # when using sub parsers. The Python 3.3 behavior is different. See this
    # answer: http://stackoverflow.com/questions/8521612/argparse-optional-subparser-for-version
    # parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    parser.add_argument(
        "-v",
        action="version",
        help="Show version number and exit.",
        version=__version__
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Show verbose version information and exit.",
        version="%(prog)s" + " %s %s by %s" % (__version__, __date__, __author__)
    )

    # There's no need to go on if the user name and password have not been defined.
    if not GITHUB_ENABLED:
        print_warning("GITHUB_USER and GITHUB_PASSWORD environment variables are required.")
        sys.exit()

    # We also can't continue if PyGithub is not installed.
    try:
        from github import Github
    except ImportError:
        print_error("The PyGithub package is required to use this command: pip install pygithub")

    # This will display help or input errors as needed.
    args = parser.parse_args()
    # print args

    # Initialize the connection to github.
    gh = Github(GITHUB_USER, GITHUB_PASSWORD)

    # Seems like loading the user is required to get at the other data.
    user = gh.get_user()

    # Get the repo instance.
    repo = user.get_repo(args.repo_name)

    # Get the issues in the repo. Assemble the output.
    count = 0
    issues = list()
    issues.append("Item,Description,Start Date,End Date,Bucket,Status,Feature Set,Labels,Assignee")
    for i in repo.get_issues():

        # We are only interested in issues that pertain to features.
        labels = list()
        for label in i.labels:

            if "bucket" in label.name:
                continue

            labels.append(label.name)

        if args.label not in labels:
            continue

        count += 1

        # Determine the current workflow of the issue.
        if "ready" in labels:
            status = "Next Up"
        elif "in progress" in labels:
            status = "In Progress"
        elif "review" in labels:
            status = "Review"
        else:
            status = "Planning"

        # Get the milestone.
        milestone = i.milestone
        if milestone:
            feature_set = milestone.title
        else:
            feature_set = ""

        # Get the end date and calculate the start date.
        if milestone and milestone.due_on:

            # We start with the due date of the milestone as a point of reference.
            end = DateTime(milestone.due_on)

            # The start date is calculated in reverse from the end date based 1 day per issue.
            days_ago = -(count * 24)
            start = DateTime(milestone.due_on)
            start.increment(business_days=days_ago)

            # Set the end and start datetimes.
            end_date = end.dt
            start_date = start.dt

        else:
            end_date = ""
            start_date = ""

        # Set the bucket if start and end date are not available.
        bucket = ""
        if not start_date and not end_date:
            for label in labels:
                if "bucket" in label:
                    bucket = label.split(":")[-1].strip()
                    break

        # Condense assignees into a series of strings.
        try:
            assignee = i.assignee.name
        except AttributeError:
            assignee = ""

        # Abbreviate the description since we don't need every last word for the road map.
        description = i.body.split(".")[0]
        description += ". Read more: %s" % i.html_url

        # item, desc, start, end, bucket, status, feature set, labels, assignee
        tokens = [
            i.title,
            description,
            start_date,
            end_date,
            bucket,
            status,
            feature_set,
            ",".join(labels),
            assignee,
        ]

        # Convert the line into CSV. We can't use join because we need to wrap the tokens in quotes.
        line = ""
        for t in tokens:
            line += '"%s",' % t

        line = line[:-1]

        # Add the line to the issues list.
        issues.append(line)

    print("\n".join(issues))

    # item (title)
    # desc (body)
    # start (?)
    # end (due_on)
    # bucket
    # assignees
    # feature set (milestone.title)
    #
    # Milestone
    # title
    # description
    # due_on

    # full_name = develmaycare/repo_name
    # name = repo_name
    # repos = user.get_repos()
    # for r in repos:
    #     print r.name, r.has_wiki

    # repo = user.get_repo("pyprojectutils")
    #
    # milestones = repo.get_milestones(state="open")
    # for m in milestones:
    #     print m.title, m.due_on
    #     print m.description
    #     print ""

    # print repo.name
    # print repo.description
    # feature = repo.get_label("feature")
    # issues = repo.get_issues(state="open", labels=[feature])
    # for issue in issues:
    #     print issue.title

    # Roadmunk
    # item (title), desc, start, end, bucket
    # release, objective/category/theme/area, status, completion, owner/assignees

    # Github Issue
    # title, state, body, labels, comments

    # Exit.
    sys.exit(EXIT_OK)


def generate_password():
    """Generate a random password."""

    __author__ = "Shawn Davis <shawn@develmaycare.com>"
    __date__ = "2016-12-11"
    __help__ = """
We often need to generate passwords automatically. This utility does just
that. Install pyprojectutils during deployment to create passwords on the fly.
    """
    __version__ = "0.10.2-d"

    # Define options and arguments.
    parser = ArgumentParser(description=__doc__, epilog=__help__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument(
        "--format=",
        choices=["crypt", "md5", "plain", "htpasswd"],
        default="plain",
        dest="format",
        help="Choose the format of the output.",
        nargs="?"
    )
    parser.add_argument("--strong", action="store_true", help="Make the password stronger.")
    parser.add_argument(
        "-U",
        action="store_true",
        dest="use_unambiguous",
        help="Avoid ambiguous characters."
    )

    # Access to the version number requires special consideration, especially
    # when using sub parsers. The Python 3.3 behavior is different. See this
    # answer: http://stackoverflow.com/questions/8521612/argparse-optional-subparser-for-version
    # parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    parser.add_argument(
        "-v",
        action="version",
        help="Show version number and exit.",
        version=__version__
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Show verbose version information and exit.",
        version="%(prog)s" + " %s %s by %s" % (__version__, __date__, __author__)
    )

    # This will display help or input errors as needed.
    args = parser.parse_args()
    # print args

    password_length = 10
    if args.strong:
        password_length = 20

    password = RandomPassword(password_length, use_unambiguous=args.use_unambiguous)

    if args.format == "crypt":
        print(password.to_crypt())
    elif args.format == "htpasswd":
        print(password.to_htpasswd())
    elif args.format == "md5":
        print(password.to_md5())
    else:
        print(password.plain_text)

    # Quit.
    sys.exit(EXIT_OK)


def package_parser():
    """List the packages for a given project."""

    __author__ = "Shawn Davis <shawn@develmaycare.com>"
    __date__ = "2016-12-11"
    __help__ = """

    """
    __version__ = "0.5.2-d"

    # Define options and arguments.
    parser = ArgumentParser(description=__doc__, epilog=__help__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument(
        "project_name",
        help="The name of the project."
    )

    parser.add_argument(
        "--env=",
        choices=ENVIRONMENTS,
        dest="env",
        help="Filter by environment."
    )

    parser.add_argument(
        "--format=",
        choices=("ansible", "command", "markdown", "plain", "rst", "table"),
        default="table",
        dest="output_format",
        help="Output format."
    )

    parser.add_argument(
        "--manager=",
        choices=("apt", "brew", "gem", "npm", "pip"),
        dest="manager",
        help="Filter by package manager."
    )

    parser.add_argument(
        "-O=",
        "--output=",
        dest="output_file",
        help="Path to the output file, if any."
    )

    parser.add_argument(
        "-p=",
        "--path=",
        default=PROJECT_HOME,
        dest="project_home",
        help="Path to where projects are stored. Defaults to %s" % PROJECT_HOME
    )

    # Access to the version number requires special consideration, especially
    # when using sub parsers. The Python 3.3 behavior is different. See this
    # answer: http://stackoverflow.com/questions/8521612/argparse-optional-subparser-for-version
    # parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    parser.add_argument(
        "-v",
        action="version",
        help="Show version number and exit.",
        version=__version__
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Show verbose version information and exit.",
        version="%(prog)s" + " %s %s by %s" % (__version__, __date__, __author__)
    )

    # Parse arguments.
    args = parser.parse_args()

    # Load the project.
    project = autoload_project(args.project_name, args.project_home)
    if not project:
        print("Project not found: %s" % args.project_name)
        sys.exit(EXIT_OTHER)

    # Generate the output.
    output = list()
    if args.output_format == "ansible":
        if not args.manager:
            print("--manager is required for Ansible output.")
            sys.exit(EXIT_USAGE)

        output.append("- name: install %s requirements" % args.manager)
        output.append("  %s: name={{ item }} state=installed" % args.manager)

        a = list()
        for p in project.get_requirements(env=args.env, manager=args.manager):
            a.append('"%s"' % p.name)

        output.append("  with_items: [%s]" % ', '.join(a))
    elif args.output_format == "command":
        if not args.manager:
            print("--manager is required for command output.")
            sys.exit(EXIT_USAGE)

        for p in project.get_requirements(env=args.env, manager=args.manager):
            output.append(p.get_command())
    elif args.output_format == "markdown":
        output.append("## Requirements")
        output.append("")

        # By default we organize the markdown output around environment. This changes if the user has given us an env.
        if args.env:
            for p in project.get_requirements(env=args.env, manager=args.manager):
                output.append(p.to_markdown())
        else:
            for env in ENVIRONMENTS:
                output.append("### %s" % env)
                output.append("")

                for p in project.get_requirements(env=env, manager=args.manager):
                    output.append(p.to_markdown())
    elif args.output_format == "plain":
        output.append("# Generated by lspackages %s" % datetime.utcnow())

        if args.manager == "pip" and args.env != BASE_ENVIRONMENT:
            output.append("-r base.pip")

        for p in project.get_requirements(env=args.env, manager=args.manager):
            try:
                output.append(p.to_plain())
            except OutputError, e:
                print(e)
                sys.exit(EXIT_OTHER)
    elif args.output_format == "rst":
        output.append("********")
        output.append("Packages")
        output.append("********")
        output.append("")

        # By default we organize the rst output around environment. This changes if the user has given us an env.
        if args.env:
            for p in project.get_requirements(env=args.env, manager=args.manager):
                output.append(p.to_rst())
        else:
            for env in ENVIRONMENTS:
                output.append(env)
                output.append("=" * len(env))
                output.append("")

                for p in project.get_requirements(env=env, manager=args.manager):
                    output.append(p.to_rst())
    else:
        output.append("=" * 105)
        output.append("%s Packages" % project.title)
        output.append("=" * 105)
        output.append(
            "%-40s %-10s %s"
            % ("Package", "Manager", "Environment")
        )
        output.append("-" * 105)

        for p in project.get_requirements(env=args.env):
            output.append(
                "%-40s %-10s %s"
                % (p.title, p.manager, ", ".join(p.env))
            )

    if args.output_file:
        try:
            result = write_file(args.output_file, "\n".join(output))
        except OutputError, e:
            print(e)
            sys.exit(EXIT_OTHER)
        if result:
            print("%s format written to %s." % (args.output_format, args.output_file))
        else:
            print("Could not write to: %s" % args.output_file)
            sys.exit(EXIT_OTHER)
    else:
        print("\n".join(output))

    sys.exit(EXIT_OK)


def project_init():
    """Initialize a project, creating various common files using intelligent defaults. Or at least *some* defaults."""

    # Define command meta data.
    __author__ = "Shawn Davis <shawn@develmaycare.com>"
    __date__ = "2016-12-12"
    __help__ = """"""
    __version__ = "0.1.2-d"

    # Initialize the argument parser.
    parser = ArgumentParser(description=__doc__, epilog=__help__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument(
        "project_name",
        help="The name of the project. The directory will be created if it does not exist in $PROJECT_HOME",
    )

    parser.add_argument(
        "--business=",
        dest="business_name",
        help="Set the name of the developer organization."
    )

    parser.add_argument(
        "-B=",
        dest="business_code",
        help="Business code. If omitted it is automatically dervied from the business name."
    )

    parser.add_argument(
        "-c=",
        "--category=",
        dest="category",
        help='Project category. For example, django or wagtail. Default is "uncategorized".'
    )

    parser.add_argument(
        "--client=",
        dest="client_name",
        help="Set the name of the client organization."
    )

    parser.add_argument(
        "-C=",
        dest="client_code",
        help="Client code. If omitted it is automatically derived from the client name."
    )

    parser.add_argument(
        "-d=",
        "--description=",
        dest="description",
        help="A brief description of the project."
    )

    parser.add_argument(
        "-L=",
        "--license=",
        dest="license_code",
        help="License code. Use lice --help for list of valid codes."
    )

    parser.add_argument(
        "-p=",
        "--path=",
        default=PROJECT_HOME,
        dest="project_home",
        help="Path to where projects are stored. Defaults to %s" % PROJECT_HOME
    )

    parser.add_argument(
        "--prompt=",
        action="store_true",
        dest="prompt",
        help="Prompt for options rather than providing them via the command line."
    )

    parser.add_argument(
        "-s=",
        "--status=",
        dest="status",
        help="Filter by project status. Use ? to list available statuses."
    )

    parser.add_argument(
        "--title=",
        dest="title",
        help="Specify the project title. Defaults to the project name."
    )

    parser.add_argument(
        "-t=",
        "--type=",
        dest="project_type",
        help='Specify the project type. Defaults to "project".'
    )

    # Access to the version number requires special consideration, especially
    # when using sub parsers. The Python 3.3 behavior is different. See this
    # answer: http://stackoverflow.com/questions/8521612/argparse-optional-subparser-for-version
    # parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    parser.add_argument(
        "-v",
        action="version",
        help="Show version number and exit.",
        version=__version__
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Show verbose version information and exit.",
        version="%(prog)s" + " %s %s by %s" % (__version__, __date__, __author__)
    )

    # Parse arguments. Help, version, and usage errors are automatically handled.
    args = parser.parse_args()

    # Get additional options if prompted.
    if args.prompt:

        if args.title:
            title = args.title
        else:
            title = get_input("Title", default=args.project_name)

        if args.description:
            description = args.description
        else:
            description = get_input("Description")

        if args.category:
            category = args.category
        else:
            category = get_input("Category")

        if args.project_type:
            project_type = args.project_type
        else:
            project_type = get_input("Type", default="project")

        is_client_project = get_input("Is this project for a client?", choices=["y", "n"])
        if is_client_project == "y":

            if args.client_name:
                client_name = args.client_name
            else:
                client_name = get_input("Client Name", required=True)

            if args.client_name:
                client_code = args.client_code
            else:
                default_client_code = BaseOrganization.get_default_code(client_name)
                client_code = get_input("Client Code", default=default_client_code)
        else:
            client_code = None
            client_name = None

        if args.business_name:
            business_name = args.business_name
        else:
            business_name = get_input("Business/Developer Name", required=True)

        if args.business_code:
            business_code = args.business_code
        else:
            default_business_code = BaseOrganization.get_default_code(business_name)
            business_code = get_input("Business/Developer Code", default=default_business_code)

        if args.status:
            status = args.status
        else:
            status = get_input("Status", default=DEVELOPMENT)

        if args.license_code:
            license_code = args.license_code
        else:
            license_code = get_input("License", choices=LICENSE_CHOICES, default="bsd3")
    else:
        business_code = args.business_code
        business_name = args.business_name
        category = args.category or "uncategorized"
        client_code = args.client_code
        client_name = args.client_name
        description = args.description
        license_code = args.license_code or "bsd3"
        project_type = args.project_type or "project"
        status = args.status or DEVELOPMENT
        title = args.title or args.project_name

    # Create instances for business and client.
    if business_name:
        business = Business(business_name, code=business_code)
    else:
        business = None

    if client_name:
        client = Client(client_name, code=client_code)
    else:
        client = None

    # Create a project instance.
    project = Project(args.project_name, path=args.project_home)

    # Set project values from input.
    project.business = business
    project.category = category
    project.client = client
    project.description = description
    project.license = license_code
    project.type = project_type
    project.status = status
    project.title = title

    # Initialize the project.
    if project.initialize():
        sys.exit(EXIT_OK)
    else:
        print_error(project.get_error(), exit_code=EXIT_OTHER)


def project_parser():
    """Find, parse, and collect project information."""

    __author__ = "Shawn Davis <shawn@develmaycare.com>"
    __date__ = "2016-12-11"
    __help__ = """FILTERING

Use the -f/--filter option to by most project attributes:

- category
- description (partial, case insensitive)
- name (partial, case insensitive)
- org (business/client code)
- scm
- tag
- type

"""
    __version__ = "2.0.0-d"

    # Define options and arguments.
    parser = ArgumentParser(description=__doc__, epilog=__help__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="show_all",
        help="Show projects even if there is no project.ini file."
    )

    parser.add_argument(
        "--dirty",
        action="store_true",
        dest="show_dirty",
        help="Only show projects with dirty repos."
    )

    parser.add_argument(
        "-d",
        "--disk",
        action="store_true",
        dest="include_disk",
        help="Calculate disk space. Takes longer to run."
    )

    parser.add_argument(
        "-f=",
        "--filter=",
        action="append",
        dest="criteria",
        help="Specify filter in the form of key:value. This may be repeated. Use ? to list available values."
    )

    parser.add_argument(
        "-n=",
        "--name=",
        dest="project_name",
        help="Find a project by name and display it's information."
    )

    parser.add_argument(
        "-p=",
        "--path=",
        default=PROJECT_HOME,
        dest="project_home",
        help="Path to where projects are stored. Defaults to %s" % PROJECT_HOME
    )

    # Access to the version number requires special consideration, especially
    # when using sub parsers. The Python 3.3 behavior is different. See this
    # answer: http://stackoverflow.com/questions/8521612/argparse-optional-subparser-for-version
    # parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    parser.add_argument(
        "-v",
        action="version",
        help="Show version number and exit.",
        version=__version__
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Show verbose version information and exit.",
        version="%(prog)s" + " %s %s by %s" % (__version__, __date__, __author__)
    )

    # Parse arguments. Help, version, and usage errors are automatically handled.
    args = parser.parse_args()
    # print args

    # Capture (and validate) filtering options.
    criteria = dict()
    if args.criteria:
        for c in args.criteria:

            # We need to test for the proper format of the each filter given.
            try:
                key, value = c.split(":")
            except ValueError:
                print_warning('Filter must be given in "key:value" format: %s' % c)
                sys.exit(EXIT_INPUT)

            # Handle requests to display available values by which filtering may occur. Otherwise, set criteria.
            if value == "?":
                print(key)
                print("-" * 80)

                d = get_distinct_project_attributes(key, path=args.project_home)
                for name, count in d.items():
                    print("%s (%s)" % (name, count))

                print("")

                sys.exit(EXIT_OK)
            else:
                criteria[key] = value

    # Handle project by name requests.
    if args.project_name:
        project = autoload_project(args.project_name, include_disk=args.include_disk, path=args.project_home)

        if not project.is_loaded:
            print("Could not autoload the project: %s" % args.project_name)

            if project.has_error:
                print("Error: %s" % project.get_error())

            sys.exit(EXIT_OTHER)

        print(project.to_markdown())

        sys.exit(EXIT_OK)

    # Print the report heading.
    heading = "Projects"
    if "type" in criteria:
        heading += " (%s)" % criteria['type']

    print("=" * 120)
    print(heading)
    print("=" * 120)

    # Print the column headings.
    print(
        "%-30s %-20s %-15s %-5s %-10s %-15s %-10s %-4s"
        % ("Title", "Category", "Type", "Org", "Version", "Status", "Disk", "SCM")
    )
    print("-" * 120)

    # Add criteria not included with the --filter option.
    if args.show_dirty:
        criteria['is_dirty'] = True

    # Print the rows.
    projects = get_projects(
        args.project_home,
        criteria=criteria,
        include_disk=args.include_disk,
        show_all=args.show_all
    )

    if len(projects) == 0:
        print("")
        print("No results.")
        sys.exit(EXIT_OK)

    dirty_count = 0
    dirty_list = list()
    error_count = 0
    for p in projects:

        if len(p.title) > 30:
            title = p.title[:27] + "..."
        else:
            title = p.title

        if p.config_exists:
            config_exists = ""
        else:
            config_exists = "*"

        if p.has_error:
            config_exists += " (e)"
            error_count += 1
        else:
            pass

        if p.is_dirty:
            dirty_count += 1
            dirty_list.append(p.name)
            scm = "%s+" % p.scm
        else:
            scm = p.scm

        print(
            "%-30s %-20s %-15s %-5s %-10s %-15s %-10s %-4s %-1s"
            % (title, p.category, p.type, p.org, p.version, p.status, p.disk, scm, config_exists)
        )

    if len(projects) == 1:
        label = "result"
    else:
        label = "results"

    print("-" * 120)
    print("")
    print("%s %s." % (len(projects), label))

    if args.show_all:
        print("* indicates absence of project.ini file.")

    if error_count >= 1:
        print("(e) indicates an error parsing the project.ini file. Use the --name switch to find out more.")

    if dirty_count == 1:
        print("One project with uncommitted changes: %s" % dirty_list[0])
    elif dirty_count > 1:
        print("%s projects with uncommitted changes." % dirty_count)
        for i in dirty_list:
            print("    cd %s/%s && git st" % (PROJECT_HOME, i))
    else:
        print("No projects with uncommitted changes.")

    # Quit.
    sys.exit(EXIT_OK)


def project_status():
    """Get information on a project."""

    # Define command meta data.
    __author__ = "Shawn Davis <shawn@develmaycare.com>"
    __date__ = "2016-12-11"
    __help__ = """"""
    __version__ = "0.2.0-d"

    # Initialize the argument parser.
    parser = ArgumentParser(description=__doc__, epilog=__help__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument(
        "project_name",
        help="The name of the project. The directory will be created if it does not exist in $PROJECT_HOME",
    )

    parser.add_argument(
        "-d",
        "--disk",
        action="store_true",
        dest="include_disk",
        help="Calculate disk space. Takes longer to run."
    )

    parser.add_argument(
        "-p=",
        "--path=",
        default=PROJECT_HOME,
        dest="project_home",
        help="Path to where projects are stored. Defaults to %s" % PROJECT_HOME
    )

    # Access to the version number requires special consideration, especially
    # when using sub parsers. The Python 3.3 behavior is different. See this
    # answer: http://stackoverflow.com/questions/8521612/argparse-optional-subparser-for-version
    # parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    parser.add_argument(
        "-v",
        action="version",
        help="Show version number and exit.",
        version=__version__
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Show verbose version information and exit.",
        version="%(prog)s" + " %s %s by %s" % (__version__, __date__, __author__)
    )

    # Parse arguments. Help, version, and usage errors are automatically handled.
    args = parser.parse_args()

    project = autoload_project(args.project_name, include_disk=args.include_disk, path=args.project_home)

    if not project.is_loaded:
        print_warning("Could not autoload the project: %s" % args.project_name)

        if project.has_error:
            print_error("Error: %s" % project.get_error())

        sys.exit(EXIT_OTHER)

    print(project.to_markdown())

    sys.exit(EXIT_OK)


def version_update():
    """Increment the version number immediately after checking out a release branch."""

    __author__ = "Shawn Davis <shawn@develmaycare.com>"
    __date__ = "2016-12-11"
    __help__ = """

    """
    __version__ = "0.12.0-d"

    # Define options and arguments.
    parser = ArgumentParser(description=__doc__, epilog=__help__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument(
        "project_name",
        help="The name of the project. Typically, the directory name in which the project is stored."
    )

    parser.add_argument(
        "-b=",
        "--build=",
        dest="build",
        help="Supply build meta data."
    )

    parser.add_argument(
        "-M",
        "--major",
        action="store_true",
        dest="major",
        help="Increase the major version number when you make changes to the public API that are "
             "backward-incompatible."
    )

    parser.add_argument(
        "-m",
        "--minor",
        action="store_true",
        dest="minor",
        help="Increase the minor version number when new or updated functionality has been implemented "
             "that does not change the public API."
    )

    parser.add_argument(
        "-n=",
        "--name=",
        dest="name",
        help="Name your release."
    )

    parser.add_argument(
        "-p",
        "--patch",
        action="store_true",
        dest="patch",
        help="Set (or increase) the patch level when backward-compatible bug-fixes have been implemented."
    )

    parser.add_argument(
        "-P=",
        "--path=",
        default=PROJECT_HOME,
        dest="path",
        help="The path to where projects are stored. Defaults to %s" % PROJECT_HOME
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        dest="preview_only",
        help="Preview the output, but don't make any changes."
    )

    parser.add_argument(
        "-s=",
        "--status=",
        dest="status",
        help="Use the status to denote a pre-release version."
    )

    parser.add_argument(
        "-T=",
        "--template=",
        dest="template",
        help="Path to the version.py template you would like to use. Use ? to see the default."
    )

    # Access to the version number requires special consideration, especially
    # when using sub parsers. The Python 3.3 behavior is different. See this
    # answer: http://stackoverflow.com/questions/8521612/argparse-optional-subparser-for-version
    # parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    parser.add_argument(
        "-v",
        action="version",
        help="Show version number and exit.",
        version=__version__
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Show verbose version information and exit.",
        version="%(prog)s" + " %s %s by %s" % (__version__, __date__, __author__)
    )

    # This will display help or input errors as needed.
    args = parser.parse_args()
    # print args

    # Display the default version.py template.
    if args.template == "?":
        print(Version.get_template())
        sys.exit(EXIT_OK)

    # Get the project. Make sure it exists.
    project = Project(args.project_name, args.path)
    if not project.exists:
        print("Project does not exist: %s" % project.name)
        sys.exit(EXIT_INPUT)

    # Initialize version instance.
    version = Version(project.version)

    # Update the version or (by default) display the current version.
    if args.major:
        version.bump(major=True, status=args.status, build=args.build)
    elif args.minor:
        version.bump(minor=True, status=args.status, build=args.build)
    elif args.patch:
        version.bump(patch=True, status=args.status, build=args.build)
    else:
        print(version)
        sys.exit(EXIT_OK)

    # Set the version name.
    if args.name:
        version.name = args.name

    # Write the VERSION.txt file.
    if args.preview_only:
        print("Write: %s" % project.version_txt)
        print(version.to_string())
        print("")
    else:
        write_file(project.version_txt, version.to_string())

    # Write the version.py file.
    if project.version_py:
        if args.template:
            content = parse_template(version.get_context(), args.template)
        else:
            content = parse_template(version.get_context(), Version.get_template())

        if args.preview_only:
            print("Write: %s" % project.version_py)
            print("-" * 80)
            print(content)
            print("-" * 80)
            print("")
        else:
            write_file(project.version_py, content)

    # Quit.
    print(version.to_string())
    sys.exit(EXIT_OK)
