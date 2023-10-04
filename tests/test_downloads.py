import os
import requests
import pytest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def download_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


@pytest.mark.parametrize(
    "path, local_path",
    [
        ("1.txt", "1.txt"),
        ("2.txt", "2.txt"),
        ("dir/3.txt", "dir/3.txt"),
        ("dir/subdir/4.txt", "dir/subdir/4.txt"),
    ],
)
def test_file_content(base_url, path, local_path):
    if base_url is None:
        pytest.skip("base_url is not provided. Provide it using --base_url option.")

    remote_content = download_file(f"{base_url}/{path}")
    with open(os.path.join(DATA_DIR, local_path), "r") as local_file:
        local_content = local_file.read()

    assert (
        remote_content == local_content
    ), f"Contents of {base_url + path} and {local_path} do not match."
