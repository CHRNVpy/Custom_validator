import pytest
from pydantic import ValidationError

from validator import EventSchemas, EventModel, EventValidator, process_events

# Test data
valid_event_data_1 = {
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
}

valid_event_data_2 = {
    "event_type": "VmwareSnapshot",
    "id": 123,
    "description": "Sample description"
}

invalid_event_data_1 = {
    "event_type": "GcpExtendDisk",
    "name": "Jane Doe"
}

invalid_event_data_2 = {
    "event_type": "VmwareSnapshot",
    "id": 123,
}


def test_validate_event_valid():
    validated_event = EventModel.validate_event(valid_event_data_1)
    assert isinstance(validated_event, EventModel)
    assert validated_event.event_type == "VmwareDiskExtend"

    validated_event = EventModel.validate_event(valid_event_data_2)
    assert isinstance(validated_event, EventModel)
    assert validated_event.event_type == "VmwareSnapshot"


def test_validate_event_invalid():
    with pytest.raises(ValueError) as excinfo:
        EventModel.validate_event(invalid_event_data_1)
    assert "Unknown event type" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        EventModel.validate_event(invalid_event_data_2)
    assert "description" in str(excinfo.value)


def test_event_validator():
    schema = EventSchemas().VmwareDiskExtend
    event_data = valid_event_data_1.copy()
    validated_event = EventValidator.validate(event_data, schema)
    assert isinstance(validated_event, EventModel)
    assert validated_event.event_type == "VmwareDiskExtend"


def test_process_events():
    event_data_list = [
        valid_event_data_1,
        valid_event_data_2,
        invalid_event_data_1,
        invalid_event_data_2
    ]
    results = process_events(event_data_list)

    assert len(results) == 4
    assert results[0]["status"] == "success"
    assert results[1]["status"] == "success"
    assert results[2]["status"] == "error"
    assert results[3]["status"] == "error"