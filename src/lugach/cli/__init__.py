from canvasapi.exceptions import ResourceDoesNotExist
import click
import json
import lugach.core.thutils as thu
import lugach.core.cvutils as cvu

from lugach.cli import interactive, utils
from lugach.cli.apps import (
    app_names_and_descriptions,
    lint_app_name,
    run_app_from_app_name,
)


@click.group()
def cli() -> None:
    """A CLI tool to make Liberty GAs lives easier."""


@cli.command()
@click.argument("app_name", required=False)
@click.option("--list", is_flag=True, help="List the currently available apps.")
@click.option("-i", is_flag=True, help="Run the interactive CLI.")
def app(app_name: str | None, i: bool | None, list: bool | None) -> None:
    """
    Run CLI applications to perform GSA tasks on the command line.

    Use APP_NAME to specify the app to run. See --list for a list of apps.
    """

    if i:
        interactive.main()
        return

    if list:
        click.echo("The currently available apps: ")
        click.echo()

        for app_name, app_description in app_names_and_descriptions.items():
            click.echo(f"   {app_name:25} {app_description}")

        return

    if not app_name:
        click.secho(
            "No APP_NAME supplied. Use --list for a list of apps.", fg="red", err=True
        )
        return

    try:
        lint_app_name(app_name)
    except (TypeError, ValueError):
        click.secho(
            "Invalid app name supplied. See --list for a list of apps.",
            fg="red",
            err=True,
        )
        return

    run_app_from_app_name(app_name)


@cli.group()
def cv() -> None:
    """Retrieve information from the user's Canvas account."""


@cv.command("courses")
@click.option(
    "--role",
    help="Filter by a certain role. Options: TA, Designer, Student. Default: Designer",
)
def cv_courses(role) -> None:
    """Get a list of courses that the user can access."""
    if not role:
        role = "designer"

    canvas = cvu.create_canvas_object()
    courses = cvu.get_courses(canvas, enrolled_as=role)
    parsed_courses = utils.parse_canvas_courses_for_cli(courses)
    click.echo(json.dumps(parsed_courses, indent=4))


@cv.command("students")
@click.argument("course_id", required=True)
@click.option("-c", is_flag=True, help="Return the number of students.")
@click.option("--name", help="Filter names by a given string.")
def cv_students(course_id, c, name) -> None:
    """
    Get a list of students in a given course.

    COURSE_ID: Required. The ID of the course.
    """
    try:
        course_id = int(course_id)
    except ValueError:
        click.secho("Error: Expected a valid COURSE_ID.", fg="red", err=True)
        return

    canvas = cvu.create_canvas_object()
    try:
        course = canvas.get_course(course_id)
    except ResourceDoesNotExist:
        click.secho(
            "Error: No course found with the given COURSE_ID.", fg="red", err=True
        )
        return

    students = course.get_users(enrollment_type="student")

    if c:
        # Count manually so we don't have to deal with the rate limitations of PaginatedList
        count = 0
        for _ in students:
            count += 1

        click.echo(count)
        return

    parsed_students = utils.parse_canvas_users_for_cli(students, name)
    click.echo(json.dumps(parsed_students, indent=4))


@cv.command()
@click.argument("course_id", required=True)
def assignments(course_id):
    """
    Get a list of assignments in a given course.

    COURSE_ID: Required. The id of the course.
    """

    try:
        course_id = int(course_id)
    except ValueError:
        click.secho("Error: Expected a valid COURSE_ID.", fg="red", err=True)
        return

    canvas = cvu.create_canvas_object()
    try:
        course = canvas.get_course(course_id)
    except ResourceDoesNotExist:
        click.secho(
            "Error: No course found with the given COURSE_ID.", fg="red", err=True
        )
        return

    assignments = course.get_assignments()
    parsed_assignments = utils.parse_canvas_assignments_for_cli(assignments)
    click.echo(json.dumps(parsed_assignments, indent=4))


@cli.group()
def th() -> None:
    """Retrieve information from the user's Top Hat account."""


@th.command("courses")
def th_courses() -> None:
    """Get a list of courses that the user oversees."""
    auth_header = thu.get_auth_header_for_session()
    courses = thu.get_th_courses(auth_header)
    parsed_courses = utils.parse_top_hat_courses_for_cli(courses)

    click.echo(json.dumps(parsed_courses, indent=4))


@th.command()
@click.argument("course_id", required=True)
def students(course_id):
    """
    Get a list of students in a given course.

    COURSE_ID: Required. The id of the Top Hat course.
    """

    try:
        course_id = int(course_id)
    except ValueError:
        click.secho("Error: Expected a valid COURSE_ID.", fg="red", err=True)
        return

    auth_header = thu.get_auth_header_for_session()
    students = thu.get_th_students(auth_header, course_id=course_id)
    parsed_students = utils.parse_top_hat_students_for_cli(students)

    click.echo(json.dumps(parsed_students, indent=4))
