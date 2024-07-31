#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import datetime
import json
from collections import Counter
import time


def get_operators():
    """
    Feel free to add your own 'operator' here;
    The input will be:
        ad_archives_generator: a generator of array of ad_archvie
        args: extra arguments passed in from CLI
        is_verbose: check this for debugging information
    """
    return {
        "count": count_ads,
        "save": save_to_file,
        "save_to_csv": save_to_csv,
        "start_time_trending": count_start_time_trending,
    }

def output_file_path(keyword, output_path, file_extension):
    # timestamp the output file so we don't inadvertently overwrite an old file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_filename = timestamp + "-" + keyword
    if not output_filename.endswith(file_extension):
        output_filename += file_extension
    return f"{output_path}/{output_filename}"


def count_ads(ad_archives_generator, args, output_path, is_verbose=False):
    """
    Count how many ad_archives match your query
    """
    count = 0
    for ad_archives in ad_archives_generator:
        count += len(ad_archives)
        if is_verbose:
            print("counting %d" % count)
    print(f"Total number of ads match the query: {count}")


def save_to_file(ad_archives_generator, args, output_path, is_verbose=False):
    """
    Save all retrieved ad_archives to the file; each ad_archive will be
    stored in JSON format in a single line;
    Accept one parameter:
        output_keyword: this keyword will be used to tag written files
    """
    if len(args) != 1:
        raise Exception("save_to_file action takes 1 argument: output_keyword")

    output_path = output_file_path(args[0], output_path, ".json")

    with open(output_path, "w+") as file:
        count = 0
        for ad_archives in ad_archives_generator:
            for data in ad_archives:
                file.write(json.dumps(data))
                file.write("\n")
            count += len(ad_archives)
            if is_verbose:
                print("Items written: %d" % count)

    print("Total number of ads written: %d" % count)


def save_to_csv(ad_archives_generator, args, output_path, fields, is_verbose=False):
    """
    Save all retrieved ad_archives to the output file. Each ad_archive will be
    stored as a row in the CSV
    Accept one parameter:
        output_keyword: this keyword will be used to tag written files
    """
    if len(args) != 1:
        raise Exception("save_to_csv action takes 1 argument: output_keyword")

    delimiter = ","
    total_count = 0
    output = fields + "\n"

    output_path = output_file_path(args[0], output_path, ".csv")

    for ad_archives in ad_archives_generator:
        total_count += len(ad_archives)
        if is_verbose:
            print("Items processed: %d" % total_count)
        for ad_archive in ad_archives:
            for field in list(fields.split(delimiter)):
                if field in ad_archive:
                    value = ad_archive[field]
                    if (type(value) is list and type(value[0]) is dict) or type(value) is dict:
                        value = json.dumps(value)
                    elif type(value) is list:
                        value = delimiter.join(value)
                    elif type(value) is int:
                        value = str(value)
                    output += (
                        '"' + value.replace("\n", "").replace('"', "") + '"' + delimiter
                    )
                else:
                    output += delimiter
            output = output.rstrip(",") + "\n"

    with open(output_path, "w") as csvfile:
        csvfile.write(output)

    print("Successfully wrote data to file: %s" % output_path)


def count_start_time_trending(ad_archives_generator, args, output_path, is_verbose=False):
    """
    output the count trending of ads by start date;
    Accept one parameter:
        output_keyword: this keyword will be used to tag written files
    """
    if len(args) != 1:
        raise Exception("start_time_trending action takes 1 argument: output_keyword")

    output_path = output_file_path(args[0], output_path, ".csv")

    total_count = 0
    date_to_count = Counter({})
    for ad_archives in ad_archives_generator:
        total_count += len(ad_archives)
        if is_verbose:
            print("Item processed: %d" % total_count)
        start_dates = list(
            map(
                lambda data: datetime.datetime.strptime(
                    data["ad_delivery_start_time"], "%Y-%m-%d"
                ).strftime("%Y-%m-%d"),
                ad_archives,
            )
        )
        date_to_count.update(start_dates)

    with open(output_path, "w") as csvfile:
        csvfile.write("date, count\n")
        for date in date_to_count.keys():
            csvfile.write("{}, {}\n".format(date, date_to_count[date]))

    print("Successfully wrote data to file: %s" % output_path)
