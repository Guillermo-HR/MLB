from subprocess import CompletedProcess
import shutil
import subprocess


class GCloudError(RuntimeError):
    """Exception raised when a gcloud command fails."""


def run_gcloud(*args: str, project: str | None = None,) -> CompletedProcess[str]:
    executable = shutil.which("gcloud")

    if executable is None:
        raise FileNotFoundError(
            "Google Cloud CLI (gcloud) was not found in PATH."
        )

    command = [executable, *args]

    if project:
        command.append(f"--project={project}")

    print("Running command:", " ".join(command))

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=False,
    )

    if result.returncode != 0:
        raise GCloudError(result.stderr.strip())

    return result