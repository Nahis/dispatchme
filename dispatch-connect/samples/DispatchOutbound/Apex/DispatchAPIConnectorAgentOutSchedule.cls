global class DispatchAPIConnectorAgentOutSchedule implements Schedulable {
	global void execute(SchedulableContext sc) {
		DispatchAPIConnectorAgentOutPoll poll = new DispatchAPIConnectorAgentOutPoll();
        ID batchId = Database.executeBatch(poll,10);
    }
}