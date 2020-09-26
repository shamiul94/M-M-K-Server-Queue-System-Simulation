#!/home/heisenberg/anaconda3/bin/python

"""
The task is to simulate an M/M/k system with a single queue.
Complete the skeleton code and produce results for three experiments.
The study is mainly to show various results of a queue against its ro parameter.
ro is defined as the ratio of arrival rate vs service rate.
For the sake of comparison, while plotting results from simulation, also produce the analytical results.
"""

import enum
import heapq
import random

import matplotlib.pyplot as plt


# Using enum class create enumerations
class ServerState(enum.IntEnum):
    BUSY = 1
    IDLE = 0


# Parameters


class Params:
    def __init__(self, lambd, mu, k, timeLimit=10000):
        self.lambd = lambd  # interarrival rate
        self.mu = mu  # service rate
        self.k = k
        self.timeLimit = timeLimit
    # Note lambd and mu are not mean value, they are rates i.e. (1/mean)


# Write more functions if required


# States and statistical counters
class States:
    def __init__(self):
        # States
        self.queue = []  # just stores the arrival times
        # Declare other states variables that might be needed
        self.totalDelay = 0.0
        self.totalServed = 0
        # Statistics
        self.util = 0.0
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0
        self.totalServingTime = 0.0

        self.timeOfLastEvent = 0.0
        self.timePassedSinceLastEvent = 0.0

        self.queueArea = 0.0

        # My added variables
        self.serverUtilizationFactor = 0.0
        self.serverStatus = ServerState.IDLE
        self.peopleInQueue = 0

        self.serverAvailableRightNow = 0

    def update(self, sim, event):
        # Complete this function
        self.timePassedSinceLastEvent = event.eventTime - self.timeOfLastEvent
        # print(self.timePassedSinceLastEvent)
        self.timeOfLastEvent = event.eventTime

        # lastEventServingTime = int(self.serverStatus) * self.timePassedSinceLastEvent
        # print(int(self.serverStatus))
        self.totalServingTime += (
                self.timePassedSinceLastEvent *
                (
                        (sim.params.k - self.serverAvailableRightNow) / sim.params.k
                )
        )

        # print(self.peopleInQueue)
        areaToBeAdded = self.peopleInQueue * self.timePassedSinceLastEvent
        self.queueArea += areaToBeAdded

    def finish(self, sim):
        # Complete this function
        if self.totalServed != 0:
            self.avgQdelay = self.totalDelay / self.totalServed
        else:
            self.avgQdelay = 0.0
            print('Average delay could not be calculated as divisor totalServed can not be 0.')

        self.avgQlength = self.queueArea / sim.now()

        # utilization factor
        self.util = self.totalServingTime / sim.now()

    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        print('############### Experimental Results #################')
        print(f'Results: lambda = {sim.params.lambd}, mu = {sim.params.mu}, k = {sim.params.k}')
        print(f'Total Customer Served: {self.totalServed}')
        print(f'Average Queue Length: {self.avgQlength}')
        print(f'Average Queue Delay: {self.avgQdelay}')
        print(f'Server Utilization Factor: {self.util}')
        print('######################################################')

    def getResults(self, sim):
        return self.avgQlength, self.avgQdelay, self.util


# Write more functions if required


class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None

    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType


class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim

    def process(self, sim):
        # Complete this function
        # initiate the first arrival event
        nextArrivalEventTime = self.eventTime + random.expovariate(sim.params.lambd)
        sim.scheduleEvent(ArrivalEvent(nextArrivalEventTime, sim))

        # push the exit event too.
        sim.scheduleEvent(ExitEvent(sim.params.timeLimit, sim))


class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        # Complete this function
        print('This is an EXIT event. Time: ', self.eventTime)


class ArrivalEvent(Event):
    # Write __init__ function
    def __init__(self, eventTime, sim):
        super().__init__(sim)
        self.eventType = 'ARRIVAL'
        self.sim = sim
        self.eventTime = eventTime

    def process(self, sim):
        # Complete this function
        # this customer has not arrived yet. he will come after 'random.expovariate(sim.params.lambd)'
        # time later than now.

        # Scheduling next arrival before processing current arrival event
        nextArrivalEventTime = sim.now() + random.expovariate(sim.params.lambd)
        sim.scheduleEvent(ArrivalEvent(nextArrivalEventTime, sim))  # scheduling next arrival event

        # process current arrival event now
        if sim.states.serverAvailableRightNow > 0:  # at least one server is idle
            # no delay except service delay
            sim.states.serverAvailableRightNow -= 1
            currentEventServiceDuration = random.expovariate(sim.params.mu)
            currentEventDepartureTime = sim.now() + currentEventServiceDuration

            sim.states.totalServed += 1
            sim.states.serverStatus = ServerState.BUSY

            currentEventDelay = 0
            sim.states.totalDelay += currentEventDelay

            sim.scheduleEvent(DepartureEvent(currentEventDepartureTime, sim))

        else:  # No server is idle
            sim.states.peopleInQueue += 1
            sim.states.queue.append(sim.now())


class DepartureEvent(Event):
    # Write __init__ function
    def __init__(self, eventTime, sim):
        super().__init__(sim)
        self.sim = sim
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'

    def process(self, sim):
        # Complete this function
        if len(sim.states.queue) == 0:
            sim.states.serverStatus = ServerState.IDLE
            sim.states.serverAvailableRightNow += 1
            sim.states.serverAvailableRightNow = min(sim.states.serverAvailableRightNow, sim.params.k)
        else:
            nextDepartureEventTime = sim.now() + random.expovariate(sim.params.mu)
            sim.scheduleEvent(DepartureEvent(nextDepartureEventTime, sim))

            currentEventDelay = sim.now() - sim.states.queue[0]
            sim.states.totalDelay += currentEventDelay

            sim.states.totalServed += 1

            sim.states.peopleInQueue -= 1
            sim.states.queue.pop(0)


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

        self.states.serverAvailableRightNow = params.k

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

            # print(event.eventTime, 'Event', event)
            self.simclock = event.eventTime
            event.process(self)

        self.states.finish(self)

    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)

    def print_analytical_results(self):
        avg_q_len = (self.params.lambd * self.params.lambd) / (self.params.mu * (self.params.mu - self.params.lambd))

        avg_delay_in_q = self.params.lambd / (self.params.mu * (self.params.mu - self.params.lambd))

        server_util_factor = self.params.lambd / self.params.mu

        print("\n################### Analytical Results #######################")
        print("lambda = %lf, mu = %lf" % (self.params.lambd, self.params.mu))
        print("Average queue length", round(avg_q_len, 3))
        print("Average delay in queue", round(avg_delay_in_q, 3))
        print("Server utilization factor", round(server_util_factor, 3))


def experiment1():
    seed = 101
    sim = Simulator(seed)
    sim.configure(Params(5.0 / 60, 8.0 / 60, 1), States())
    sim.run()
    sim.printResults()
    sim.print_analytical_results()


def experiment2():
    seed = 110
    mu = 1000.0 / 60
    ratios = [u / 10.0 for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []

    for ro in ratios:
        sim = Simulator(seed)
        sim.configure(Params(mu * ro, mu, 1), States())
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
    server_quantity = 4
    lambd = 5.0 / 60
    mu = 8.0 / 60
    seed = 101

    avg_length = []
    avg_delay = []
    util = []

    servers = []
    for i in range(1, server_quantity + 1):
        servers.append(i)

    for i in range(1, server_quantity + 1):
        sim = Simulator(seed)
        sim.configure(Params(lambd, mu, i), States())

        sim.run()
        sim.printResults()
        sim.print_analytical_results()

        length, delay, utl = sim.getResults()
        avg_length.append(length)
        avg_delay.append(delay)
        util.append(utl)

    # plot
    plt.figure(1)
    plt.subplot(311)
    plt.plot(servers, avg_length)
    plt.xlabel('Server (k)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(servers, avg_delay)
    plt.xlabel('Server (k)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(servers, util)
    plt.xlabel('Server (k)')
    plt.ylabel('Util')

    plt.show()


def main():
    # experiment1()
    # experiment2()
    experiment3()


if __name__ == "__main__":
    main()
