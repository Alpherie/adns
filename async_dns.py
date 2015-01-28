#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# Asynchronous DNS Resolution. v1.0.
#
# Read more about this code at:
# http://www.catonmat.net/blog/asynchronous-dns-resolution
#

import sys
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

    def resolve(self, output_file):
        """ Resolves hosts and writes result to file """
        global resolved_hosts
        resolved_hosts = 0 #it is a counter
        global successfully_resolved_hosts
        successfully_resolved_hosts = 0
        active_queries = {}
        host_queue = self.hosts[:]

        def collect_results():
            for query in self.adns.completed():
                global resolved_hosts
                answer = query.check()
                host = active_queries[query]
                del active_queries[query]
                if answer[0] == 0:
                    ip = answer[3][0]
                    global successfully_resolved_hosts
                    successfully_resolved_hosts += 1
                    resolved_hosts += 1
                    output_file.write(host + ' resolved to ' + str(ip))
                elif answer[0] == 101: # CNAME
                    query = self.adns.submit(answer[1], adns.rr.A)
                    active_queries[query] = host
                else:
                    output_file.write(host + ' could not be resolved')
                    resolved_hosts = resolved_hosts + 1

        def finished_resolving():
            global resolved_hosts
            return resolved_hosts == len(self.hosts)

        while not finished_resolving():
            while host_queue and len(active_queries) < self.intensity:
                host = host_queue.pop()
                query = self.adns.submit(host, adns.rr.A)
                active_queries[query] = host
            collect_results()

        return successfully_resolved_hosts


if __name__ == "__main__":
    try:
        input_file = open(sys.argv[1], 'r')
    except IndexError:
        print 'Input file name incorrect!'
        sys.exit()
    try:
        output_file = open(sys.argv[2], 'w')
    except IndexError:
        print 'Output file name incorrect!'
        sys.exit()

    try:
        intensity = int(sys.argv[3])
        print 'Using intensity = %d' % (intensity)
    except (IndexError, ValueError):
        print 'Using default intensity = 500'
        intensity = 500

    hosts = [line.replace('\n', '') for line in input_file.readlines()]
    #hosts = [line for line in input_file.readlines()]
    global resolved_hosts
    resolved_hosts = 0

    ar = AsyncResolver(hosts, intensity=intensity)
    start = time()
    successfully_resolved_hosts = ar.resolve(output_file)
    output_file.close()
    end = time()

    print "It took %.2f seconds to resolve %d hosts.\n%d hosts were resolved successfully\n" % (end-start, resolved_hosts, successfully_resolved_hosts)

