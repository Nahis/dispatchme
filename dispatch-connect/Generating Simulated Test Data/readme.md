Please use this file for generating test data. This simulates receiving data from the brand which will be waiting to be picked up with the credentials that have been provided. Things to note:

* `test_data_generation_key` - replace with value you receive from Dispatch.
* `test_org_id` - replace with value you receive from Dispatch
* `external_id` - this is used for upsert logic **so be sure to increment** each time you want to create a new job (this would correlate to the brand's unique ID for the job)


Once you create your job:
* You should be able to log into https://work-sandbox.dispatch.me with the credentials you've been provided to view it. This front end is a "view only" front end as for you are concerned to facilitate your testing
* You should be able connect to the agent/out endpoint to pick it up and processinto your subsequently

Subsequently you can send updates by following the playbook.