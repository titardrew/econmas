import sys
from simulation import VisualSimulation, new_local_agent, AgentType

if __name__ == "__main__":
    try:
        size = int(sys.argv[1])
    except:
        size = 50

    h = VisualSimulation(c_size=(size, size))

    harvester1 = new_local_agent(AgentType.HARVESTER, h.world, (10, 10))
    harvester2 = new_local_agent(AgentType.HARVESTER, h.world, (11, 11))
    harvester3 = new_local_agent(AgentType.HARVESTER, h.world, (12, 12))
    harvester4 = new_local_agent(AgentType.HARVESTER, h.world, (12, 12))

    industrial_a1 = new_local_agent(AgentType.INDUSTRIAL_A, h.world, (10, 10))
    industrial_a2 = new_local_agent(AgentType.INDUSTRIAL_A, h.world, (13, 13))
    industrial_a3 = new_local_agent(AgentType.INDUSTRIAL_A, h.world, (13, 13))

    industrial_b1 = new_local_agent(AgentType.INDUSTRIAL_B, h.world, (11, 11))
    industrial_b2 = new_local_agent(AgentType.INDUSTRIAL_B, h.world, (11, 11))
    industrial_b3 = new_local_agent(AgentType.INDUSTRIAL_B, h.world, (11, 11))

    consumer1 = new_local_agent(AgentType.CONSUMER, h.world, (10, 10), 1)
    consumer2 = new_local_agent(AgentType.CONSUMER, h.world, (10, 10), 1)
    consumer3 = new_local_agent(AgentType.CONSUMER, h.world, (10, 10), 1)
    consumer4 = new_local_agent(AgentType.CONSUMER, h.world, (10, 10), 1)

    # h.add_agent(harvester1)
    h.add_agent(harvester2)
    # h.add_agent(harvester3)
    # h.add_agent(harvester4)

    h.add_agent(industrial_a1)
    # h.add_agent(industrial_a2)
    # h.add_agent(industrial_a3)

    h.add_agent(industrial_b1)
    # h.add_agent(industrial_b2)
    # h.add_agent(industrial_b3)

    h.add_agent(consumer1)

    h.run()
