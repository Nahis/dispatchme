global class DispatchAPIConnectorAgentOut {

    // this class needs to be expanded to model the payload under PutObject

    global class DispatchAPIResponse {
        public List<DispatchAPIObject> Messages;
    }    

    global class DispatchAPIObject {
        public MessageObject Message;
    }
    
    public class MessageObject {
        public RequestObject Request;
        public String ID;
        public String Receipt;
    }

    public class RequestObject {
        public String ProcedureID;
    }    

    public class PayloadObject {
        public List<ActionsObject> Actions;
    }

    public class ActionsObject {
        public String ID;
        public PutObject Put;
    }

    public class PutObject {
        public AttachmentObject attachment;
    }

    public class AttachmentObject {
        public String updated_at;
    }
}