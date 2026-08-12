"""
console.py

Console helpers for infrastructure deployment.
"""

def print_header(title: str) -> None:
    """
    Print the header of a deployment section.
    """

    print(f"\nStarting: {title}...")

def print_footer(title: str) -> None:
    """
    Print the footer of a deployment section.
    """

    print(f"Finished: {title}.")

def print_step(action: str, resource: str) -> None:
    """
    Print a deployment step.
    """

    print(f"- {action} {resource}: ", end="")

def print_success(message: str = "Completed successfully.") -> None:
    """
    Print a success message.
    """

    print(message)

def print_failed(message: str = "Failed to complete.") -> None:
    """
    Print a failed message.
    """

    print(message)

def print_info(message: str) -> None:
    """
    Print an informational message.
    """

    print(message)

def print_warning(message: str) -> None:
    """
    Print a warning message.
    """

    print(f"Warning: {message}")

def print_error(message: str) -> None:
    """
    Print an error message.
    """
    print("!"*10)
    print(f"Error: {message}")
    print("!"*10)