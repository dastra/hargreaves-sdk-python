# <img src="https://upload.wikimedia.org/wikipedia/en/thumb/3/32/Hargreaves_Lansdown_logo.svg/1280px-Hargreaves_Lansdown_logo.svg.png" height="22" /> Unofficial SDK ![](https://github.com/dastra/hargreaves-sdk-python/actions/workflows/main.yml/badge.svg)

> This is an unofficial SDK to programatically access your Hargreaves Lansdown account

## Motivation

I wanted to programatically access my Hargreaves Lansdowne accounts, but they do not currently offer an API.
This SDK accesses your accounts via their website, and allows you to list your holdings.  
This codebase started life as a port to Python of [Jamie Haywood's Javascript package](https://github.com/jamiehaywood/hargreaves).

## Installation

```shell
pip3 install hargreaves
```

## Usage 

There are examples of use in doc/examples/

### Secrets

You will need to pass your authentication credentials to the code, either in a file or via environment variables.

#### Secrets File

You will need to create a secrets.json file containing your login credentials.  
The format is:

```json
{
  "username": "tuser",
  "password": "tpass",
  "date_of_birth": "011286", // Format DDMMYY
  "secure_number": "123456"
}
```

Which is then passed to the API config loader:

```python
config = load_api_config("./secrets.json")
```

#### Secrets Environment Variables

As an alternative to storing your secrets in a file, you can set them as environment variables:

```shell
export HL_USERNAME = "tuser2"
export HL_PASSWORD = "tpass2"
export HL_DATE_OF_BIRTH = "011285" # Format DDMMYY
export HL_SECURE_NUMBER = "654321"
```

### Usage Example - listing holdings

You can find the script below in doc/examples/list_account_holdings.py

```python
from hargreaves.authentication import *
from hargreaves.account import *
from hargreaves.config import *

if __name__ == '__main__':
    # Load your secrets
    config = load_api_config("./secrets.json")

    # Log in
    session = login(config)

    # Lists all of your accounts - i.e. SIPP, ISA.
    session, accounts = list_accounts(session)

    for account_summary in accounts:
        # Fetches information in my-accounts page
        account_detail = get_account_detail(session, account_summary)
        print(f'Your {account_detail.account_type} is worth {account_detail.total_value} with the following holdings:')
        for investment in account_detail.investments:
            print(f'\tYou hold {investment.units_held} units of {investment.security_name} worth {investment.value_gbp}')

    # If you're running this in a long running server environment,
    # make sure to log out to avoid session expiration errors
    logout(session)
```

## Analysing bugs

Assuming you have pre-recorded a use-case in a Firefox browser and saved the HAR file
locally to the "./session_cache/my-recording.har" file you can run the following command
to filter out the Hargreaves Lansdown request "noise" and convert it to a set of Markdown files

```
PYTHONPATH=. python3 hargreaves/utils/har2md.py ./session_cache/my-recording.har
```

You can then compare the markdown files to scraper sessions (HAR files converted to markdown).
For more information read https://github.com/eladeon/requests-tracker-python/blob/main/README.md


## Contributing

You are welcome to suggest a new feature by raising an issue, or indeed to contribute


