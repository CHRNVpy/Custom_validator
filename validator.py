from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError, Field, create_model


# Example schemas for different event types
class EventSchemas(BaseModel):
    VmwareDiskExtend: Dict[str, Any] = Field(
        default_factory=lambda: {
            "vcenter_name": (str, ...),
            "target_vm_name": (Optional[str], None),
            "disk_size_gb": (Optional[int], None),
            "username": (Optional[str], None),
            "token": (Optional[str], None),
            "secret_namespace": (Optional[str], None),
            "secret_path": (Optional[str], None),
            "mark_disk_label": (Optional[str], None),
            "drive_letter": (Optional[str], None),
        }
    )
    VmwareSnapshot: Dict[str, Any] = Field(
        default_factory=lambda: {
            "id": (int, ...),
            "description": (str, ...),
        }
    )

    def __call__(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('__')}


# Base class for all event models
class EventModel(BaseModel):
    event_type: str

    @classmethod
    def validate_event(cls, event_data: Dict[str, Any]) -> "EventModel":
        event_type = event_data.get("event_type")
        if not event_type:
            raise ValueError("Missing event_type in event data")

        schema = getattr(EventSchemas(), event_type, None)
        if not schema:
            raise ValueError(f"Unknown event type: {event_type}")

        return EventValidator.validate(event_data, schema)


class EventValidator:
    @staticmethod
    def validate(event_data: Dict[str, Any], schema: Dict[str, Any]) -> EventModel:
        DynamicEventModel = create_model('DynamicEventModel', **schema, __base__=EventModel)

        return DynamicEventModel(**event_data)


# Function to process a list of event data
def process_events(event_data_list: List[Dict[str, Any]]):
    results = []
    for event_data in event_data_list:
        try:
            validated_event = EventModel.validate_event(event_data)
            results.append({"status": "success", "event": validated_event})
        except ValidationError as e:
            results.append({"status": "error", "message": str(e)})
        except ValueError as e:
            results.append({"status": "error", "message": str(e)})

    return results


# Example usage
event_data_list = [
    {
        "event_type": "VmwareDiskExtend",
        "vcenter_name": "v000VCS00012.Tamcentral.asp",
        "target_vm_name": "VTAM002DATA01781.TAMCENTRAL_ASP",
        "disk_size_gb": 60,
        "username": "tamcentrall\\gavi",
        "token": "",
        "secret_namespace": "",
        "secret_path": "",
        "mark_disk_label": "Hard disk 1",
        "drive_letter": "C"
    },
    {
        "event_type": "VmwareSnapshot",
        "id": 123,
        "description": "Sample description"
    },
    {
        "event_type": "GcpExtendDisk",
        "name": "Jane Doe"
        # Not existing event type
    },
    {
        "event_type": "VmwareSnapshot",
        "id": 123,
        # Missing required field 'description'
    }
]

results = process_events(event_data_list)
for result in results:
    if result["status"] == "success":
        print(f"Validated Event: {result['event']}")
    else:
        print(f"Error: {result['message']}")
