import boto3

class Route53Updater(object):
    def __init__(self):
        # クライアント初期化
        self.client = boto3.client('route53', region_name="us-east-1")

    def update_a_record(self, host="", domain="", ttl=300, addr=""):
        # hosted_zoneのid取得
        name = domain if host == "" else host + "." + domain
        hosted_zones = self.client.list_hosted_zones_by_name(DNSName=name)["HostedZones"]
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
        self.client.change_resource_record_sets(
            HostedZoneId = hosted_zone_id,
            ChangeBatch = change_batch
        )

    def list_resource_record_set(self, host="", domain=""):
        name = domain if host == "" else host + "." + domain
        hosted_zones = self.client.list_hosted_zones_by_name(DNSName=name)["HostedZones"]
        return hosted_zones
