# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
from time import sleep


def splunk_single(service, search):
    kwargs_normalsearch = {"exec_mode": "normal"}
    tried = 0
    while True:
        job = service.jobs.create(search, **kwargs_normalsearch)

        # A normal search returns the job's SID right away, so we need to poll for completion
        while True:
            while not job.is_ready():
                pass
            stats = {"isDone": job["isDone"],
                     "doneProgress": float(job["doneProgress"]) * 100,
                     "scanCount": int(job["scanCount"]),
                     "eventCount": int(job["eventCount"]),
                     "resultCount": int(job["resultCount"])}

            if stats["isDone"] == "1":
                break
            else:
                sleep(2)

        # Get the results and display them
        resultCount = stats["resultCount"]
        eventCount = stats["eventCount"]
        if resultCount > 0 or tried > 5:
            break
        else:
            tried += 1
            sleep(5)
    return resultCount, eventCount
