#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import json
import re
from datetime import datetime

import requests


def get_ad_archive_id(data):
    """
    Extract ad_archive_id from ad_snapshot_url
    """
    return re.search(r"/\?id=([0-9]+)", data["ad_snapshot_url"]).group(1)


class FbAdsLibraryTraversal:
    default_url_parameters = [
        "access_token",
        "ad_active_status",
        "ad_reached_countries",
        "ad_type",
        "fields",
        "limit",
        "media_type",
        "search_page_ids",
        "search_terms",
    ]
    default_url_pattern = "https://graph.facebook.com/{}/ads_archive?"
    default_api_version = "v20.0"

    def __init__(
        self,
        access_token,
        fields,
        search_terms,
        ad_reached_countries,
        ad_type="ALL",
        media_type="ALL",
        search_page_ids="",
        ad_active_status="ALL",
        after_date="1970-01-01",
        limit=500,
        api_version=None,
        retry_limit=3,
    ):
        self.page_count = 0
        self.access_token = access_token
        self.fields = fields
        self.search_terms = search_terms
        self.ad_reached_countries = ad_reached_countries
        self.ad_type = ad_type
        self.media_type = media_type
        self.after_date = after_date
        self.search_page_ids = search_page_ids
        self.ad_active_status = ad_active_status
        self.limit = limit
        self.retry_limit = retry_limit
        if api_version is None:
            self.api_version = self.default_api_version
        else:
            self.api_version = api_version

    def generate_ad_archives(self):
        # construct the URL
        next_page_url = self.default_url_pattern.format(self.api_version)
        params_to_add = []

        for param in self.default_url_parameters:
            param_value = getattr(self, param)
            if param_value:
                params_to_add.append(f"{param}={param_value}")

        next_page_url += "&".join(params_to_add)

        return self.__class__._get_ad_archives_from_url(
            next_page_url, after_date=self.after_date, retry_limit=self.retry_limit
        )

    @staticmethod
    def _get_ad_archives_from_url(
        next_page_url, after_date="1970-01-01", retry_limit=3
    ):
        last_error_url = None
        last_retry_count = 0
        start_time_cutoff_after = datetime.strptime(after_date, "%Y-%m-%d").timestamp()

        while next_page_url is not None:
            response = requests.get(next_page_url)
            response_data = json.loads(response.text)
            if "error" in response_data:
                if next_page_url == last_error_url:
                    # failed again
                    if last_retry_count >= retry_limit:
                        raise Exception(
                            "Error message: [{}], failed on URL: [{}]".format(
                                json.dumps(response_data["error"]), next_page_url
                            )
                        )
                else:
                    last_error_url = next_page_url
                    last_retry_count = 0
                last_retry_count += 1
                continue

            filtered = list(
                filter(
                    lambda ad_archive: ("ad_delivery_start_time" in ad_archive)
                    and (
                        datetime.strptime(
                            ad_archive["ad_delivery_start_time"], "%Y-%m-%d"
                        ).timestamp()
                        >= start_time_cutoff_after
                    ),
                    response_data["data"],
                )
            )
            if len(filtered) == 0:
                # if no data after the after_date, break
                next_page_url = None
                break
            yield filtered

            if "paging" in response_data:
                next_page_url = response_data["paging"]["next"]
            else:
                next_page_url = None

    @classmethod
    def generate_ad_archives_from_url(cls, failure_url, after_date="1970-01-01"):
        """
        if we failed from error, later we can just continue from the last failure url
        """
        return cls._get_ad_archives_from_url(failure_url, after_date=after_date)
