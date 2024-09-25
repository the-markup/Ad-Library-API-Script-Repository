#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import os
import subprocess
import sys
import time

from dotenv import load_dotenv
from fb_ads_library_api import FbAdsLibraryTraversal
from fb_ads_library_api_operators import get_operators, save_to_csv
from fb_ads_library_api_utils import get_country_code, is_valid_fields


def argument_parser():
    parser = argparse.ArgumentParser(description="The Meta Ad Library API CLI Utility")
    parser.add_argument(
        "-t",
        "--access-token",
        help="The Facebook developer access token",
    )
    parser.add_argument(
        "-f",
        "--fields",
        help="Fields to retrieve from the Ad Library API, comma-separated, no spaces",
        required=True,
        type=validate_fields_param,
    )
    parser.add_argument(
        "-s", "--search-terms", help="The terms you want to search for, space-separated"
    )
    parser.add_argument(
        "-c",
        "--country",
        default="US",
        help="Country code(s), comma-separated, no spaces",
        required=True,
        type=validate_country_param,
    )
    parser.add_argument(
        "--search-page-ids", help="IDs for specific Facebook pages you want to search for ads from, comma-separated, no spaces"
    )
    parser.add_argument(
        "--ad-active-status",
        default="ALL",
        help="Filter by the current status of the ads at the moment the script runs, can be ALL (default), ACTIVE, INACTIVE",
    )
    parser.add_argument(
        "--ad-type",
        help="Return this type of ad, can be ALL (default), CREDIT_ADS, EMPLOYMENT_ADS, HOUSING_ADS, POLITICAL_AND_ISSUE_ADS",
        default="ALL",
    )
    parser.add_argument(
        "--media-type",
        help="Return ads that contain this type of media, can be ALL (default), IMAGE, MEME, VIDEO, NONE",
        default="ALL",
    )
    parser.add_argument(
        "--after-date",
        help="Only return ads that started delivery after this date, in the format YYYY-MM-DD",
    )
    parser.add_argument(
        "--after-page-token",
        help="Restart a previous session by passing the 'after' token included in the paging section of the response",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        help="Request records in batches of this size, default is 250",
        default=250,
    )
    parser.add_argument(
        "--retry-limit",
        type=int,
        help="How many times to retry when an error occurs, default is 3",
        default=3,
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    actions = ",".join(get_operators().keys())
    parser.add_argument(
        "action", help="Action to take on the ads, possible values: %s" % actions
    )
    parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="The parameter for the specific action"
    )
    return parser


def validate_country_param(country_input):
    if not country_input:
        return ""
    country_list = list(filter(lambda x: x.strip(), country_input.split(",")))
    if not country_list:
        raise argparse.ArgumentTypeError("Country cannot be empty")
    valid_country_codes = list(map(lambda x: get_country_code(x), country_list))
    invalid_inputs = {
        key: value
        for (key, value) in zip(country_list, valid_country_codes)
        if value is None
    }

    if invalid_inputs:
        raise argparse.ArgumentTypeError(
            "Invalid/unsupported country code: %s" % (",".join(invalid_inputs.keys()))
        )
    else:
        return ",".join(valid_country_codes)


def validate_fields_param(fields_input):
    if not fields_input:
        return False
    fields_list = list(
        filter(lambda x: x, map(lambda x: x.strip(), fields_input.split(",")))
    )
    if not fields_list:
        raise argparse.ArgumentTypeError("Fields cannot be empty")
    invalid_fields = list(filter(lambda x: not is_valid_fields(x), fields_list))
    if not invalid_fields:
        return ",".join(fields_list)
    else:
        raise argparse.ArgumentTypeError(
            "Unsupported fields: %s" % (",".join(invalid_fields))
        )


# from https://stackoverflow.com/a/53675112
def git_root_directory():
    return (
        subprocess.Popen(
            ["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE
        )
        .communicate()[0]
        .rstrip()
        .decode("utf-8")
    )


def main():
    # get the access token from .env
    load_dotenv()
    access_token = os.getenv("ACCESS_TOKEN")

    parser = argument_parser()
    opts = parser.parse_args()

    # if we didn't get an access token from env, check args
    if not access_token:
        access_token = opts.access_token

    if not opts.search_terms and not opts.search_page_ids:
        print("At least one must be set: --search-terms, --search-page-ids")
        sys.exit(1)

    if not opts.search_terms:
        search_terms = "."
    else:
        search_terms = opts.search_terms
    api = FbAdsLibraryTraversal(access_token, opts.fields, search_terms, opts.country)
    if opts.search_page_ids:
        api.search_page_ids = opts.search_page_ids
    if opts.ad_active_status:
        api.ad_active_status = opts.ad_active_status
    if opts.ad_type:
        api.ad_type = opts.ad_type
    if opts.media_type:
        api.media_type = opts.media_type
    if opts.batch_size:
        api.limit = opts.batch_size
    if opts.retry_limit:
        api.retry_limit = opts.retry_limit
    if opts.after_date:
        api.after_date = opts.after_date
    if opts.after_page_token:
        api.after = opts.after_page_token

    # where to save data
    root_directory = git_root_directory()
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = f"{root_directory}/output/{timestamp}"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # get the ad archives data
    ad_archives_generator = api.generate_ad_archives()

    if opts.action in get_operators():
        if opts.action == "save_to_csv":
            save_to_csv(
                ad_archives_generator,
                opts.args,
                output_path,
                opts.fields,
                is_verbose=opts.verbose,
            )
        else:
            get_operators()[opts.action](
                ad_archives_generator, opts.args, output_path, is_verbose=opts.verbose
            )
    else:
        print("Invalid 'action' value: %s" % opts.action)
        sys.exit(1)


if __name__ == "__main__":
    main()
