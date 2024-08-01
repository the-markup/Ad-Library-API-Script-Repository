# Ads-Library-API-Script-Repository
Ads-Library-API-Script-Repository is a set of code examples to help user/researchers understand how the Facebook Ads Library API works. It also provides a simple command-line interface(CLI) for users to easily use the Facebook Ads Library API.

## Setup

### Make sure you have Python 3 installed

This command should show you a path to the executable, like `/usr/bin/python3`
```bash
which python3
```

If Python isn't installed and you're on an Apple computer, [install homebrew](https://brew.sh/) and use it to install python3
```bash
brew install python
```

You can check [Python's downloads page](https://www.python.org/downloads/) for instructions on installing on other operating systems.

### Start a virtual environment

Create the environment
```bash
python3 -m venv venv
```

Activate it
```bash
source venv/bin/activate
```

### Install the required packages
```bash
python3 -m pip install -r requirements.txt
```

## Usage

To use these scripts to access the Meta Ad Library API, you must have a Facebook developer account, which will require you to confirm your identity (by uploading identifying documents such as a drivers license or passport) and mailing address (by entering a code that Meta sends you in the physical mail.)

Once those details are confirmed, you can create a new app (an app of type "Business" will work) which will allow you to generate an access token. That token is required by these scripts to authenticate with the API. The access token can be found on the [Graph API Explorer](https://developers.facebook.com/tools/explorer/) or the [Access Token Tool](https://developers.facebook.com/tools/accesstoken/), where it's described as the "User Token".

The access token can be passed to the script using the `-t` flag, or saved in a `.env` file with the key `ACCESS_TOKEN`. You can copy the `.env-sample` file in this repository to `.env` and fill in your token there.

```bash
cp .env-sample .env
```

If you choose to save the results of your query to a file, they will be saved in the `output` directory, in a folder time-stamped with the time you started the query.

Here are some examples on how to use the CLI:

### Count the number of political ads in Canada (CA)
replace `{access_token}` with your token
```python
python3 python/fb_ads_library_api_cli.py -t {access_token} -f 'page_id,ad_snapshot_url,funding_entity,ad_delivery_start_time' -c 'CA' -s '.' -v count
```

### Search US political ads delivered after 7/20 for "coconut" and save them to a CSV file
Assuming you've put your access token in `.env`
```python
python3 python/fb_ads_library_api_cli.py -f 'id,ad_creation_time,ad_creative_bodies,ad_creative_link_captions,ad_creative_link_descriptions,ad_creative_link_titles,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,age_country_gender_reach_breakdown,beneficiary_payers,bylines,currency,delivery_by_region,demographic_distribution,estimated_audience_size,eu_total_reach,impressions,languages,page_id,page_name,publisher_platforms,spend,target_ages,target_gender,target_locations' -c 'US' --ad-type 'POLITICAL_AND_ISSUE_ADS' -s 'coconut' --batch-size 250 --after-date 2024-07-20 -v save_to_csv coconut_after_07_20
```

### Options

You can see the available arguments by passing `--help`

```bash
python3 python/fb_ads_library_api_cli.py --help
```

```
The Facebook Ads Library API CLI Utility

positional arguments:
  action                Action to take on the ads, possible values: count,save,save_to_csv,start_time_trending
  args                  The parameter for the specific action

options:
  -h, --help            show this help message and exit
  -t ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        The Facebook developer access token
  -f FIELDS, --fields FIELDS
                        Fields to retrieve from the Ad Library API
  -s SEARCH_TERMS, --search-terms SEARCH_TERMS
                        The terms you want to search for
  -c COUNTRY, --country COUNTRY
                        Comma-separated country code (no spaces)
  --search-page-ids SEARCH_PAGE_IDS
                        The specific Facebook Page you want to search
  --ad-active-status AD_ACTIVE_STATUS
                        Filter by the current status of the ads at the moment the script runs
  --ad-type AD_TYPE     Return this type of ad, can be ALL (default), CREDIT_ADS, EMPLOYMENT_ADS, HOUSING_ADS, POLITICAL_AND_ISSUE_ADS
  --media-type MEDIA_TYPE
                        Return ads that contain this type of media, can be ALL (default), IMAGE, MEME, VIDEO, NONE
  --after-date AFTER_DATE
                        Only return ads that started delivery after this date
  --batch-size BATCH_SIZE
                        Batch size
  --retry-limit RETRY_LIMIT
                        When an error occurs, the script will abort if it fails to get the same batch this amount of times
```

## How Ads-Library-API-Script-Repository works
The script will query the [Facebook Ads library API](https://www.facebook.com/ads/library/api) to get all the Ads Library information on the Facebook platform;


## More about Facebook Ads Library
* Website: https://www.facebook.com/ads/library
* Report: https://www.facebook.com/ads/library/report
* API: https://www.facebook.com/ads/library/api

See the [CONTRIBUTING](CONTRIBUTING.md) file for how to help out.


## License
Ads-Library-API-Script-Repository is licensed under the Facebook Platform License, as found in the LICENSE file.
