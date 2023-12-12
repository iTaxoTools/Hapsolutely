import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen

from delocate.fuse import fuse_wheels
from yaml import safe_load


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()


def verify_file(file_path, expected_hash):
    calculated_hash = calculate_sha256(file_path)
    return calculated_hash == expected_hash


def download_file(egg, url, tmp_dir: Path) -> Path:
    with urlopen(url) as response:
        if response.getcode() != 200:
            raise Exception(
                f"Failed to download wheel for egg: {egg}. HTTP status code: {response.getcode()}"
            )
        file_name = Path(url).name
        file_path = tmp_dir / file_name
        with open(file_path, "wb") as file:
            file.write(response.read())
        return file_path


def download_universal2_wheel(wheel: dict, tmp_dir: Path):
    egg = wheel["egg"]
    url = wheel["universal2_url"]
    hash = wheel["universal2_sha256"]

    print(f"Downloading wheel for {egg}...")
    file_path = download_file(egg, url, tmp_dir)
    if not verify_file(file_path, hash):
        raise Exception(f"Wheel hash does not match for: {egg}")


def download_and_fuse_wheels(wheel: dict, tmp_dir: Path):
    egg = wheel["egg"]
    arm64_url = wheel["arm64_url"]
    arm64_hash = wheel["arm64_sha256"]
    x86_64_url = wheel["x86_64_url"]
    x86_64_hash = wheel["x86_64_sha256"]

    print(f"Downloading arm64 wheel for {egg}...")
    arm64_path = download_file(egg, arm64_url, tmp_dir)
    if not verify_file(arm64_path, arm64_hash):
        raise Exception(f"Wheel hash (arm64) does not match for: {egg}")

    print(f"Downloading x86_64 wheel for {egg}...")
    x86_64_path = download_file(egg, x86_64_url, tmp_dir)
    if not verify_file(x86_64_path, x86_64_hash):
        raise Exception(f"Wheel hash (x86_64) does not match for: {egg}")

    print(f"Fusing universal2 wheel for {egg}...")
    stem = arm64_path.name.split("-macosx")[0]
    universal2_path = tmp_dir / f"{stem}-macosx_11_0_universal2.whl"
    fuse_wheels(arm64_path, x86_64_path, universal2_path)

    arm64_path.unlink()
    x86_64_path.unlink()


def download_source_tarball(wheel: dict, tmp_dir: Path):
    egg = wheel["egg"]
    url = wheel["source_url"]
    hash = wheel["source_sha256"]

    print(f"Downloading source for {egg}...")
    file_path = download_file(egg, url, tmp_dir)
    if not verify_file(file_path, hash):
        raise Exception(f"Source hash does not match for: {egg}")


def download_wheel(wheel: dict, tmp_dir: Path):
    egg = wheel["egg"]
    if "universal2_url" in wheel:
        return download_universal2_wheel(wheel, tmp_dir)
    if "arm64_url" in wheel and "x86_64_url" in wheel:
        return download_and_fuse_wheels(wheel, tmp_dir)
    if "source_url" in wheel:
        return download_source_tarball(wheel, tmp_dir)
    raise Exception(f"Bad wheel definition for: {egg}")


def download_wheels(wheels: list[dict], tmp_dir: Path):
    for wheel in wheels:
        download_wheel(wheel, tmp_dir)


def install_all(tmp_dir: Path):
    wheels = list(tmp_dir.glob("*.whl")) + list(tmp_dir.glob("*.tar.gz"))
    cmd = [sys.executable, "-m", "pip", "install", "--force-reinstall"]
    cmd.extend(wheel.name for wheel in wheels)
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=tmp_dir)


def main(path: str):
    with open(path) as file:
        text = file.read()

    wheels = safe_load(text)

    with tempfile.TemporaryDirectory() as tmp_dir:
        download_wheels(wheels, Path(tmp_dir))
        install_all(Path(tmp_dir))


if __name__ == "__main__":
    path = Path(sys.argv[1])
    main(path)
