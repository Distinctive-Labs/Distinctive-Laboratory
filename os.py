import os
import platform
import subprocess
import json
from datetime import datetime

USER_FILE = "users.json"
LOG_FILE = "power.in"
logged_in_user = None

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as log:
        log.write("Log File - Distinctive Laboratory OS\n")

def log_entry(message):
    with open(LOG_FILE, 'a') as log:
        log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def log_command(func):
    def wrapper(args):
        try:
            log_entry(f"Command: {func.__name__} Args: {args}")
            func(args)
        except Exception as e:
            log_entry(f"Error in {func.__name__}: {e}")
            print(f"An error occurred: {e}")
    return wrapper

def load_users():
    try:
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = password
    save_users(users)
    return True

def delete_user(username):
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        return True
    return False

def login_user(username, password):
    users = load_users()
    return users.get(username) == password

def login_system():
    global logged_in_user
    print("Welcome to Distinctive Laboratory OS\n")
    while not logged_in_user:
        action = input("Do you want to (login/register)? ").strip().lower()
        if action == "register":
            username = input("Enter new username: ").strip()
            password = input("Enter new password: ").strip()
            if register_user(username, password):
                print("Registration successful! Please login.\n")
            else:
                print("Username already exists. Try again.\n")
        elif action == "login":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            if login_user(username, password):
                print("\nLogin successful!")
                logged_in_user = username
                log_entry(f"User logged in: {username}")
            else:
                print("Incorrect username or password. Try again.\n")

commands_registry = {}

def command(name):
    def wrapper(func):
        commands_registry[name] = log_command(func)
        return func
    return wrapper

def main_shell():
    print_intro()
    while True:
        command_input = input(f"{logged_in_user}@DistinctiveLabOS$ ").strip()
        args = command_input.split()
        if not args:
            continue
        cmd = args[0]
        func = commands_registry.get(cmd)
        if func:
            func(args[1:])
        else:
            log_entry(f"Unknown command attempted: {cmd}")
            print(f"Command '{cmd}' not recognized. Type 'help' for a list of commands.")

def print_intro():
    print("\nWelcome to Distinctive Laboratory OS\nType 'help' for a list of commands.\n")

@command("help")
def help_command(args):
    print("Available Commands:\n")
    command_descriptions = {
        "help": "Show this help message",
        "sysinfo": "Display system information",
        "datetime": "Show current date and time",
        "clear": "Clear the screen",
        "calc": "Perform a basic calculation",
        "echo": "Display text",
        "network": "Display network information",
        "whoami": "Display current logged-in user",
        "reboot": "Restart the shell",
        "diskinfo": "Show disk usage information",
        "filemanager": "View and manage files in the current directory",
        "createfile": "Create a new file",
        "editfile": "Edit an existing file",
        "deletefile": "Delete a specified file",
        "logout": "Logout of the current session",
        "add_user": "Add a new user to the system",
        "del_user": "Delete an existing user",
        "list_users": "List all registered users",
        "shutdown": "Shut down the OS"
    }
    for cmd, desc in command_descriptions.items():
        print(f"{cmd:15} - {desc}")

@command("sysinfo")
def sysinfo_command(args):
    print(f"System: {platform.system()} {platform.release()} ({platform.machine()})\nProcessor: {platform.processor()}")

@command("datetime")
def datetime_command(args):
    print(f"Current Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

@command("clear")
def clear_command(args):
    os.system('cls' if os.name == 'nt' else 'clear')

@command("calc")
def calc_command(args):
    try:
        result = eval(" ".join(args))
        print(f"Result: {result}")
    except Exception as e:
        log_entry(f"Calculation error: {e}")
        print(f"Calculation error: {e}")

@command("echo")
def echo_command(args):
    print(" ".join(args))

@command("network")
def network_command(args):
    hostname = platform.node()
    ip_address = subprocess.getoutput("ipconfig" if os.name == 'nt' else "hostname -I")
    print(f"Hostname: {hostname}\nIP Address: {ip_address}")

@command("whoami")
def whoami_command(args):
    print(f"Current User: {logged_in_user}")

@command("reboot")
def reboot_command(args):
    print("Restarting OS...")
    log_entry("OS reboot initiated.")
    main_shell()

@command("diskinfo")
def diskinfo_command(args):
    info = subprocess.getoutput("df -h" if os.name != 'nt' else "wmic logicaldisk get size,freespace,caption")
    print(f"Disk Usage Information:\n{info}")

@command("filemanager")
def filemanager_command(args):
    current_dir = os.getcwd()
    print(f"Directory: {current_dir}\nFiles:")
    for filename in os.listdir(current_dir):
        print(f" - {filename}")
    print("Use commands: createfile <name>, editfile <name>, deletefile <name>")

@command("createfile")
def createfile_command(args):
    if args:
        with open(args[0], 'w') as f:
            print(f"File '{args[0]}' created.")
        log_entry(f"File created: {args[0]}")
    else:
        print("Please provide a file name.")

@command("editfile")
def editfile_command(args):
    if args:
        if not os.path.exists(args[0]):
            print(f"File '{args[0]}' not found.")
            return
        print("Enter text (type 'exit' to finish):")
        with open(args[0], 'w') as f:
            while True:
                line = input()
                if line == "exit":
                    break
                f.write(line + "\n")
        print(f"File '{args[0]}' updated.")
        log_entry(f"File edited: {args[0]}")
    else:
        print("Please provide a file name.")

@command("deletefile")
def deletefile_command(args):
    if args:
        if os.path.exists(args[0]):
            os.remove(args[0])
            print(f"File '{args[0]}' deleted.")
            log_entry(f"File deleted: {args[0]}")
        else:
            print(f"File '{args[0]}' not found.")
    else:
        print("Please provide a file name.")

@command("add_user")
def add_user_command(args):
    if len(args) < 2:
        print("Usage: add_user <username> <password>")
        return
    username, password = args[0], args[1]
    if register_user(username, password):
        print(f"User '{username}' added successfully.")
        log_entry(f"User added: {username}")
    else:
        print(f"User '{username}' already exists.")

@command("del_user")
def del_user_command(args):
    if not args:
        print("Usage: del_user <username>")
        return
    username = args[0]
    if delete_user(username):
        print(f"User '{username}' deleted successfully.")
        log_entry(f"User deleted: {username}")
    else:
        print(f"User '{username}' does not exist.")

@command("list_users")
def list_users_command(args):
    users = load_users()
    print("Registered Users:")
    for user in users:
        print(f" - {user}")

@command("logout")
def logout_command(args):
    global logged_in_user
    log_entry(f"User logged out: {logged_in_user}")
    print("Logging out.")
    logged_in_user = None
    login_system()

@command("shutdown")
def shutdown_command(args):
    log_entry("OS shutdown.")
    print("Shutting down the OS...")
    exit()

if __name__ == "__main__":
    login_system()
    main_shell()
