from app.data.schema import create_tables

from app.data.users import (
    add_test_users,
    load_users_from_file,
    get_all_users,
    create_user,
    get_user_by_id,
    delete_user,
)

from app.data.cyber_incidents import (
    migrate_cyber_incidents,
    read_all_cyber_incidents,
    create_incident,
    get_incident_by_id,
    get_all_incidents,
    delete_incident,
)

from app.data.datasets import (
    migrate_datasets,
    read_all_datasets,
    create_dataset,
    get_dataset_by_id,
    get_all_datasets,
    delete_dataset,
)

from app.data.it_tickets import (
    migrate_tickets,
    read_all_tickets,
    create_ticket,
    get_ticket_by_id,
    get_all_tickets,
    delete_ticket,
)

# =========================
# COLORS
# =========================
RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"


# =========================
# HELPERS
# =========================
def print_header(text: str):
    print(f"\n{CYAN}{'=' * 60}{RESET}")
    print(f"{CYAN}{text}{RESET}")
    print(f"{CYAN}{'=' * 60}{RESET}")


def print_info(text: str):
    print(f"{YELLOW}[INFO]{RESET} {text}")


def print_ok(text: str):
    print(f"{GREEN}[OK]{RESET} {text}")


def print_error(text: str):
    print(f"{RED}[ERROR]{RESET} {text}")


def pause():
    input(f"\n{YELLOW}Press Enter to continue...{RESET}")


# =========================
# USERS MENU
# =========================
def menu_users():
    while True:
        print_header("USERS MANAGEMENT")
        print("1 - List all users")
        print("2 - Create demo user")
        print("3 - Get user by ID")
        print("4 - Delete user by ID")
        print("0 - Back to main menu")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            users = get_all_users()
            print_ok(f"Total users: {len(users)}")
            for u in users:
                print(u)
            pause()

        elif choice == "2":
            print_info("Creating demo user...")
            username = input("Username (default demo_cli_user): ").strip() or "demo_cli_user"
            email = input("Email (default demo@example.com): ").strip() or "demo@example.com"
            role = input("Role (default user): ").strip() or "user"

            # Very simple demo hash placeholder
            password_hash = "demo_cli_hash"
            is_admin = 1 if role.lower() == "admin" else 0
            disabled = 0
            license_key = "CLI-DEMO-KEY"

            try:
                user_id = create_user(
                    username,
                    password_hash,
                    is_admin,
                    disabled,
                    role,
                    email,
                    license_key,
                )
                print_ok(f"Created user with id {user_id}")
            except Exception as e:
                print_error(f"Could not create user: {e}")
            pause()

        elif choice == "3":
            try:
                user_id = int(input("Enter user ID: ").strip())
            except ValueError:
                print_error("ID must be an integer.")
                pause()
                continue

            user = get_user_by_id(user_id)
            if user:
                print_ok("User found:")
                print(user)
            else:
                print_error("User not found.")
            pause()

        elif choice == "4":
            try:
                user_id = int(input("Enter user ID to delete: ").strip())
            except ValueError:
                print_error("ID must be an integer.")
                pause()
                continue

            user = get_user_by_id(user_id)
            if not user:
                print_error("User not found.")
                pause()
                continue

            print_info(f"About to delete user: {user}")
            confirm = input("Are you sure? (y/N): ").strip().lower()
            if confirm == "y":
                try:
                    delete_user(user_id)
                    print_ok("User deleted.")
                except Exception as e:
                    print_error(f"Could not delete user: {e}")
            else:
                print_info("Delete cancelled.")
            pause()

        elif choice == "0":
            break
        else:
            print_error("Invalid option.")
            pause()


# =========================
# CYBER INCIDENTS MENU
# =========================
def menu_incidents():
    while True:
        print_header("CYBER INCIDENTS MANAGEMENT")
        print("1 - List all incidents (count only)")
        print("2 - List first 10 incidents")
        print("3 - Create demo incident")
        print("4 - Get incident by ID")
        print("5 - Delete incident by ID")
        print("0 - Back to main menu")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            rows = get_all_incidents()
            print_ok(f"Total incidents: {len(rows)}")
            pause()

        elif choice == "2":
            rows = get_all_incidents()
            for r in rows[:10]:
                print(r)
            pause()

        elif choice == "3":
            print_info("Creating demo incident...")
            try:
                incident_id = int(input("Incident ID (default 9999): ").strip() or "9999")
            except ValueError:
                print_error("Incident ID must be an integer.")
                pause()
                continue

            timestamp = input("Timestamp (default 2024-12-01 12:00:00): ").strip() or "2024-12-01 12:00:00"
            severity = input("Severity (Low/Medium/High/Critical, default High): ").strip() or "High"
            category = input("Category (default Testing): ").strip() or "Testing"
            status = input("Status (default Open): ").strip() or "Open"
            description = input("Description (default CLI demo incident): ").strip() or "CLI demo incident"

            try:
                create_incident(incident_id, timestamp, severity, category, status, description)
                print_ok("Demo incident created.")
            except Exception as e:
                print_error(f"Could not create incident: {e}")
            pause()

        elif choice == "4":
            try:
                incident_id = int(input("Incident ID: ").strip())
            except ValueError:
                print_error("Incident ID must be an integer.")
                pause()
                continue

            inc = get_incident_by_id(incident_id)
            if inc:
                print_ok("Incident found:")
                print(inc)
            else:
                print_error("Incident not found.")
            pause()

        elif choice == "5":
            try:
                incident_id = int(input("Incident ID to delete: ").strip())
            except ValueError:
                print_error("Incident ID must be an integer.")
                pause()
                continue

            inc = get_incident_by_id(incident_id)
            if not inc:
                print_error("Incident not found.")
                pause()
                continue

            print_info(f"About to delete incident: {inc}")
            confirm = input("Are you sure? (y/N): ").strip().lower()
            if confirm == "y":
                try:
                    delete_incident(incident_id)
                    print_ok("Incident deleted.")
                except Exception as e:
                    print_error(f"Could not delete incident: {e}")
            else:
                print_info("Delete cancelled.")
            pause()

        elif choice == "0":
            break
        else:
            print_error("Invalid option.")
            pause()


# =========================
# DATASETS MENU
# =========================
def menu_datasets():
    while True:
        print_header("DATASETS METADATA MANAGEMENT")
        print("1 - List all datasets (count only)")
        print("2 - List all datasets (full)")
        print("3 - Create demo dataset")
        print("4 - Get dataset by ID")
        print("5 - Delete dataset by ID")
        print("0 - Back to main menu")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            rows = get_all_datasets()
            print_ok(f"Total datasets: {len(rows)}")
            pause()

        elif choice == "2":
            rows = get_all_datasets()
            for r in rows:
                print(r)
            pause()

        elif choice == "3":
            print_info("Creating demo dataset...")
            try:
                dataset_id = int(input("Dataset ID (default 7777): ").strip() or "7777")
            except ValueError:
                print_error("Dataset ID must be an integer.")
                pause()
                continue

            name = input("Name (default CLI_Demo_Dataset): ").strip() or "CLI_Demo_Dataset"
            try:
                rows_count = int(input("Rows (default 1000): ").strip() or "1000")
                cols_count = int(input("Columns (default 10): ").strip() or "10")
            except ValueError:
                print_error("Rows and columns must be integers.")
                pause()
                continue

            uploaded_by = input("Uploaded by (default cli_user): ").strip() or "cli_user"
            upload_date = input("Upload date (default 2024-12-01): ").strip() or "2024-12-01"

            try:
                create_dataset(dataset_id, name, rows_count, cols_count, uploaded_by, upload_date)
                print_ok("Demo dataset created.")
            except Exception as e:
                print_error(f"Could not create dataset: {e}")
            pause()

        elif choice == "4":
            try:
                dataset_id = int(input("Dataset ID: ").strip())
            except ValueError:
                print_error("Dataset ID must be an integer.")
                pause()
                continue

            ds = get_dataset_by_id(dataset_id)
            if ds:
                print_ok("Dataset found:")
                print(ds)
            else:
                print_error("Dataset not found.")
            pause()

        elif choice == "5":
            try:
                dataset_id = int(input("Dataset ID to delete: ").strip())
            except ValueError:
                print_error("Dataset ID must be an integer.")
                pause()
                continue

            ds = get_dataset_by_id(dataset_id)
            if not ds:
                print_error("Dataset not found.")
                pause()
                continue

            print_info(f"About to delete dataset: {ds}")
            confirm = input("Are you sure? (y/N): ").strip().lower()
            if confirm == "y":
                try:
                    delete_dataset(dataset_id)
                    print_ok("Dataset deleted.")
                except Exception as e:
                    print_error(f"Could not delete dataset: {e}")
            else:
                print_info("Delete cancelled.")
            pause()

        elif choice == "0":
            break
        else:
            print_error("Invalid option.")
            pause()


# =========================
# IT TICKETS MENU
# =========================
def menu_tickets():
    while True:
        print_header("IT TICKETS MANAGEMENT")
        print("1 - List all tickets (count only)")
        print("2 - List first 10 tickets")
        print("3 - Create demo ticket")
        print("4 - Get ticket by ID")
        print("5 - Delete ticket by ID")
        print("0 - Back to main menu")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            rows = get_all_tickets()
            print_ok(f"Total tickets: {len(rows)}")
            pause()

        elif choice == "2":
            rows = get_all_tickets()
            for r in rows[:10]:
                print(r)
            pause()

        elif choice == "3":
            print_info("Creating demo ticket...")
            try:
                ticket_id = int(input("Ticket ID (default 8888): ").strip() or "8888")
            except ValueError:
                print_error("Ticket ID must be an integer.")
                pause()
                continue

            created = input("Created (default 2024-12-03 09:00:00): ").strip() or "2024-12-03 09:00:00"
            priority = input("Priority (Low/Medium/High/Critical, default Low): ").strip() or "Low"
            issue_type = input("Issue type (default CLI demo issue): ").strip() or "CLI demo issue"
            assigned_to = input("Assigned to (default cli_agent): ").strip() or "cli_agent"
            status = input("Status (default Open): ").strip() or "Open"
            description = input("Description (default CLI demo ticket): ").strip() or "CLI demo ticket"

            try:
                create_ticket(ticket_id, created, priority, issue_type, assigned_to, status, description)
                print_ok("Demo ticket created.")
            except Exception as e:
                print_error(f"Could not create ticket: {e}")
            pause()

        elif choice == "4":
            try:
                ticket_id = int(input("Ticket ID: ").strip())
            except ValueError:
                print_error("Ticket ID must be an integer.")
                pause()
                continue

            t = get_ticket_by_id(ticket_id)
            if t:
                print_ok("Ticket found:")
                print(t)
            else:
                print_error("Ticket not found.")
            pause()

        elif choice == "5":
            try:
                ticket_id = int(input("Ticket ID to delete: ").strip())
            except ValueError:
                print_error("Ticket ID must be an integer.")
                pause()
                continue

            t = get_ticket_by_id(ticket_id)
            if not t:
                print_error("Ticket not found.")
                pause()
                continue

            print_info(f"About to delete ticket: {t}")
            confirm = input("Are you sure? (y/N): ").strip().lower()
            if confirm == "y":
                try:
                    delete_ticket(ticket_id)
                    print_ok("Ticket deleted.")
                except Exception as e:
                    print_error(f"Could not delete ticket: {e}")
            else:
                print_info("Delete cancelled.")
            pause()

        elif choice == "0":
            break
        else:
            print_error("Invalid option.")
            pause()


# =========================
# SNAPSHOT VIEW
# =========================
def menu_snapshots():
    print_header("DATA SNAPSHOTS")
    print_info("Cyber incidents - first 5 rows:")
    print(read_all_cyber_incidents().head())

    print_info("Datasets metadata - first 5 rows:")
    print(read_all_datasets().head())

    print_info("IT tickets - first 5 rows:")
    print(read_all_tickets().head())

    pause()


# =========================
# MAIN
# =========================
def initialize_system():
    print_header("MULTI-DOMAIN INTELLIGENCE PLATFORM - INITIALIZATION")
    print_info("Creating tables...")
    create_tables()
    print_ok("Tables ready.")

    print_info("Loading users from file and adding test users...")
    add_test_users()
    load_users_from_file()
    print_ok(f"Users in DB: {len(get_all_users())}")

    print_info("Migrating CSV data...")
    migrate_cyber_incidents()
    migrate_datasets()
    migrate_tickets()
    print_ok("CSV migration completed.")


def main():
    initialize_system()

    while True:
        print_header("MANAGEMENT CONSOLE - MAIN MENU")
        print("1 - Manage Users")
        print("2 - Manage Cyber Incidents")
        print("3 - Manage Datasets")
        print("4 - Manage IT Tickets")
        print("5 - View Data Snapshots")
        print("0 - Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            menu_users()
        elif choice == "2":
            menu_incidents()
        elif choice == "3":
            menu_datasets()
        elif choice == "4":
            menu_tickets()
        elif choice == "5":
            menu_snapshots()
        elif choice == "0":
            print_ok("Exiting. Goodbye.")
            break
        else:
            print_error("Invalid option.")
            pause()


if __name__ == "__main__":
    main()
