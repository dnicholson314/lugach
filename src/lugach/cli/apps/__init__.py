import importlib
import traceback as tb

"""
Edit this variable to enable/disable applications in LUGACH.
Two applications are commented out by default; these make
use of Lighthouse, which is a proprietary application that
affects sensitive student information. As such, they are
deprecated applications. Use them at your own risk, and with
awareness that they may not be working.
"""
app_names_and_descriptions = {
    "setup": "Setup secret variables necessary for the other applications.",
    "identify_absent_students": "Identify students who have missed an excessive number of classes.",
    "identify_quiz_concerns": "Notify students who have failed to complete an excessive number of quizzes.",
    "modify_due_dates": "Change due dates for a given student and assignment.",
    "modify_time_limits": "Add percent time to all quizzes for a given student.",
    "search_student_by_name": "Search all classes for a given student.",
    "modify_attendance": "Change attendance records for students in Top Hat.",
    "take_attendance": "Take and monitor attendance in Top Hat.",
    "get_grades": "View a student's grades in Canvas.",
}


__all__ = [*app_names_and_descriptions]


def handle_exception(e):
    print()
    print("Encountered exception ----------------------------------")
    print(*e.args)
    tb.print_tb(e.__traceback__)
    print("--------------------------------------------------------")
    input("Press ENTER to continue.")


def lint_app_name(app_name: str) -> bool:
    if type(app_name) is not str:
        raise TypeError(f"Expected a string for the app name: {app_name}.")
    if app_name not in __all__:
        raise ValueError(f"The app name given ({app_name}) was not found in __all__.")

    return True


def title_from_app_name(app_name: str) -> str:
    lint_app_name(app_name)

    title = app_name.replace("_", " ").title()
    return title


def run_app_from_app_name(app_name: str):
    lint_app_name(app_name)

    try:
        app = importlib.import_module(f"lugach.cli.apps.{app_name}")
        app.main()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Application terminated.")
    except Exception as e:
        handle_exception(e)
