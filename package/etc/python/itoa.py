from pyrate_limiter import RedisBucket, RequestRate, Duration
from requests import Session
from requests_cache import CacheMixin, RedisCache
from requests_ratelimiter import LimiterMixin

import json
import logging
import sys, traceback
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


try:
    import syslogng

    logger = syslogng.Logger()
except ImportError:
    log_format = logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(log_format)
    logger.addHandler(handler)


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    """Session class with caching and rate-limiting behavior. Accepts arguments for both
    LimiterSession and CachedSession.
    """


class entities:
    def init(self, options):
        # 'host', "`SC4S_ITOA_HOST`",
        #     'port', "`SC4S_ITOA_PORT`",
        #     'verify', "`SC4S_ITOA_TLS_VERIFY`",
        #     'token', "`SC4S_ITOA_AUTH_TOKEN`"
        host = os.getenv(f"SC4S_ITOA_HOST", "")
        if host == "":
            raise Exception("ITOA Invalid Host")

        port = os.getenv(f"SC4S_ITOA_PORT", "8089")

        token = os.getenv(f"SC4S_ITOA_AUTH_TOKEN", "")
        if token == "":
            raise Exception("ITOA Invalid Token")

        logger.debug("Init itoa")
        self.session = CachedLimiterSession(
            per_second=int(os.getenv(f"SC4S_ITOA_LIMIT_PER_SEC", "60")),
            cache_name="itoa_cache",
            backend="sqlite",
            expire_after=int(os.getenv(f"SC4S_ITOA_TTL", "600")),
            logger=logger,
            match_headers=False,
            stale_if_error=True,
        )

        if os.getenv(f"SC4S_ITOA_TLS_VERIFY", "yes") in [
            "true",
            "1",
            "t",
            "y",
            "yes",
        ]:
            self.verify = True
        else:
            self.verify = False

        self.url = (
            f"https://{host}:{port}/servicesNS/nobody/SA-ITOA/itoa_interface/entity"
        )
        self.headers = {
            "Authorization": f"Bearer {token}",
            "user-agent": "sc4s/1.0 (itoa)",
        }
        return True

    def deinit(self):
        pass

    def parse(self, log_message):
        # try to resolve the IP address
        try:
            ip = log_message["SOURCEIP"].decode("utf-8")
            host = log_message["HOST"].decode("utf-8")
            logger.debug(f"checking for {host},{ip}")
            response = self.session.request(
                "GET",
                self.url,
                timeout=10,
                params={
                    "fields": "title,entity_type_ids,sc4s_vendor_product,host",
                    "filter": f'{{"$or": [{{"host": "{host}"}},{{"host": "{ip}"}}]}}',
                },
                headers=self.headers,
                verify=self.verify,
            )

            logger.debug(f"result={response.text}")

            entities = json.loads(response.text)
            if len(entities) > 0:
                entity = entities[0]
                log_message["HOST"] = entity["title"]
                if "sc4s_vendor_product" in entity:
                    vp_key = entity["sc4s_vendor_product"][0]
                    for vp in entity["sc4s_vendor_product"]:
                        if len(vp) < len(vp_key):
                            vp_key = vp
                    log_message[".netsource.sc4s_vendor_product"] = entity[
                        "sc4s_vendor_product"
                    ][vp_key]

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            er = "".join("!! " + line for line in lines)  # Log it or whatever here
            logger.error(f"ITOA exception\n{er}")
        # return True, other way message is dropped
        return True


if __name__ == "__main__":
    # execute only if run as a script
    options = {}
    ef = entities()
    ef.init(options)
    lm = {}
    lm["HOST"] = "vserver".encode("utf-8")
    lm["SOURCEIP"] = "10.136.153.117".encode("utf-8")
    ef.parse(lm)
    print(lm)
    ef.deinit()
