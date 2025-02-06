import boto3
import json
from datetime import datetime, timedelta
import sys

# Configuration
CHANNEL_1_ID = '7528721'
CHANNEL_1_REGION = 'ap-northeast-1'
CHANNEL_2_ID = '3320982'
CHANNEL_2_REGION = 'ap-northeast-3'
INPUT_1 = "ch1-slate"
INPUT_2 = "ch1-prod"

def get_future_time():
    """Get time 30 seconds in the future"""
    return (datetime.utcnow() + timedelta(seconds=30)).strftime('%Y-%m-%dT%H:%M:%S.000Z')

def get_current_time():
    """Get current UTC time"""
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

def get_medialive_client(region):
    """Create boto3 medialive client for specified region"""
    return boto3.client('medialive', region_name=region)

def create_input_s3_json():
    return {
        "Creates": {
            "ScheduleActions": [
                {
                    "ActionName": get_current_time(),
                    "ScheduleActionSettings": {
                        "InputSwitchSettings": {
                            "InputAttachmentNameReference": INPUT_1,
                            "UrlPath": []
                        }
                    },
                    "ScheduleActionStartSettings": {
                        "ImmediateModeScheduleActionStartSettings": {}
                    }
                }
            ]
        }
    }

def create_input_live_json():
    schedule_time = get_future_time()
    return {
        "Creates": {
            "ScheduleActions": [
                {
                    "ActionName": schedule_time,
                    "ScheduleActionSettings": {
                        "InputSwitchSettings": {
                            "InputAttachmentNameReference": INPUT_2,
                            "UrlPath": []
                        }
                    },
                    "ScheduleActionStartSettings": {
                        "FixedModeScheduleActionStartSettings": {
                            "Time": schedule_time
                        }
                    }
                }
            ]
        }
    }

def create_pause_json():
    return {
        "Creates": {
            "ScheduleActions": [
                {
                    "ActionName": get_current_time(),
                    "ScheduleActionSettings": {
                        "PauseStateSettings": {
                            "Pipelines": [{"PipelineId": "PIPELINE_0"}]
                        }
                    },
                    "ScheduleActionStartSettings": {
                        "ImmediateModeScheduleActionStartSettings": {}
                    }
                }
            ]
        }
    }

def create_unpause_json():
    return {
        "Creates": {
            "ScheduleActions": [
                {
                    "ActionName": get_current_time(),
                    "ScheduleActionSettings": {
                        "PauseStateSettings": {
                            "Pipelines": []
                        }
                    },
                    "ScheduleActionStartSettings": {
                        "ImmediateModeScheduleActionStartSettings": {}
                    }
                }
            ]
        }
    }

def start_service():
    print("Event starting")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    client2 = get_medialive_client(CHANNEL_2_REGION)
    
    client1.start_channel(ChannelId=CHANNEL_1_ID)
    client2.start_channel(ChannelId=CHANNEL_2_ID)
    print("Event started")

def stop_service():
    print("Event stopping")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    client2 = get_medialive_client(CHANNEL_2_REGION)
    
    client1.stop_channel(ChannelId=CHANNEL_1_ID)
    client2.stop_channel(ChannelId=CHANNEL_2_ID)
    print("Event stopped")

def input_s3():
    print("Event switching to slate")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    client2 = get_medialive_client(CHANNEL_2_REGION)
    
    schedule_json = create_input_s3_json()
    client1.batch_update_schedule(ChannelId=CHANNEL_1_ID, **schedule_json)
    client2.batch_update_schedule(ChannelId=CHANNEL_2_ID, **schedule_json)

def input_live():
    print("Event switching to live")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    client2 = get_medialive_client(CHANNEL_2_REGION)
    
    schedule_json = create_input_live_json()
    client1.batch_update_schedule(ChannelId=CHANNEL_1_ID, **schedule_json)
    client2.batch_update_schedule(ChannelId=CHANNEL_2_ID, **schedule_json)

def ch1_pause():
    print("Pausing channel 1")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    
    schedule_json = create_pause_json()
    client1.batch_update_schedule(ChannelId=CHANNEL_1_ID, **schedule_json)

def ch1_unpause():
    print("Unpausing channel 1")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    
    schedule_json = create_unpause_json()
    client1.batch_update_schedule(ChannelId=CHANNEL_1_ID, **schedule_json)

def ch2_pause():
    print("Pausing channel 2")
    client1 = get_medialive_client(CHANNEL_2_REGION)
    
    schedule_json = create_pause_json()
    client1.batch_update_schedule(ChannelId=CHANNEL_2_ID, **schedule_json)

def ch2_unpause():
    print("Unpausing channel 2")
    client1 = get_medialive_client(CHANNEL_2_REGION)
    
    schedule_json = create_unpause_json()
    client1.batch_update_schedule(ChannelId=CHANNEL_2_ID, **schedule_json)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py {start|stop|input_s3|input_live|ch1_pause|ch2_pasue|ch1_unpause|ch2_unpause}")
        sys.exit(1)

    command = sys.argv[1]
    commands = {
        'start': start_service,
        'stop': stop_service,
        'input_s3': input_s3,
        'input_live': input_live,
        'ch1_pause': ch1_pause,
        'ch1_unpause': ch1_unpause,
        'ch2_pause': ch2_pause,
        'ch2_unpause': ch2_unpause,        
    }

    if command in commands:
        commands[command]()
    else:
        print("Invalid command. Use: start|stop|input_s3|input_live|ch1_pause|ch2_pasue|ch1_unpause|ch2_unpause")
        sys.exit(1)

if __name__ == "__main__":
    main()
