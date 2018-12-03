import boto3

class Route53Updater(object):
    def __init__(self):
        pass

    def update_a_record(self, host="", domain="", ttl=300, addr=""):
        # クライアント初期化
        client = boto3.client('route53', region_name="us-east-1")

        # hosted_zoneのid取得
        hosted_zones = client.list_hosted_zones()["HostedZones"]
        hosted_zone_id = [i["Id"] for i in hosted_zones if i["Name"] == domain][0]

        # changebatch作成
        change_batch = {
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain if host == "" else host + "." + domain,
                        'Type': 'A',
                        'TTL': ttl,
                        'ResourceRecords': [
                            {'Value': addr}
                        ]
                    }
                }
            ]
        }

        # レコード更新
        client.change_resource_record_sets(
            HostedZoneId = hosted_zone_id,
            ChangeBatch = change_batch
        )
