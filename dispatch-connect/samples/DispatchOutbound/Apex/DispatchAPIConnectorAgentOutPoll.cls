global class DispatchAPIConnectorAgentOutPoll implements Database.Batchable<DispatchAPIConnectorAgentOut.DispatchAPIResponse>, Database.AllowsCallouts {

    global Iterable<DispatchAPIConnectorAgentOut.DispatchAPIResponse> start(Database.BatchableContext bc) {
        return new DispatchAPIConnectorAgentOutIterator();
	}

   	global void execute(Database.BatchableContext bc, List<DispatchAPIConnectorAgentOut.DispatchAPIResponse> scope) {
        HTTP http = new HTTP();
        for (DispatchAPIConnectorAgentOut.DispatchAPIResponse resp : scope) {
            for (DispatchAPIConnectorAgentOut.DispatchAPIObject rec : resp.Messages) {
                system.debug(rec.Message.ID); // process payload
            }
        }
    }

	global void finish(Database.BatchableContext bc) {}

}