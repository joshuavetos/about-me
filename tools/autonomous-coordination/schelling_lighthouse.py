import numpy as np
import scipy.ndimage as ndimage

class LighthouseAgent:
    """
    Autonomous Coordination Agent:
    Achieves zero-communication rendezvous via Multi-Scale Saliency.
    Designed for Jammed/Fog-of-War environments.
    """
    def __init__(self, agent_id, world_size=100, view_dist=25):
        self.agent_id = agent_id
        self.world_size = world_size
        self.view_dist = view_dist

    def get_lighthouse_signal(self, global_terrain, current_pos):
        """
        The 'Squint' Mechanism:
        Detects low-frequency structural energy beyond the immediate fog.
        """
        r, c = current_pos
        # Observe a larger radius with heavy blurring to find macro-features
        macro_dist = self.view_dist * 2 
        r0, r1 = max(0, r-macro_dist), min(self.world_size, r+macro_dist)
        c0, c1 = max(0, c-macro_dist), min(self.world_size, c+macro_dist)
        
        view = global_terrain[r0:r1, c0:c1]
        
        # Saliency on the blurred view (Macro-Feature Detection)
        # Sigma=5 removes local 'noise' and highlights the global peak
        macro_features = ndimage.gaussian_filter(view, sigma=5)
        
        local_idx = np.unravel_index(np.argmax(macro_features), macro_features.shape)
        return (local_idx[0] + r0, local_idx[1] + c0)

    def hunt(self, global_terrain, start_pos, iterations=20):
        """
        Iterative convergence loop. 
        Moves toward the center of mass of structural uniqueness.
        """
        curr = np.array(start_pos)
        for _ in range(iterations):
            target = np.array(self.get_lighthouse_signal(global_terrain, tuple(curr)))
            direction = target - curr
            dist = np.linalg.norm(direction)
            
            if dist < 1.0: 
                break
            
            # Step size of 8 to bridge information dead zones
            step = (direction / dist) * 8
            curr = (curr + step).astype(int)
            curr = np.clip(curr, 0, self.world_size - 1)
        return tuple(curr)

def run_coordination_test():
    """Execution Bench for Verification"""
    np.random.seed(42)
    # Generate noisy world
    world = ndimage.gaussian_filter(np.random.normal(0, 1, (100, 100)), sigma=2)
    # The Global Schelling Point (Singularity)
    world[50, 50] += 100.0 

    agents = [LighthouseAgent(i) for i in range(3)]
    spawns = [(5, 5), (95, 95), (5, 95)]
    final_landings = []

    print("--- VETOS COORDINATION: LIGHTHOUSE PROTOCOL ---")
    for i, agent in enumerate(agents):
        end_pos = agent.hunt(world, spawns[i])
        final_landings.append(end_pos)
        print(f"Agent {i} | Spawn: {spawns[i]} | Final: {end_pos}")

    # Success Threshold
    success = all(np.linalg.norm(np.array(p) - np.array(final_landings[0])) < 3 for p in final_landings)
    print("-" * 30)
    print(f"COORDINATION STATUS: {'SUCCESS' if success else 'FAILURE'}")

if __name__ == "__main__":
    run_coordination_test()
