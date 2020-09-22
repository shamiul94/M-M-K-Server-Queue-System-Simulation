"""
The task is to simulate an M/M/k system with a single queue.
Complete the skeleton code and produce results for three experiments.
The study is mainly to show various results of a queue against its ro parameter.
ro is defined as the ratio of arrival rate vs service rate.
For the sake of comparison, while plotting results from simulation, also produce the analytical results.
"""

import heapq
import random
import matplotlib.pyplot as plt

from enum import Enum
import math
import numpy.random as rand


class Status(Enum):
    BUSY = 0
    IDLE = 1


class Customer:
    def __init__(self, arrival_time):
        self.arrival_time = arrival_time
        self.delay_in_queue = None
        self.service_time = None


# Parameters
class Params:
    def __init__(self, lambd, mu, k):
        self.lambd = lambd
        self.mu = mu
        self.k = k


# States and statistical counters
class States:
    def __init__(self):
        #self.server_status = Status.IDLE
        self.number_of_servers_busy = 0
        self.total_utilization = 0.0
        self.total_queue_area = 0.0
        self.total_delay = 0.0
        self.last_event_time = 0.0

        # States
        self.queue = []

        # Statistics
        self.util = 0.0
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0

    def update(self, sim, event):
        if event.eventType == 'ARRIVAL':
            sim.states.total_queue_area += (event.eventTime - sim.states.last_event_time) * len(sim.states.queue)
            sim.states.total_utilization += (event.eventTime - sim.states.last_event_time) * (sim.states.number_of_servers_busy / sim.params.k)
        elif event.eventType == 'DEPARTURE':
            sim.states.served += 1
            sim.states.total_utilization += (event.eventTime - sim.states.last_event_time) * (sim.states.number_of_servers_busy / sim.params.k)
            if len(sim.states.queue) == 0:
                None
            else:
                sim.states.total_queue_area += (event.eventTime - sim.states.last_event_time) * len(sim.states.queue)
                arrival_time_of_this_person = sim.states.queue.pop()
                sim.states.total_delay += event.eventTime - arrival_time_of_this_person
        else:
            print('Unknown eventType to update')

    def finish(self, sim):
        if self.last_event_time != 0:
            self.util = self.total_utilization / self.last_event_time
            self.avgQlength = self.total_queue_area / self.last_event_time

        if self.served != 0:
            self.avgQdelay = self.total_delay / self.served

    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        print('MMk Results: lambda = %lf, mu = %lf, k = %d' % (sim.params.lambd, sim.params.mu, sim.params.k))
        print('MMk Total customer served: %d' % (self.served))
        print('MMk Average queue length: %lf' % (self.avgQlength))
        print('MMk Average customer delay in queue: %lf' % (self.avgQdelay))
        print('MMk Time-average server utility: %lf' % (self.util))

    def getResults(self, sim):
        return (self.avgQlength, self.avgQdelay, self.util)


class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None

    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType

    def __lt__(self, other):
        return self.eventTime < other.eventTime


class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim

    def process(self, sim):
        sim.scheduleEvent(ArrivalEvent(sim.now() + sim.get_random(sim.params.lambd), sim))
        sim.scheduleEvent(ExitEvent(10, sim))
        sim.states.last_event_time = self.eventTime


class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        sim.states.last_event_time = self.eventTime


class ArrivalEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim

    def process(self, sim):
        # rand or random ekta use korlei hobe
        sim.scheduleEvent(ArrivalEvent(sim.now() + sim.get_random(sim.params.lambd), sim))

        if sim.states.number_of_servers_busy >= sim.params.k:
            sim.states.queue.append(self.eventTime)
        else:
            sim.states.number_of_servers_busy += 1
            sim.scheduleEvent(DepartureEvent(sim.now() + sim.get_random(sim.params.lambd), sim))

        sim.states.last_event_time = self.eventTime


class DepartureEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'
        self.sim = sim

    def process(self, sim):

        if len(sim.states.queue) == 0:
            sim.states.number_of_servers_busy -= 1
        else:
            sim.scheduleEvent(DepartureEvent(sim.now() + sim.get_random(sim.params.mu), sim))

        sim.states.last_event_time = self.eventTime


class Simulator:
    def __init__(self, seed):
        self.eventQ = []
        self.simclock = 0
        self.seed = seed
        self.params = None
        self.states = None

    def initialize(self):
        self.simclock = 0
        self.scheduleEvent(StartEvent(0, self))

    def configure(self, params, states):
        self.params = params
        self.states = states

    def now(self):
        return self.simclock

    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))

    def run(self):
        random.seed(self.seed)
        self.initialize()

        while len(self.eventQ) > 0:
            time, event = heapq.heappop(self.eventQ)

            if event.eventType == 'EXIT':
                break

            if self.states != None:
                self.states.update(self, event)

            print(event.eventTime, 'Event', event)
            self.simclock = event.eventTime
            event.process(self)

        self.states.finish(self)

    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)

    def get_random(self, arrival_or_departure_rate):
        return - math.log(rand.uniform(0, 1)) / arrival_or_departure_rate


def experiment1():
    seed = 101
    sim = Simulator(seed)
    sim.configure(Params(5.0 / 60, 8.0 / 60, 1), States())
    sim.run()
    sim.printResults()


def experiment2(k):
    seed = 110
    mu = 1000.0 / 60
    ratios = [u / 10.0 for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []

    for ro in ratios:
        sim = Simulator(seed)
        sim.configure(Params(mu * ro, mu, k), States())
        sim.run()

        length, delay, utl = sim.getResults()
        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl)

    plt.figure(1)
    plt.subplot(311)
    plt.plot(ratios, avglength)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(ratios, avgdelay)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(ratios, util)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Util')

    plt.show()


def experiment3():
    # Similar to experiment2 but for different values of k; 1, 2, 3, 4
    # Generate the same plots
    for x in range(1, 5):
        experiment2(x)


def main():

    experiment1()
    # experiment2()
    experiment3()


if __name__ == "__main__":
    main()
