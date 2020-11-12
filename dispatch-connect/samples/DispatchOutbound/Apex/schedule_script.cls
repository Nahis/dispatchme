// Run this script to schedule a job retry script to run every 10 mins

for(CronTrigger ct : [SELECT Id, CronJobDetail.Name, CronJobDetail.JobType FROM CronTrigger WHERE CronJobDetail.Name like 'Dispatch Agent Out%']) {
  try{
    system.debug(LoggingLevel.ERROR,'Deleting Job: '+ ct.CronJobDetail.Name);
    system.abortJob(ct.id);
  } catch (exception e) {}
}

System.Schedule('Dispatch Agent Out-3',  '0 3 * * * ? ',  new DispatchAPIConnectorAgentOutSchedule());
System.Schedule('Dispatch Agent Out-13', '0 13 * * * ? ', new DispatchAPIConnectorAgentOutSchedule());
System.Schedule('Dispatch Agent Out-23', '0 23 * * * ? ', new DispatchAPIConnectorAgentOutSchedule());
System.Schedule('Dispatch Agent Out-33', '0 33 * * * ? ', new DispatchAPIConnectorAgentOutSchedule());
System.Schedule('Dispatch Agent Out-43', '0 43 * * * ? ', new DispatchAPIConnectorAgentOutSchedule());
System.Schedule('Dispatch Agent Out-53', '0 53 * * * ? ', new DispatchAPIConnectorAgentOutSchedule());

// To intitiate manual run
ID batchId = Database.executeBatch(new DispatchAPIConnectorAgentOutPoll(), 10);
