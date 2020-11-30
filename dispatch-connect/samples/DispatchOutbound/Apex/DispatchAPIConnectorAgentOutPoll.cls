global class DispatchAPIConnectorAgentOutPoll implements Database.Batchable<DispatchAPIConnectorAgentOut.DispatchAPIResponse>, Database.AllowsCallouts {

    global Iterable<DispatchAPIConnectorAgentOut.DispatchAPIResponse> start(Database.BatchableContext bc) {
        return new DispatchAPIConnectorAgentOutIterator();
	}

   	global void execute(Database.BatchableContext bc, List<DispatchAPIConnectorAgentOut.DispatchAPIResponse> scope) {
        HTTP http = new HTTP();
        for (DispatchAPIConnectorAgentOut.DispatchAPIResponse resp : scope) {
            for (DispatchAPIConnectorAgentOut.DispatchAPIObject rec : resp.Messages) {
                system.debug(rec.Message.ID);
                for (DispatchAPIConnectorAgentOut.ActionsObject action : rec.Message.Request.Payload.Actions) { // should only be 1
                    if (action.Put.containsKey(job)) {
                        // process job payload
                        system.debug(action.Put.job.id);
                    } else if (action.Put.containsKey(appointment)) {
                        // process appointment payload
                    } else if (action.Put.containsKey(attachment)) {
                        // process attachment payload
                    } else if (action.Put.containsKey(surveyresponse)) {
                        // process survey payload
                    }
                    

                }
            }
        }
    }

	global void finish(Database.BatchableContext bc) {}

}