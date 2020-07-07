#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import jmespath
import os,sys
import config
import subprocess
import logging
from concurrent.futures import ProcessPoolExecutor
from prometheus_client.core import GaugeMetricFamily
sys.path.append(os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def get_expiry_map_list():
    ex_cls = ExpiryData()
    domain_expiry_data = ex_cls.daemon_get_expiry_map()
    return domain_expiry_data


class ExpiryData:

    def __init__(self):
        conf = config.Config()
        self.domains = conf.domains
        self.timeout = 300 #default seconds
        self.port = 8800  #default port listen
        self.debug = False  #default
        self.log_dir = 'log'  #default dir
        self.log_file = 'ssl-monitor.log' #default file
        try:
            self.interval = self.general['interval']
        except Exception as e:
            pass
        try:
            self.debug = self.general['debug']
        except Exception as e:
            pass
        try:
            self.port = self.general['port']
        except Exception as e:
            pass
        try:
            self.log_dir = self.general['log_dir']
        except Exception as e:
            pass
        try:
            self.log_file = self.general['log_file']
        except Exception as e:
            pass


    def __get_expiry_seconds_from_domain__(self,domain_map):
        domain_ex = _get_expiry_seconds_from_domain(domain_map['host'],domain_map['port'])
        return domain_ex

    def daemon_get_expiry_map(self):
        ex_list = []
        with ProcessPoolExecutor() as pool:
            if self.domains and len(self.domains) > 0:
                for _host_,_expiry_ in zip(self.domains,pool.map(self.__get_expiry_seconds_from_domain__,self.domains)):
                    try:
                        ex_map = dict()
                        ex_map['host'] = _host_['host']
                        ex_map['port'] = _host_['port']
                        ex_map['expiry'] = _expiry_
                        ex_list.append(ex_map)
                        logging.info(f'ssl-cert-monitor : {ex_map}')
                    except Exception as e:
                        logging.error('[get_expiry_map] error : %s' % e)
                        pass
        return ex_list


class ExportToPrometheus:

    def format_metric_name(self):
        """
        :desc: ssl_cert_expiry_seconds
        :demo: ssl_cert_expiry_seconds{host="www.8btc.com", port=443}=6666
        :demo: ssl_cert_expiry_seconds{host="www.chainnode.com", port=443}=3456
        """
        return "ssl_cert_expiry_seconds"

    def collect_data_metric(self,expiry_map):
        if expiry_map and len(expiry_map) > 0:
            for expiry_items in expiry_map:
                avg_gauge = GaugeMetricFamily(self.format_metric_name(),'check SSL certificate expiration dates ',
                                              labels=['host','port'])
                labels = [str(jmespath.search(k,expiry_items)) for k in ['host','port']]
                value = jmespath.search('expiry',expiry_items)
                if value > 0:
                    # value = "".join(filter(str.isdigit,value))
                    avg_gauge.add_metric(labels=labels,value=value)
                else:
                    yield self.metric_up_gauge(self.format_metric_name())
                yield avg_gauge

    def metric_up_gauge(self,resource: str, succeeded=True):
        metric_name = resource + '_up'
        description = 'Did the {} fetch succeed.'.format(resource)
        return GaugeMetricFamily(metric_name, description, value=int(succeeded))

    def collect(self):
        expiry_map_data = get_expiry_map_list()
        if len(expiry_map_data) > 0 :
            # print(list(self.collect_data_metric(expiry_map_data)))
            yield from self.collect_data_metric(expiry_map_data)



def _get_expiry_seconds_from_domain(host, port = 443):
    now = int(time.time())
    opssl_command = "echo |openssl s_client -servername %s -connect %s:%d 2>/dev/null | openssl x509 -noout -dates|awk -F '=' '/notAfter/{print $2}'" % (host,host,port)
    command = f'date +%s -d "$({opssl_command})"'
    expiry_seconds = 0
    try:
        sub_res = subprocess.run(command, timeout=150, encoding='utf-8', stdout=subprocess.PIPE, shell=True)
        _expiry_ = int(sub_res.stdout)
        expiry_seconds = _expiry_ - now
        # logger.info('host %s ,expiry_seconds: %d' % (host,expiry_seconds))
    except Exception as e:
        logging.error(f'command {command} get error {e}')
    return expiry_seconds

