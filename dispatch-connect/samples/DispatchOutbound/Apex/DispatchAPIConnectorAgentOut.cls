global class DispatchAPIConnectorAgentOut {

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
        public PayloadObject Payload;
    }    

    public class PayloadObject {
        public List<ActionsObject> Actions;
    }

    public class ActionsObject {
        public String ID;
        public PutObject Put;
    }

    public class PutObject {
        public JobObject job;
        public AppointmentObject appointment;
        public SurveyObject surveyappointment;
        public AttachmentObject attachment;
    }

    public class JobObject {
        public Integer id;
        public Integer organization_id;
        public String organization_external_id;
        public String title;
        public String status;
        public String status_message;
        public String external_id;
        public String updated_at;
        public String description;
        public String symptom;
        public String service_instructions;
        public Integer service_fee;
        public String service_type;
        public AddressObject address;
        public CustomerObject customer;
        public List<EquipmentObject> equipment_descriptions;
        public UiOptionsObject ui_options;
    }
    
    public class AppointmentObject {
        public Integer id;
        public Integer job_id;
        public String status;
        public String external_id;        
        public String updated_at;
        public String start_time;
        public String end_time;
        public JobObject job;
    }    

    public class AttachmentObject {
        public Integer id;
        public Integer entity_id;
        public String entity_type;
        public String file_token;
        public String name;
        public String description;
        public String updated_at;
        public String deleted_at;
        public JobObject job;
    }

    public class SurveyObject {
        public Integer id;
        public Integer job_id;
        public Integer rating;
        public String rating_message;
        public Integer account_rating;
        public String account_message;
        public String updated_at;
        public JobObject job;
    }

    public class AddressObject {
        public String street_1;
        public String street_2;
        public String postal_code;
        public String city;
        public String state;
        public String country;
        public String timezone;
    }

    public class CustomerObject {
        public Integer id;
        public String external_id;
        public String first_name;
        public String last_name;
        public String company_name;
        public String email;
        public String phone_number;
    }

    public class EquipmentObject {
        public String manufacturer;
        public String model_number;
        public String model_name;
        public String serial_number;
        public String equipment_type;
        public String installation_date;
        public String location;
        public String symptom;
    }

    public class UiOptionsObject {
        public Boolean show_decline;
        public List<String> reject_reasons;
        public List<String> complete_reasons;
        public List<String> pause_reasons;
        public List<String> cancel_reasons;
    }    
}