import os
import subprocess
import argparse
import magic

RUN_NUMBER = "RunNumber"  # the key for the attribute
FILE_PATH = "FilePath"  # the key for the attribute, is the path for the static page and allure report zip files
CONTENT_TYPE = "ContentType"
PUT_TIMEOUT = 600  # in seconds


def parse_args():
    print("Start parse_args()")
    parser = argparse.ArgumentParser(description="Process allure reports")
    parser.add_argument(
        "--neofs_domain",
        required=True,
        type=str,
        help="NeoFS network domain, example: st1.t5.fs.neo.org",
    )
    parser.add_argument("--wallet", required=True, type=str, help="Path to the wallet")
    parser.add_argument("--cid", required=True, type=str, help="Container ID")
    parser.add_argument("--run_id", required=True, type=str, help="GitHub run ID")
    parser.add_argument(
        "--files-dir",
        type=str,
        help="Path to the directory with the files to be pushed",
    ),
    parser.add_argument(
        "--expire-at",
        type=int,
        help="Expiration epoch. If epoch is not provided, or if it is 0, the report will be stored indefinitely",
        default=None,
    )

    return parser.parse_args()


def get_password() -> str:
    print("Start get_password()")
    password = os.getenv("TEST_RESULTS_PASSWORD")
    return password


def change_root_dir_to_container_id(
    root_directory: str, current_directory: str, run_id: str
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
    if current_directory == os.path.basename(root_directory):
        return run_id
    else:
        return os.path.join(run_id, current_directory)


def push_files_to_neofs(
    directory: str,
    neofs_domain: str,
    wallet: str,
    cid: str,
    run_id: str,
    expire_at: int,
    password: str,
) -> None:
    print("Start push_files_to_neofs()")
    base_cmd = (
        f"NEOFS_CLI_PASSWORD={password} neofs-cli --rpc-endpoint {neofs_domain}:8080 "
        f"--wallet {wallet}  object put --cid {cid} --timeout {PUT_TIMEOUT}s"
    )
    print(f"Base cmd: {base_cmd}")

    if expire_at is not None and expire_at > 0:
        base_cmd += f" --expire-at {expire_at}"
    print(f"Base cmd with expire-at: {base_cmd}")

    for subdir, dirs, files in os.walk(directory):
        current_dir_name = os.path.basename(subdir)
        neofs_path_attr = change_root_dir_to_container_id(
            directory, current_dir_name, run_id
        )
        print(f"neofs_path_attr: {neofs_path_attr}")

        for filename in files:
            print(f"Filename: {filename}")
            filepath = os.path.join(subdir, filename)
            print(f"Filepath: {filepath}")
            mime_type = magic.from_file(filepath, mime=True)
            print(f"Mime type: {mime_type}")
            base_cmd_with_file = (
                f"{base_cmd} --file {filepath} --attributes {RUN_NUMBER}={run_id},"
                f"{FILE_PATH}={neofs_path_attr}/{filename},{CONTENT_TYPE}={mime_type}"
            )
            print(f"Cmd: {base_cmd_with_file}")

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


if __name__ == "__main__":
    print("Start push-to-neofs.py")
    args = parse_args()
    neofs_password = get_password()

    push_files_to_neofs(
        args.files_dir,
        args.neofs_domain,
        args.wallet,
        args.cid,
        args.run_id,
        args.expire_at,
        neofs_password,
    )
    print("End push-to-neofs.py")
