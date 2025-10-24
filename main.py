from utils import Utils
from Scheduling import Scheduling
from Process import Process
import sys

def main():
    
    print("Iniciando o simulador")
    quantum, aging = Utils.readConfig()
    print(f"Quantum: {quantum}, Aging: {aging}")
    
    processes = Utils.readProcessesStdin()
    if not processes:
        print("Nenhum processo lido. Forneça processos no stdin no formato: [tempo de chegada] [tempo de execução] [prioridade]")
        sys.exit(1)
    for proc in processes:
        print(f"  {proc}")
    
    scheduling = Scheduling(quantum=quantum, aging=aging)

    for proc in processes:
        scheduling.add_process(Process(proc[0], proc[1], proc[2], proc[3]))

    # Executa os algoritmos de escalonamento
    scheduling.run_all_algorithms()


if __name__ == "__main__":
    main()