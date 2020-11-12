global class DispatchAPIConnectorAgentOutIterator implements iterable<DispatchAPIConnectorAgentOut.DispatchAPIResponse> {
    global Iterator<DispatchAPIConnectorAgentOut.DispatchAPIResponse> Iterator() {
       return new DispatchAPIConnectorAgentOutIterable();
    }
 }