import os
from cloudflare import Cloudflare
from dotenv import load_dotenv
import requests
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

## Create Cloudflare Client
client = Cloudflare(
    api_email= os.environ.get("CLOUDFLARE_EMAIL"),
    api_key= os.environ.get("CLOUDFLARE_API_KEY"),
)

def get_domains_to_process():
    """
    Returns a list of domains for which the script should update the DNS records
    from the CLOUDFLARE_DOMAINS environment variable. The domains should be
    comma-separated in the variable.
    """
    return os.environ.get("CLOUDFLARE_DOMAINS").split(",")

def get_public_ip():
    """
    Makes a GET request to https://checkip.amazonaws.com and returns the result as a string, stripped of whitespace.
    If the request fails for any reason, returns None.
    """
    try:
        response = requests.get('https://checkip.amazonaws.com')
        if response.status_code == 200:
            return response.text.strip();
    except requests.RequestException:
        return Exception("No account found in this email")

def get_zone(domain_name):
    """
    Lists all DNS records for a specific domain using the Cloudflare API.
    """
    try:
        zones = client.zones.list(name = domain_name)
        if zones.has_next_page:
            return zones._get_page_items()[0]
        else:
            raise Exception("No zone found for domain: {domain_name}")
    except Exception as e:
       logger.error(f"Error listing DNS records: {str(e)}")
       raise Exception(f"Error listing DNS records: {str(e)}")

def update_dns_record(domain, actual_ip):
    """
    Updates a DNS record for the specified domain with the specified actual_ip.

    Args:
    domain (str): The domain name for which the DNS record should be updated.
    actual_ip (str): The actual IP address that the DNS record should be set to.

    Returns:
    None
    """
    try:
        zone = get_zone(domain)
        dns_records = client.dns.records.list(zone_id=zone.id, type="A")

        ## Only first type A domain shall be updated. If you have more that 1 type A domain this won't work for your sorry.
        if dns_records.has_next_page:
            dns_record = dns_records._get_page_items()[0]
        
        if dns_record.content != actual_ip:
            logger.info(f"Updating DNS record for {domain} ({dns_record.content}) to {actual_ip}")
            client.dns.records.update(zone_id=zone.id, dns_record_id=dns_record.id, content=actual_ip, name=dns_record.name, type=dns_record.type)
            logger.info(f"DNS record for {domain} updated!")
        else:
            logger.info(f"DNS record for {domain} is already up to date")
    except Exception as e:
        logger.error(f"Error updating DNS records for {domain}: {str(e)}")

## Main function``
if __name__ == '__main__':
    actual_public_ip = get_public_ip()
    
    for domain in get_domains_to_process():
        update_dns_record(domain, actual_public_ip)