from main import load_population, population_size, issues
import fitness
from negotiationGenerator.scenario import Scenario
from negotiationGenerator.discreteGenerator import build_negotiation_scenario
from negotiation import generate_simulations, simulate_local_negotiations, process_results

from mpi4py import MPI

import csv

refinement_cycles = 10

if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    print(f"Rank {rank}, Size {size}")

    if rank == 0:
        populations = {
            "accommodating": load_population(population_size, fitness.accommodating, "accommodating"),
            "collaborating": load_population(population_size, fitness.collaborating, "collaborating"),
            "compromising": load_population(population_size, fitness.compromising, "compromising"),
            "avoiding": load_population(population_size, fitness.avoiding, "avoiding"),
            "competing": load_population(population_size, fitness.competing, "competing")
        }
        headers = ["Cycle"]
        for population_name in populations:
            for population_name_2 in populations:
                headers.append(f"Fitness_{population_name}_vs_{population_name_2}")
        for stat in ["Accepts", "Rejects", "Time"]:
            for population_name in populations:
                active = False
                for population_name_2 in populations:
                    if population_name_2 == population_name:
                        active = True
                    if active:
                        headers.append(f"{stat}_{population_name}_vs_{population_name_2}")
        headers.append("Cycle_Time")
        csv_file = open("refinement.csv", "w", newline="")
        csv_writer = csv.writer(csv_file, dialect='excel')
        csv_writer.writerow(headers)

    for cycle in range(refinement_cycles):
        simulations = None
        if rank == 0:
            scenario: Scenario = build_negotiation_scenario(issues)
            all_simulations = generate_simulations(populations, scenario)
            simulations = all_simulations
        simulations = comm.bcast(simulations, root=0)
        local_simulation_results = simulate_local_negotiations(simulations, rank, size)
        simulation_results = comm.gather(local_simulation_results, root=0)
        if rank == 0:
            simulation_results = [item for sublist in simulation_results for item in sublist]  # Flatten results
            simulation_stats = process_results(populations, all_simulations, simulation_results)
            csv_row = [cycle]
            for matrix in simulation_stats:
                csv_row.extend([value for value in matrix.values()])
            csv_writer.writerow(csv_row)
            print(f"Cycle {cycle} done")

    if rank == 0:
        csv_file.close()
        for population_name in populations:
            populations[population_name].sort(key=lambda agent: agent.fitness)
            populations[population_name][-1].model.save(f"models/{population_name}.keras")
