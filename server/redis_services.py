import boto3
from botocore.exceptions import ClientError, NoRegionError

from uvicorn.config import logger

from .environment import REDIS_HOST, REDIS_LOCAL_PORT


class ElastiCache_Api_client():

    def get_host_port(self):
        try:
            client = boto3.client('elasticache')
            response = client.describe_cache_clusters(
                MaxRecords=10,
                ShowCacheNodeInfo=True,
                ShowCacheClustersNotInReplicationGroups=True,
            )
            url = response.CacheClusters[0].CacheNodes[0].Endpoint.Address
            port = response.CacheClusters[0].CacheNodes[0].Endpoint.Port
            return (url, port)
        except ClientError as e:
            logger.error(e)
            logger.error(f'Trying local connection - Connecting to HOST: {REDIS_HOST}, PORT: {REDIS_LOCAL_PORT}')
            return (REDIS_HOST, REDIS_LOCAL_PORT)
        except NoRegionError as e:
            logger.error(e)
            return (REDIS_HOST, REDIS_LOCAL_PORT)
