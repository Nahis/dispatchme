
def xform(msg, config):
    # The way you map this to your system will depend very much about the way data and APIs work in your system.
    # You may have a separate customer and job API or they may be combined.
    # The key for you will be to take Dispatch's output and massage into the payload expected by your API
    # You will also need a mechanism to ensure that you can match to an existing customer rather than  creating 
    # a duplicate in your system. Again this will depend on how your system works.

    # The example below uses a 3rd party API that has both a customer and job API. But the way this system has 
    # been designed, is that when you post a new job, it will automatically map to an existing customer through
    # internal logic. If a customer is not found, the job post will fail. In which case, we now need to try again
    # but this time we post both the customer payload (to create the new customer record) and then the job payloaod
    # which will match to the customer payload just created.

    # In other external systems, you have to do an explicit customer lookup - where you try match by phone, email, 
    # street address or whatever else is available to match. That's not used in this example as that logic is handled
    # internally but we've left in sample get_customer and find_customer functions to illustrate what that might look
    # like.

    data = msg["payload"]["data"]
    entity = "customer"
    customer_id = data["customer_id"]
    customer = data[entity]
    address = data["address"]
    customer_name = "%s %s" % (customer["first_name"], customer["last_name"])
    customer_address = [{
        "city": address["city"],
        "state_prov": address["state"],
        "street_1": address["street_1"],
        "postal_code": address["postal_code"],
        "country": address["country"],
        "latitude": str(address["latitude"]),
        "longitude": str(address["longitude"])
    }]
    email = customer["email"]
    mobile_number = customer["phone_number"]
    emails = []
    if email:
        emails.append({
            "email": email
        })
    phones = []
    if mobile_number:
        phones.append({
            "phone": "%s-%s-%s" % (mobile_number[2:5], mobile_number[5:8], mobile_number[8:]),
            "type": "Mobile"
        })
    customer_out = {
        "customer_name": customer_name,
        "locations": customer_address,
        "contacts": [{
            "fname": customer["first_name"],
            "lname": customer["last_name"],
            "is_primary": True,
            "phones": phones,
            "emails": emails
        }]
    }

    headers = {
        "Content-Type": "application/json"
    }

    entity = "job"
    job_id = data["id"]
    title = data["title"]
    external_id = None
    source_id = data["source_id"] if data["source_id"] else ""
    if "external_ids" in data:
        external_id = data["external_ids"][0].split(":")[1] if data["external_ids"] else ""
    source = "%s:" % data["source"] if data["source"] else ""
    title = "%s%s %s" % (source, external_id, title)
    desc = "%s\n\n%s" % (title, data["description"])
    if "equipment_descriptions" in data:
        for equipment in data["equipment_descriptions"]:
            desc += format_text("Manufacturer", equipment, "manufacturer")
            desc += format_text("Model Number", equipment, "model_number")
            desc += format_text("Serial Number", equipment, "serial_number")
            desc += format_text("Installation Date", equipment, "installation_date")
            desc += format_text("Equipment Type", equipment, "equipment_type")
    desc += format_text("Symptom", data, "symptom")
    desc += format_text("Service Instructions", data, "service_instructions")
    job_status = "Offered"
    job_out = {
        "description": desc,
        "customer_name": customer_name,
        "status": job_status,
        "source": source,
        "category": category,
        "contact_first_name": customer["first_name"],
        "contact_last_name": customer["last_name"],
        "street_1": address["street_1"],
        "street_2": address["street_2"],
        "city": address["city"],
        "state_prov": address["state"],
        "postal_code": address["postal_code"],
        "custom_fields": [{
            "name": "Dispatchme ID",
            "value": "%s-%s-%s" % (data["id"], source_id, data["organization_id"])
        }]
    }
    job_out_id, existing = external_api(s3, host, headers, entity, job_id, account_id, xref_bucket, org_id,
                                        job=job_out, customer=customer_out, checkpoint=checkpoint,
                                        config=mapping_config, bucket=s3_checkpoint_bucket,
                                        config_version=agent_config_version, entity_type=entity_type,
                                        process_id=process_id)
    return None, None


def external_api(s3, host, headers, entity, dispatch_id, account_id=None, xref_bucket=None, org_id=None,
                 action=None, job=None, customer=None, params=None, email=None, phone=None, address=None, rec_id=None,
                 checkpoint=None, config=None, bucket=None, config_version=None, entity_type=None, process_id=None):
    # Strategy here is to create job and see if it finds customer. If it can't, create customer and create job again
    existing = False
    rec_id = xform_util.get_xref(s3, xref_bucket, xform_util.outbound, "account", account_id, "job", dispatch_id)
    if rec_id:
        rec_id = int(json.loads(rec_id)[0].split("-")[0])  # use first part of xref as ID as 2nd part is org ID
        existing = True
        print("job %s/%s already exists" % (rec_id, dispatch_id))
        return rec_id, existing  # no push or patch available
    job_out_id = None
    print("attempt to create job %s %s" % (job, org_id))
    j1 = do_request(host, "%s/v1/jobs" % host, job, headers, "post", config, checkpoint, bucket, config_version,
                    account_id, process_id, s3, org_id=org_id)
    if j1.ok:
        job_out_id = j1.json()["id"]
        print("job created against existing customer %s %s" % (job_out_id, dispatch_id))
    else:
        if j1.status_code == 422:
            errors = j1.json()
            if "Customer Name can not be found" in errors[0]["message"]:
                print("job not created so create customer because %s" % errors[0]["message"])
                c1 = do_request(host, "%s/v1/customers" % host, customer, headers, "post", config, checkpoint, bucket,
                                config_version, account_id, process_id, s3, org_id=org_id)
                if c1.ok:
                    customer_out_id = c1.json()["id"]
                    print("customer created and now create job again %s" % c1.json())
                    j2 = do_request(host, "%s/v1/jobs" % host, job, headers, "post", config, checkpoint, bucket,
                                    config_version, account_id, process_id, s3, org_id=org_id)
                    if j2.ok:
                        job_out_id = j2.json()["id"]
                        print("job created %s %s" % (job_out_id, dispatch_id))
                    else:
                        print("job could not be created 1 %s %s %s %s" % (dispatch_id, j2.status_code, j2.reason, j2.json()))
                else:
                    print("customer could not be created %s %s %s %s" % (dispatch_id, c1.status_code, j1.reason, c1.json()))
            else:
                print("job could not be created 2 %s %s %s %s" % (dispatch_id, j1.status_code, j1.reason, j1.json()))
        else:
            print("job could not be created 3 %s %s %s %s" % (dispatch_id, j1.status_code, j1.reason, j1.json()))
    if job_out_id:
        xform_util.write_xref(s3, xref_bucket, "account", account_id, "job", dispatch_id,
                              "%s-%s" % (job_out_id, org_id))
    else:
        raise(Exception("Error creating job: %s" % dispatch_id))
    return job_out_id, existing


def do_request(host, url, payload, headers, action, config, checkpoint, bucket, config_version,
               account_id, process_id, s3, retry=False, org_id=None):
    checkpoint_parts = checkpoint.split("|")
    if "Authorization" not in headers:
        token = checkpoint_parts[0] if checkpoint else ""
        headers["Authorization"] = "Bearer %s" % token  # get stored token
    r = None
    if action == "post":
        r = requests.post(url=url, json=payload, headers=headers)
    if r.ok:
        return r
    else:
        if retry:
            print("still failing after retry %s %s %s" % (r.status_code, r.reason, r.json()))
            return r
        if r.status_code == 401 and r.json()["name"] == "Unauthorized":
            a = None
            refresh_token = checkpoint_parts[1] if len(checkpoint_parts) > 1 else None
            if refresh_token:  # first try using refresh token
                print("attempting to refresh token")
                auth_payload = {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                }
                a = requests.post(url="%s/oauth/access_token" % host, json=auth_payload, headers=headers)
            if not refresh_token or not a.ok:
                print("attempting to reauth")
                auth_payload = {
                    "grant_type": "client_credentials",
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"]
                }
                a = requests.post(url="%s/oauth/access_token" % host, json=auth_payload, headers=headers)
            if a.ok:
                print("auth successful")
                auth_resp = a.json()
                if len(checkpoint_parts) == 3:
                    checkpoint = "%s|%s|%s" % (auth_resp["access_token"], auth_resp["refresh_token"],
                                               checkpoint_parts[2])
                else:
                    checkpoint = "%s|%s" % (auth_resp["access_token"], auth_resp["refresh_token"])
                    print("initial checkpoint being set for %s %s" % (org_id, checkpoint))
                xform_util.set_next_checkpoint(s3=s3, s3_bucket=bucket, config_version=config_version,
                                               entity_type="account", entity_id=account_id, process_id=process_id,
                                               checkpoint=checkpoint)
                headers["Authorization"] = "Bearer %s" % auth_resp["access_token"]
                # try request again with updated token
                print("authenticated and retrying: %s %s" % (checkpoint, headers))
                return do_request(host, url, payload, headers, action, config, checkpoint, bucket, config_version,
                                  account_id, process_id, s3, retry=True)
            else:
                print("failed to auth %s %s %s" % (a.status_code, a.reason, a.json()))
                return a
        else:
            print("failed %s %s %s" % (r.status_code, r.reason, r.json()))
            return r


def format_text(title, field, name):
    return "\n%s: %s" % (title, field[name]) if name in field and field[name] else ""


"""
def get_customer(host, headers, email, phone, address):
    customer_id = None
    if email:  # TODO: lookup by email not currently supported
        print("lookup customer by email")
        params = (("filters[email]", email),)
        customer_id = find_customer(host, headers, params, "email")
    if not customer_id and phone:
        mobile_number = phone[2:]
        print("lookup customer by mobile")
        params = (("filters[phone]", mobile_number),)
        customer_id = find_customer(host, headers, params, "mobile")
    return customer_id


def find_customer(host, headers, params, search_by):
    r1 = requests.get(url="%s/customers" % host, headers=headers, params=params)
    if r1.ok:
        recs = r1.json()
        print("%s recs %s %s:" % (search_by, recs, params))
        if "items" in recs and len(recs["items"]) > 0:
            for rec in recs["items"]:
                customer_id = rec["id"]
                print("found customer id by %s %s" % (search_by, customer_id))
                return customer_id
    return None
"""
