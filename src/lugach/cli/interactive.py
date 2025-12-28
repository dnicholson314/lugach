from lugach.cli import apps

HEADER = """
    Welcome to LUGACH! Please choose one of the following options (or 'q' to quit): \
"""


def print_menu():
    print(HEADER)
    for i, app_name in enumerate(apps.__all__, start=1):
        title = apps.title_from_app_name(app_name)
        print(f"        ({i}) {title}")
    print()


def get_choice():
    print_menu()

    choice = 0
    while True:
        try:
            choice = input("Choose an option: ")
            choice = int(choice)
            if choice <= 0:
                raise ValueError
            break
        except ValueError:
            if choice == "q":
                break
            print("Please enter a number listed above.")
        except (KeyboardInterrupt, EOFError):
            choice = "q"
            break

    return choice


def process_choice(choice: int):
    try:
        app_name = apps.__all__[choice - 1]
    except IndexError:
        print("Please choose one of the listed options.")
        return

    apps.run_app_from_app_name(app_name)


def main():
    while True:
        choice = get_choice()
        if choice == "q":
            print("Goodbye!")
            break
        process_choice(choice)
