import pyglet
from numpy.random import shuffle, seed
from .parameters import SEED
from .core import World, AgentType, Core
from .visualization import WorldVisualizer, DataCollector as dc

seed(SEED)


class Simulation:
    def __init__(self, t_max=1000, quota=.99, c_size=(50, 50), initial_amount=1, **kwargs):
        self.world = World(c_size, quota, **kwargs) * initial_amount
        self.agents = {
            AgentType.HARVESTER: [],
            AgentType.INDUSTRIAL_A: [],
            AgentType.INDUSTRIAL_B: [],
            AgentType.CONSUMER: []}

        self.t_max = t_max
        self.time = 0

    def add_agent(self, agent):
        if agent not in self.agents:
            self.agents[agent.type].append(agent)

    def do(self):
        # Renew resources
        self.world.renew()

        # Deciding from top to bottom
        shuffle(self.agents[AgentType.HARVESTER])
        for harvester in self.agents[AgentType.HARVESTER]:
            harvester.decide()
            dc.add_private(harvester)

        for consumer in self.agents[AgentType.CONSUMER]:
            consumer.decide()
            dc.add_private(consumer)

        for industrial_b in self.agents[AgentType.INDUSTRIAL_B]:
            industrial_b.decide()
            dc.add_private(industrial_b)

        for industrial_a in self.agents[AgentType.INDUSTRIAL_A]:
            industrial_a.decide()
            dc.add_private(industrial_a)

        for harvester in self.agents[AgentType.HARVESTER]:
            harvester.decide()
            dc.add_private(harvester)

        Core.process_requests()

    def loop(self, plot=True):
        for i in range(self.t_max):
            self.do()

        if plot:
            dc.plot_em_all()
            dc.pickle_em_all()


class VisualSimulation(Simulation):
    def __init__(self, freq=.01, t_max=10, quota=.99, width=600, height=600, c_size=(50, 50), initial_amount=1, **kwargs):
        super(VisualSimulation, self).__init__(t_max, quota, c_size, initial_amount, **kwargs)
        self.visualizer = WorldVisualizer(self.world, width, height, frequency=freq)

    def run(self):
        self._schedule()
        pyglet.app.run()

    def _schedule(self):
        pyglet.clock.schedule_interval(self._do, self.visualizer.frequency)

    def _do(self, delta_t):
        """Main-loop instructions."""
        self.visualizer.draw()
        if not self.visualizer.paused:
            self.do()
            self.time += 1

        if self.time >= self.t_max:
            pyglet.app.exit()
            dc.plot_em_all()
            dc.pickle_em_all()
