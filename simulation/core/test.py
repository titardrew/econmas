from simulation.core import Harvester, World
import numpy as np


def test_world():
    map_ = np.array([[1, 2, 3],
                     [4, 5, 6],
                     [7, 8, 9]])

    w = World((3, 3), amount=map_)

    # Neighbourhood test
    nb1, nb2 = Harvester.get_neighbours((2, 2)), Harvester.get_neighbours((1, 1))
    assert np.allclose([w.tor_item(nb) for nb in nb1], [7, 3, 8, 6])
    assert np.allclose([w.tor_item(nb) for nb in nb2], [6, 8, 4, 2])

    # Dist test
    assert w.dist((2, 0), (0, 6)) == 1
    assert w.dist((0, 0), (2, 0)) == 1
    assert w.dist((0, 0), (1, 1)) == 2

test_world()