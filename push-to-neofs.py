import os
import subprocess
import argparse
import magic

RUN_NUMBER = "RunNumber"  # the key for the attribute
FILE_PATH = "FilePath"  # the key for the attribute, is the path for the static page and allure report zip files
CONTENT_TYPE = "ContentType"
PUT_TIMEOUT = 600  # in seconds


def parse_args():
    parser = argparse.ArgumentParser(description="Process allure reports")
    parser.add_argument(
        "--neofs_domain",
        required=True,
        type=str,
        help="NeoFS network domain, example: st1.storage.fs.neo.org",
    )
    parser.add_argument("--wallet", required=True, type=str, help="Path to the wallet")
    parser.add_argument("--cid", required=True, type=str, help="Container ID")
    parser.add_argument(
        "--attributes",
        required=False,
        type=str,
        help="User attributes in form of Key1=Value1,Key2=Value2"
        "For example, it's convenient to create url links to access an object via http:"
        "FilePath=96-1697035975/dir/3.txt"
        "Type=test_result,Master=true,RUN_ID=96-1697035975",
        default=None,
    )
    parser.add_argument(
        "--url_path_prefix",
        required=False,
        type=str,
        help="This is a prefix to the url address for each of the files(objects)."
        "For example, if Container ID is HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6 and"
        "--url_path_prefix is '96-1697035975', then the url will be: "
        "  https://http.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/832-1695916423/file.txt"
        "Without --url_path_prefix the url will be:"
        "  https://http.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/file.txt",
        default=None,
    )
    parser.add_argument(
        "--files-dir",
        required=True,
        type=str,
        help="Path to the directory with the files to be pushed",
    )
    parser.add_argument(
        "--expire-at",
        type=int,
        help="Expiration epoch. If epoch is not provided, or if it is 0, the report will be stored indefinitely",
        default=None,
    )

    return parser.parse_args()


def get_password() -> str:
    password = os.getenv("NEOFS_WALLET_PASSWORD")
    return password


def change_root_dir_to_container_id(
    root_directory: str,
    filepath: str,
    run_id: str,
) -> str:
    """
    The root of the directory is changing to Container ID.
    For example, if the directory is /home/varg/work/neofs-testcases/report:
        varg@burzum:~/work/neofs-testcases/report$ tree -d
        .
        ├── data
        │   ├── attachments
        │   └── test-cases
        ├── export
        ├── history
    And
        Container ID is HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6
        Run ID is 832-1695916423
    Then the directory structure in the NeoFS will be like this:
        HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6
        ├── data
        │   ├── attachments
        │   └── test-cases
        ├── export
        ├── history
    And the static page will be available at the link:
    https://http.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/832-1695916423/data/__files__
    https://http.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/832-1695916423/data/attachments/__files__
    ...
    https://http.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/832-1695916423/export/__files__
    ...

    This adds the ability to upload a static page (such as the Allure report) and hyperlink from that static page
    to attachments that are separate objects.
    In this way we can split a static page from one huge file of several hundred megabytes to the wonderful
    world of Web 1.0 with hyperlinks.
    Isn't that cool?
    """
    relative_path = os.path.relpath(filepath, root_directory)
    return os.path.join(run_id, relative_path)


def push_file(
    directory: str,
    subdir: str,
    url_path_prefix: str,
    filename: str,
    attributes: str,
    base_cmd: str,
) -> None:
    print(f"Directory: {directory}")
    print(f"Subdir: {subdir}")
    print(f"Url path prefix: {url_path_prefix}")
    print(f"Filename: {filename}")
    print(f"Attributes: {attributes}")
    print(f"Base cmd: {base_cmd}")

    filepath = os.path.join(subdir, filename)

    print(f"Filepath: {filepath}")

    # neofs_path_attr = change_root_dir_to_container_id(directory, filepath, run_id)

    mime_type = magic.from_file(filepath, mime=True)

    relative_path = os.path.relpath(filepath, os.path.dirname(directory))
    print(f"Relative path: {relative_path}")

    if url_path_prefix is not None:
        neofs_path_attr = os.path.join(url_path_prefix, relative_path)
    else:
        neofs_path_attr = relative_path
    print(f"Filepath with url_path_prefix: {neofs_path_attr}")

    base_cmd_with_file = f"{base_cmd} --file {filepath} --attributes {FILE_PATH}={neofs_path_attr},{CONTENT_TYPE}={mime_type}"
    print(f"Base cmd with file: {base_cmd_with_file}")

    if attributes is not None:
        base_cmd_with_file += f",{attributes}"
    print(f"Base cmd with file and attributes: {base_cmd_with_file}")

    print(f"Neofs cli cmd is: {base_cmd_with_file}")

    try:
        compl_proc = subprocess.run(
            base_cmd_with_file,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=PUT_TIMEOUT,
            shell=True,
        )

        print(f"RC: {compl_proc.returncode}")
        print(f"Output: {compl_proc.stdout}")
        print(f"Error: {compl_proc.stderr}")

    except subprocess.CalledProcessError as e:
        raise Exception(
            f"Command failed: {e.cmd}\n"
            f"Error code: {e.returncode}\n"
            f"Output: {e.output}\n"
            f"Stdout: {e.stdout}\n"
            f"Stderr: {e.stderr}\n"
        )


def push_files_to_neofs(
    directory: str,
    neofs_domain: str,
    wallet: str,
    cid: str,
    attributes: str,
    url_path_prefix: str,
    expire_at: int,
    password: str,
) -> None:
    if not os.path.exists(directory):
        raise Exception(f"Directory '{directory}' does not exist.")
    if not os.listdir(directory):
        raise Exception(f"Directory '{directory}' is empty.")

    base_cmd = (
        f"NEOFS_CLI_PASSWORD={password} neofs-cli --rpc-endpoint {neofs_domain}:8080 "
        f"--wallet {wallet}  object put --cid {cid} --timeout {PUT_TIMEOUT}s"
    )
    if expire_at is not None and expire_at > 0:
        base_cmd += f" --expire-at {expire_at}"

    print(f"Directory: {directory}")
    relative_directory = os.path.relpath(directory)
    url_root = os.path.basename(relative_directory)
    print(f"Url root: {url_root}")
    print(f"Relative directory: {relative_directory}")

    base_path = os.path.abspath(directory)
    for subdir, dirs, files in os.walk(base_path):
        for filename in files:
            full_path = os.path.join(subdir, filename)
            relative_from_root = os.path.relpath(full_path, os.path.dirname(base_path))
            print(relative_from_root)

    for subdir, dirs, files in os.walk(base_path):
        for filename in files:
            push_file(
                base_path, subdir, url_path_prefix, filename, attributes, base_cmd
            )


if __name__ == "__main__":
    args = parse_args()
    neofs_password = get_password()

    push_files_to_neofs(
        args.files_dir,
        args.neofs_domain,
        args.wallet,
        args.cid,
        args.attributes,
        args.url_path_prefix,
        args.expire_at,
        neofs_password,
    )
