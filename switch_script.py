import boto3
import json
from datetime import datetime, timedelta
import sys

# Configuration
CHANNEL_1_ID = ['5833484','1963187', '283907']
CHANNEL_1_REGION = 'us-west-2'
CHANNEL_2_ID = ['6401052','3124197', '9681417']
CHANNEL_2_REGION = 'us-east-1'
INPUT_1 = "slate"
INPUT_2 = "prod"

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
    print("Event start action")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    client2 = get_medialive_client(CHANNEL_2_REGION)

    print(f"Region: {CHANNEL_1_REGION}")    
    for channel_id in CHANNEL_1_ID:
        try:
            print(f"Starting channel 1 ID: {channel_id}")
            client1.start_channel(ChannelId=channel_id)
        except Exception as e:
            print(f"Error starting channel 1 ID {channel_id}: {str(e)}")

    print(f"Region: {CHANNEL_2_REGION}")  
    for channel_id in CHANNEL_2_ID:
        try:
            print(f"Starting channel 2 ID: {channel_id}")
            client2.start_channel(ChannelId=channel_id)
        except Exception as e:
            print(f"Error starting channel 2 ID {channel_id}: {str(e)}")
    print("Event starting")

def stop_service():
    print("Event stop action")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    client2 = get_medialive_client(CHANNEL_2_REGION)

    print(f"Region: {CHANNEL_1_REGION}") 
    for channel_id in CHANNEL_1_ID:
        try:
            print(f"Stopping channel 1 ID: {channel_id}")
            client1.stop_channel(ChannelId=channel_id)
        except Exception as e:
            print(f"Error stopping channel 1 ID {channel_id}: {str(e)}")

    print(f"Region: {CHANNEL_2_REGION}")      
    for channel_id in CHANNEL_2_ID:
        try:
            print(f"Stopping channel 2 ID: {channel_id}")
            client2.stop_channel(ChannelId=channel_id)
        except Exception as e:
            print(f"Error stopping channel 2 ID {channel_id}: {str(e)}")
    print("Event stopping")

def input_s3():
    print("Event switching to slate")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    client2 = get_medialive_client(CHANNEL_2_REGION)
    
    schedule_json = create_input_s3_json()
    print(f"Region: {CHANNEL_1_REGION}")
    for channel_id in CHANNEL_1_ID:
        try:
            print(f"Switching channel 1 ID {channel_id} to slate")
            client1.batch_update_schedule(ChannelId=channel_id, **schedule_json)
        except Exception as e:
            print(f"Error switching channel 1 ID {channel_id}: {str(e)}")
    
    print(f"Region: {CHANNEL_2_REGION}") 
    for channel_id in CHANNEL_2_ID:
        try:
            print(f"Switching channel 2 ID {channel_id} to slate")
            client2.batch_update_schedule(ChannelId=channel_id, **schedule_json)
        except Exception as e:
            print(f"Error switching channel 2 ID {channel_id}: {str(e)}")

def input_live():
    print("Event switching to live")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    client2 = get_medialive_client(CHANNEL_2_REGION)
    
    schedule_json = create_input_live_json()
    print(f"Region: {CHANNEL_1_REGION}")
    for channel_id in CHANNEL_1_ID:
        try:
            print(f"Switching channel 1 ID {channel_id} to live")
            client1.batch_update_schedule(ChannelId=channel_id, **schedule_json)
        except Exception as e:
            print(f"Error switching channel 1 ID {channel_id}: {str(e)}")
    
    print(f"Region: {CHANNEL_2_REGION}") 
    for channel_id in CHANNEL_2_ID:
        try:
            print(f"Switching channel 2 ID {channel_id} to live")
            client2.batch_update_schedule(ChannelId=channel_id, **schedule_json)
        except Exception as e:
            print(f"Error switching channel 2 ID {channel_id}: {str(e)}")

def ch1_pause():
    print("Pausing channel 1")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    
    schedule_json = create_pause_json()
    try:
        first_channel = CHANNEL_1_ID[0]  # Get only the first channel ID
        print(f"Pausing channel 1 ID: {first_channel} in region: {CHANNEL_1_REGION}")
        client1.batch_update_schedule(ChannelId=first_channel, **schedule_json)
    except Exception as e:
        print(f"Error pausing channel 1 ID {first_channel} in region {CHANNEL_1_REGION}: {str(e)}")

def ch1_unpause():
    print("Unpausing channel 1")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    
    schedule_json = create_unpause_json()
    try:
        first_channel = CHANNEL_1_ID[0]  # Get only the first channel ID
        print(f"Pausing channel 1 ID: {first_channel} in region: {CHANNEL_1_REGION}")
        client1.batch_update_schedule(ChannelId=first_channel, **schedule_json)
    except Exception as e:
        print(f"Error pausing channel 1 ID {first_channel} in region {CHANNEL_1_REGION}: {str(e)}")

def ch2_pause():
    print("Pausing channel 2")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    
    schedule_json = create_pause_json()
    try:
        first_channel = CHANNEL_1_ID[1]  # Get only the first channel ID
        print(f"Pausing channel 2 ID: {first_channel} in region: {CHANNEL_1_REGION}")
        client1.batch_update_schedule(ChannelId=first_channel, **schedule_json)
    except Exception as e:
        print(f"Error pausing channel 2 ID {first_channel} in region {CHANNEL_1_REGION}: {str(e)}")

def ch2_unpause():
    print("Unpausing channel 2")
    client1 = get_medialive_client(CHANNEL_1_REGION)
    
    schedule_json = create_unpause_json()
    try:
        first_channel = CHANNEL_1_ID[1]  # Get only the first channel ID
        print(f"Pausing channel 2 ID: {first_channel} in region: {CHANNEL_1_REGION}")
        client1.batch_update_schedule(ChannelId=first_channel, **schedule_json)
    except Exception as e:
        print(f"Error pausing channel 2 ID {first_channel} in region {CHANNEL_1_REGION}: {str(e)}")

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
