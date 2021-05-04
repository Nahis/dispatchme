# This is an example of sending updates back to Dispatch. Just like outbound example, this will very much depend
# on how your system works, what updates are transmitted, how those updates look (e.g. json structure), how they 
# are transmitted (webhook, polling mechanism or your end etc.). And lastly also to be able to detect that the said
# change has in fact been made. Hopefully the latter is straight-forward e.g. it is scheduled when a scheduled event 
# is sent. But sometimes that's not the case.

# For example, in the example below, while non-scheduled status are fairly easy to detect (the status is changed and 
# then you just run a mapping on that status to convert it to the equivalent Dispatch status (see playbook)), the 
# scheduled event is a little bit more invlved and we have to check a bunch of other fields to know if it's truly in a
# scheduled state. Again this will depend on the inner workings of your system.

# Also this also contains an example where we do timezone translation. If your dates are stored in UTC then this won't 
# be necessary but if you store dates in local time time zone translation will be necessary.

# Once the data translation has been done - post the payload to the Dispatch inbound endpoint


def xform(msg, config):
    records = json.loads(msg)
    records_out = []
    for record in records:
        external_id = record["external_id"]
        if external_id:
            external_id_parts = external_id.split("-")
            job_id = int(external_id_parts[0])
            account_id = int(external_id_parts[1])
            org_id = int(external_id_parts[2])
            tz = config.get("timezone", "America/New_York")
            ext_status = record["status"].lower()
            mapping_config = config["mapping_config"]["in"]
            status = xform_util.get_at(mapping_config, ["job_status", ext_status])
            status_message = xform_util.get_at(mapping_config, ["job_status_message", ext_status])
            if status:
                if status != "scheduled" or status_message:
                    job = {
                        "id": job_id,
                        "status": status,
                        "status_message": None,
                        "organization_id": org_id
                    }
                    if status_message:
                        job["status_message"] = status_message
                    elif status == "complete":
                        if record.get("due_total"):
                            job["custom_fields"] = {"gateway_total": record["due_total"]}
                        if record.get("completion_notes"):
                            job["resolution"] = record["completion_notes"]
                    records_out.append(xform_util.record_stub(record_type="job", record_version="v3", record=job))
                elif status == "scheduled" and record.get("start_date") and record.get("time_frame_promised_start") \
                        and (record.get("time_frame_promised_end") or record.get("duration")):
                        start_time_ts = parse(record["time_frame_promised_start"])
                        start_time = start_time_ts.time()
                        if record.get("time_frame_promised_end"):
                            end_time = parse(record["time_frame_promised_end"]).time()
                        else:
                            end_time = (start_time_ts + timedelta(seconds=record["duration"])).time()
                        start_date = parse(record["start_date"])
                        window_start_time = pytz.timezone(tz).localize(datetime.datetime.combine(start_date, start_time))
                        window_end_time = pytz.timezone(tz).localize(datetime.datetime.combine(start_date, end_time))
                        appt = {
                            "status": status,
                            "organization_id": org_id,
                            "job_id": job_id,
                            "time": window_start_time.isoformat(),
                            "duration": (window_end_time - window_start_time).seconds,
                            "external_id": str(record["id"])
                        }
                        records_out.append(xform_util.record_stub(record_type="appointment", record_version="v3",
                                                                  record=appt))
            else:
                xform_util.print_log("job", external_id, "status %s not mapped" % ext_status)
        else:
            xform_util.print_log("job", external_id, "not an external job")
    # POST PAYLOAD TO DISPATCH AGENT/IN


