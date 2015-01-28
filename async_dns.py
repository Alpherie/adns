#!/usr/bin/python3
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# Asynchronous DNS Resolution. v1.0.
#
# Read more about this code at:
# http://www.catonmat.net/blog/asynchronous-dns-resolution
#
#Redone and modified for python 3 by Alpherie (alpherie@yandex.ru)
#

import copy
import adns
from time import time

class AsyncResolver(object):
    def __init__(self, hosts, intensity=100):
        """
        hosts: a list of hosts to resolve
        intensity: how many hosts to resolve at once
        """
        self.hosts = hosts
        self.intensity = intensity
        self.adns = adns.init()
        self.in_progress = False
        self.hosts_are_added = False

    def add_hosts(self, more_hosts):
        """ Adding more hosts during resolving"""
        if self.in_progress:
            self.hosts_are_added = True
            self.added_hosts = more_hosts
        else:
            self.hosts.extend(more_hosts)

    def resolve_partially(clear = False):
        """ Get resolving result dict during the process,
may be useful for threaded programms
"""
        if clear:
            the_dict = copy.copy(self.resolved_hosts)
            self.resolved_hosts = {}
            return the_dict
        else:
            return copy.copy(self.resolved_hosts)
    
    def resolve(self):
        """ Resolves hosts and returns a dictionary of { 'host': 'ip' }. """
        self.in_progress = True
        self.resolved_hosts = {}
        resolved_hosts = self.resolved_hosts
        active_queries = {}
        host_queue = self.hosts[:]

        def collect_results():
            for query in self.adns.completed():
                answer = query.check()
                host = active_queries[query]
                del active_queries[query]
                if answer[0] == 0:
                    ip = answer[3][0]
                    resolved_hosts[host] = ip
                elif answer[0] == 101: # CNAME
                    query = self.adns.submit(answer[1], adns.rr.A)
                    active_queries[query] = host
                else:
                    resolved_hosts[host] = None

        def finished_resolving():
            return len(resolved_hosts) == len(self.hosts)

        while not finished_resolving():
            while host_queue and len(active_queries) < self.intensity:
                if self.hosts_are_added:
                    host_queue.extend(self.added_hosts)
                host = host_queue.pop()
                query = self.adns.submit(host, adns.rr.A)
                active_queries[query] = host
            collect_results()

        self.in_progress = False
        return resolved_hosts


if __name__ == "__main__":
    host_format = "www.host%d.com"
    number_of_hosts = 10

    hosts = [host_format % i for i in range(number_of_hosts)]

    ar = AsyncResolver(hosts, intensity=500)
    start = time()
    resolved_hosts = ar.resolve()
    end = time()

    print ("It took %.2f seconds to resolve %d hosts." % (end-start, number_of_hosts))

