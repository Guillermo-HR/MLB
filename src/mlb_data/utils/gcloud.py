from subprocess import CompletedProcess
import shutil
import subprocess


class GCloudError(RuntimeError):
    """Exception raised when a gcloud command fails."""

def run_command(executable: str,*args: str) -> CompletedProcess[str]:
    """
    Execute a Google Cloud CLI command.

    Parameters
    ----------
    executable : str
        Executable name (e.g. gcloud, bq).

    *args : str
        Command arguments.

    Returns
    -------
    CompletedProcess
        Result of the executed command.

    Raises
    ------
    GoogleCloudError
        If the command exits with a non-zero status.
    """

    executable_path = (
        shutil.which(executable)
        or shutil.which(f"{executable}.cmd")
    )

    if executable_path is None:
        raise FileNotFoundError(
            f"{executable} CLI was not found in PATH."
        )

    command = [executable_path, *args]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise GCloudError(result.stderr.strip())

    return result

def run_gcloud(*args: str, project: str | None = None) -> CompletedProcess[str]:
    command = list(args)

    if project:
        command.append(f"--project={project}")

    return run_command(
        "gcloud",
        *command,
    )

def run_bq(*args: str, project: str | None = None) -> CompletedProcess[str]:
    command = []

    if project:
        command.append(f"--project_id={project}")
    command.extend(args)

    return run_command(
        "bq",
        *command,
    )