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

# GitHub Action to Publish Static Page to NeoFS

# Configuration

## GitHub secrets
The following Sensitive information must be passed as [GitHub Actions secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).
It is very important to use SECRETS and NOT variables, otherwise your wallet, password and token will be available to the whole internet.

| Key                     | Value                                                                                                | Required | Default |
|-------------------------|------------------------------------------------------------------------------------------------------|----------|---------|
| `TEST_RESULTS_WALLET`   | N3 wallet. The output of this command should be here: 'cat wallet.json &#124; json_pp &#124; base64' | **Yes**  | N/A     |
| `TEST_RESULTS_PASSWORD` | Wallet password                                                                                      | **Yes**  | N/A     |

## GitHub environment variables
The following settings must be passed as [GitHub Actions environment variables](https://docs.github.com/en/actions/learn-github-actions/variables).


| Key                                 | Value                                                                                 | Required | Default            |
|-------------------------------------|---------------------------------------------------------------------------------------|----------|--------------------|
| `TEST_RESULTS_NEOFS_NETWORK_DOMAIN` | Rpc endpoint domain address                                                           | **No**   | st1.t5.fs.neo.org  |
| `TEST_RESULTS_HTTP_GATE`            | HTTP Gateway domain address                                                           | **No**   | http.t5.fs.neo.org |
| `TEST_RESULTS_CID`                  | Container ID for your data. For example: 7gHG4HB3BrpFcH9BN3KMZg6hEETx4mFP71nEoNXHFqrv | **Yes**  | N/A                |

### NeoFS network environment variables
Up-to-date information on the NeoFS network can be viewed on https://status.fs.neo.org.

If you are using the NeoFS mainnet, we recommend that you do not change these environment variables.

| Key                                 | Value                                                                                 | Required | Default            |
|-------------------------------------|---------------------------------------------------------------------------------------|----------|--------------------|
| `TEST_RESULTS_NEOFS_NETWORK_DOMAIN` | Rpc endpoint domain address                                                           | **No**   | st1.t5.fs.neo.org  |
| `TEST_RESULTS_HTTP_GATE`            | HTTP Gateway domain address                                                           | **No**   | http.t5.fs.neo.org |
| `TEST_RESULTS_CID`                  | Container ID for your data. For example: 7gHG4HB3BrpFcH9BN3KMZg6hEETx4mFP71nEoNXHFqrv | **Yes**  | N/A                |


### Expiration period environment variables
These environment variables are responsible for the storage time of the results in the storage network in HOURS.

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


# Examples

## How to store Allure report to NeoFS as static page