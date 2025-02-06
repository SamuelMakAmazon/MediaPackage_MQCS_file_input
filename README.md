# MediaPackage_MQCS_file

## Overview

Set up a test environment for cross region MQCS failover using file input and MediaLive Single pipeline.

## Prerequisites

Ensure your awscli, boto3, botocore supports MQCS. Please upgrade to the latest if it it not supported. 

```bash
pip install --upgrade boto3 botocore awscli
```

## CloudFormation

Channel A: `1-EMP.yaml`  
Channel B: `2-EMP_CF.yaml`

### Deployment Steps

1. Deploy `1-EMP.yaml` in region 1
   - Configure "S3FilePathA" and "S3FilePathB" where PathA is the slate input and PathB is the prod input
   - Once the CloudFormation has deployed, select Outputs tab and drop down "MediaPackageDomain"

2. Deploy `2-EMP_CF.yaml` in region 2
   - Configure "S3FilePathA" and "S3FilePathB" where PathA is the slate input and PathB is the prod input
   - Keep channel group, channel name and endpoint name identical between regions
   - Copy the "MediaPackageDomain" from region 1 to "EgressDomainChannel1"

3. Enable MQCS in MediaPackage
   - CloudFormation currently does not support MQCS. MQCS has to be configured manually: 
   
   Method 1: via script
   1. Modify the emp_mqcs.py script
   ```python
   regions = ['ap-northeast-1', 'ap-northeast-3']
   channel_group_id = 'gp1'
   channel_id = 'ch1'
   ```
   1. Enable MQCS in MediaPackage channel
   ```
   python3 ./emp_mqcs.py
   ```

   Method 2: via Console
   1. Navigate to MediaPackage > Channel groups > gp1 > ch1 > select edit
   2. Enable "Enable input switch based on MQCS" and "Enable MQCS publishing in Common Media Server Data (CMSD)"
   3. Select "Update"
   4. Repeat the steps in region 2

4. Get the CloudFront endpoint
   - Copy the MediaPackageV2HLS from CloudFormation Output
   - Find the CF domain name in the CF distributions

## Before Testing

### Endpoints
- Endpoint 1 (primary): `https://AAAAAAA.egress.iv3jd8.mediapackagev2.ap-northeast-1.amazonaws.com/out/v1/gp1/ch1/cmaf/index.m3u8`
- Endpoint 2: `https://BBBBBBBBB.mediapackagev2.ap-northeast-3.amazonaws.com/out/v1/gp1/ch1/cmaf/index.m3u8`
- CF: `https://XXXXXXXX.cloudfront.net/out/v1/gp1/ch1/cmaf/index.m3u8`

### Testing Script

The script uses boto3 for testing: `switch_script.py`

### Usage
```bash
python script.py {start|stop|input_s3|input_live|ch1_pause|ch2_pasue|ch1_unpause|ch2_unpause}
```

### Configuration
Before using the script, modify the channel ids and regions:
```python
CHANNEL_1_ID = '7528721'
CHANNEL_1_REGION = 'ap-northeast-1'
CHANNEL_2_ID = '3320982'
CHANNEL_2_REGION = 'ap-northeast-3'
```

## Test Cases

1. Start channels:
```bash
python3 script.py start
```

2. Playback Setup
   - Use HLS player: https://hls-js-c682795c-032a-4c39-9374-225b776c04f6.netlify.app/demo/
   - Open Developer tab, right click on the name and select Response headers
   - Select "Manage Header Columns"
   - Add custom headers:
     - "cmsd-static"
     - "x-amzn-mediapackage-active-input"
   - Now you can monitor when failover occurs

3. Switch to prod file input:
   ```bash
   python3 script.py input_live
   ```
   - After 30s, both channels switch to the prod file input

4. Test Channel 1 Failover
   ```bash
   python3 script.py ch1_pause
   ```
   Expected behavior:
   - Video stream should switch from Channel 1 to Channel 2

5. Restore Channel 1
   ```bash
   python3 script.py ch1_unpause
   ```
   Expected behavior:
   - Video stream should switch back from Channel 2 to Channel 1
