<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./.github/logo_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./.github/logo_light.svg">
    <img src="./.github/logo_light.svg"  width="500px" alt="NeoFS logo">
  </picture>
</p>
<p align="center">
  <a href="https://fs.neo.org">NeoFS</a> is a decentralized distributed object storage integrated with the <a href="https://neo.org">NEO Blockchain</a>.
</p>

# GitHub Action to Publish to NeoFS

# Configuration

## GitHub secrets
The following Sensitive information must be passed as [GitHub Actions secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).
It is very important to use SECRETS and NOT variables, otherwise your wallet, password and token will be available to the whole internet.

| Key                     | Value                                                                                                | Required | Default |
|-------------------------|------------------------------------------------------------------------------------------------------|----------|---------|
| `TEST_RESULTS_WALLET`   | N3 wallet. The output of this command should be here: 'cat wallet.json &#124; json_pp &#124; base64' | **Yes**  | N/A     |
| `TEST_RESULTS_PASSWORD` | N3 wallet password                                                                                   | **Yes**  | N/A     |

Please keep sensitive data safe.

## GitHub environment variables

### NeoFS network environment variables
The following variables must be passed as [GitHub Actions vars context](https://docs.github.com/en/actions/learn-github-actions/variables#using-the-vars-context-to-access-configuration-variable-values) or [GitHub Actions environment variables](https://docs.github.com/en/actions/learn-github-actions/variables).

Up-to-date information on the NeoFS network can be viewed on https://status.fs.neo.org.

If you are using the NeoFS mainnet, we recommend that you do not change `TEST_RESULTS_NEOFS_NETWORK_DOMAIN` and `TEST_RESULTS_HTTP_GATE` environment variables.

| Key                                 | Value                                                                                 | Required | Default            |
|-------------------------------------|---------------------------------------------------------------------------------------|----------|--------------------|
| `TEST_RESULTS_NEOFS_NETWORK_DOMAIN` | Rpc endpoint domain address                                                           | **No**   | st1.t5.fs.neo.org  |
| `TEST_RESULTS_HTTP_GATE`            | HTTP Gateway domain address                                                           | **No**   | http.t5.fs.neo.org |
| `TEST_RESULTS_CID`                  | Container ID for your data. For example: 7gHG4HB3BrpFcH9BN3KMZg6hEETx4mFP71nEoNXHFqrv | **Yes**  | N/A                |


### Workflow environment variables
The following variables must be passed as [GitHub Actions vars context](https://docs.github.com/en/actions/learn-github-actions/variables#using-the-vars-context-to-access-configuration-variable-values) or [GitHub Actions environment variables](https://docs.github.com/en/actions/learn-github-actions/variables).

| Key                 | Value                                                                                                                                                                                                                                                                      | Required | Default |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|---------|
| `PATH_TO_FILES_DIR` | Path to the directory with the files to be pushed                                                                                                                                                                                                                          | **Yes**  | N/A     |
| `RUN_ID`            | GitHub run ID. The ID will be a unique part of the URL address. If a new file with the same name is uploaded to the same container and with the same ID, the new file will replace the old one. We recommend using a combination of github.run_number, start time, and sha | **Yes**  | N/A     |

### Expiration period environment variables
The following variables must be passed as [GitHub Actions vars context](https://docs.github.com/en/actions/learn-github-actions/variables#using-the-vars-context-to-access-configuration-variable-values) or [GitHub Actions environment variables](https://docs.github.com/en/actions/learn-github-actions/variables).

These environment variables are responsible for the storage time of the results in the storage network in epochs (in the mainnet, an epoch is approximately equal to one hour, so we can assume that values are specified in HOURS).

After the period is over, the data will be deleted. They are convenient to use for log rotation or test reports.

They default to 0, in which case the data will be stored until they are manually deleted.
We recommend setting a reasonable and convenient for work expiration period, for example, a month (744 hours).

For results from releases, there is no expiration date, they will be stored until they are manually deleted.

| Key                            | Value                                                                                                                                                                             | Required | Default |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|---------|
| `PR_EXPIRATION_PERIOD`         | Expiration period for artifacts created as a result of [opening or modifying a PR](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request) | **No**   | 0       |
| `MASTER_EXPIRATION_PERIOD`     | Expiration period for artifacts created as a result of [master/main branch modification](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#push)   | **No**   | 0       |
| `MANUAL_RUN_EXPIRATION_PERIOD` | Expiration period for artifacts created as a result of [manually run](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch)         | **No**   | 0       |
| `OTHER_EXPIRATION_PERIOD`      | Expiration period for artifacts created as a result of other events                                                                                                               | **No**   | 0       |

## Output

| Key                    | Value                                                                                                       | Required | Default |
|------------------------|-------------------------------------------------------------------------------------------------------------|----------|---------|
| `OUTPUT_CONTAINER_URL` | Output example: https://http.storage.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/872-1696332227 | **No**   | N/A     |

# Dependencies

## Python
The GitHub runner must have Python 3 installed on it.

You can install Python like this:
```yml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11.6'
```

# Examples

```yml
name: Publish to NeoFS
on:
  push:
    branches: [ master ]
jobs:
  push-to-neofs:
    runs-on: ubuntu-latest
    steps:
      - name: Get the current date
        id: date
        shell: bash
        run: echo "::set-output name=timestamp::$(date +%s)"

      - name: Set RUN_ID
        shell: bash
        env:
          TIMESTAMP: ${{ steps.date.outputs.timestamp }}
        run: echo "RUN_ID=${{ github.run_number }}-$TIMESTAMP" >> $GITHUB_ENV
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11.6'
  
      - uses: actions/checkout@v4
      - name: Publish to NeoFS
        uses: nspcc-dev/gh-push-to-neofs@master
        with:
          TEST_RESULTS_WALLET: ${{ secrets.TEST_RESULTS_WALLET }}
          TEST_RESULTS_PASSWORD: ${{ secrets.TEST_RESULTS_PASSWORD }}
          TEST_RESULTS_NEOFS_NETWORK_DOMAIN: ${{ vars.TEST_RESULTS_NEOFS_NETWORK_DOMAIN }}
          TEST_RESULTS_HTTP_GATE: ${{ vars.TEST_RESULTS_HTTP_GATE }}
          TEST_RESULTS_CID: ${{ vars.TEST_RESULTS_CID }}
          PR_EXPIRATION_PERIOD: ${{ vars.PR_EXPIRATION_PERIOD }}
          MASTER_EXPIRATION_PERIOD: ${{ vars.MASTER_EXPIRATION_PERIOD }}
          MANUAL_RUN_EXPIRATION_PERIOD: ${{ vars.MANUAL_RUN_EXPIRATION_PERIOD }}
          OTHER_EXPIRATION_PERIOD: ${{ vars.OTHER_EXPIRATION_PERIOD }}
          PATH_TO_FILES_DIR: ${{ env.PATH_TO_FILES_DIR }}
          RUN_ID: ${{ env.RUN_ID }}
```

## How to store Allure report to NeoFS as static page