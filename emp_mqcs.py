import boto3
import sys
import time
import json

# Configuration
regions = ['ap-northeast-1', 'ap-northeast-3']  # Add your regions
channel_group_id = 'gp1'  # Your channel group ID
channel_id = 'ch1'  # Your channel ID

def enable_mqcs_for_channel(channel_group_id, channel_id, region):
    """
    Enable MQCS for a specific MediaPackage channel
    """
    try:
        # Create MediaPackage client
        client = boto3.client('mediapackagev2', region_name=region)

        update_params = {
            'ChannelGroupName': channel_group_id,
            'ChannelName': channel_id,
            'InputSwitchConfiguration': {
                'MQCSInputSwitching': True
            },
            'OutputHeaderConfiguration': {
                'PublishMQCS': True
            }

        }

        # Update the channel
        response = client.update_channel(**update_params)
        
        print(f"Successfully enabled MQCS for channel {channel_id} in {region}")
        return True

    except Exception as e:
        print(f"Error enabling MQCS for channel {channel_id} in {region}: {str(e)}")
        return False

def main():


    # Enable MQCS in all regions
    for region in regions:
        print(f"\nProcessing region: {region}")
        success = enable_mqcs_for_channel(channel_group_id, channel_id, region)
        
        if not success:
            print(f"Failed to enable MQCS in {region}")
            continue
        
        # Wait a few seconds between regions
        time.sleep(2)

if __name__ == "__main__":
    main()
