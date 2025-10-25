import sys
import random
from Process import Process

class Utils:
    @staticmethod
    def readConfig(path="./config"): # Caminho padrão para o arquivo de configuração
        quantum = 2
        aging = 0
        try:
            with open(path, 'r') as file: # Abre o arquivo de configuração
                # Tenta ler o quantum e aging do arquivo se der erro retorna os valores padrão
                for line in file:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if key == "quantum":
                        quantum = int(value)
                    elif key == "aging":
                        aging = int(value)
        except Exception:
            pass # Usa os valores padrão se ocorrer algum erro
        return quantum, aging
    
    @staticmethod
    def readProcessesStdin(): # Lê processos do stdin pelo terminal ou por redirecionamento de arquivo
        procs = []
        pid = 1 # Contador do PID
        for line in sys.stdin: # Lê cada linha do stdin e cria um processo se for valido
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 3:
                continue
            arrival = int(parts[0])
            burst = int(parts[1])
            priority = int(parts[2])

            # cria e adiciona na lista
            procs.append((f'P{pid}', arrival, burst, priority))
            pid += 1
        return procs
    
    @staticmethod
    def compute_metrics(processes, timeline, cs):
        # calcula turnaround e waiting times
        total_turnaround = 0
        total_waiting = 0
        n = len(processes)

        for p in processes:
            turnaround = p.finish_time - p.arrival
            waiting = turnaround - p.burst
            total_turnaround += turnaround
            total_waiting += waiting

        avg_turnaround = total_turnaround / n if n > 0 else 0
        avg_waiting = total_waiting / n if n > 0 else 0

        print(f"\nTempo médio de vida (Turnaround Time): {avg_turnaround:.2f}")
        print(f"Tempo médio de espera (Waiting Time): {avg_waiting:.2f}")
        print(f"Número de trocas de contexto: {cs}\n")

        print(f"\nTimeline: ")
        Utils.printTimeline(processes, timeline)
        
    @staticmethod
    def printTimeline(processes, timeline):
        col_width = 6  # seta o espaço das colunas

        # Cabeçalho
        pids = [p.pid for p in sorted(processes, key=lambda x: int(x.pid[1:]))]
        header = f"{'tempo'.ljust(col_width)}" + ''.join(pid.center(col_width) for pid in pids)
        print(header)

        # Corpo da timeline
        for start, end, running in timeline:
            time_label = f"{int(start)}-{int(end)}".ljust(col_width)
            row = [time_label]
            for pid in pids:
                row.append(('##' if running == pid else '--').center(col_width))
            print(''.join(row))
    
    # Escolhe o proximo processo no Round Robin com 
    @staticmethod
    def chooseNext(prio_levels, prefer_current_candidate=None):

        all_ready_procs = []
        # pega todos os processos prontos em uma lista
        for q in prio_levels.values():
            all_ready_procs.extend(list(q))
             
        if not all_ready_procs: # se não houver ninguem na fila retorna None
            return None
            
        # pega a menor prioridade dinâmica entre os processos prontos
        best_prio = min(p.dynamic_priority for p in all_ready_procs)
        
        # filtra os processos que possuem menor prioridade dinâmica
        candidates = [p for p in all_ready_procs if p.dynamic_priority == best_prio]
        
        # usa o metodo de desempate para escolher entre os candidatos 
        next = Utils.breakTie(candidates, prefer_current_candidate)

        if next:
            # remove o processo escolhido da fila de prontos
            prio_levels[next.dynamic_priority].remove(next)
            return next

        return None

    # Selecionar entre os candidatos (desempatar)
    # candidates: lista de processos
    # prefer_current: processo que está atualmente em execução ou nenhum
    # Ordem de preferencia: 
        # (1) o processo ques está em execução e está entre os com menor tempo restante
        # (2) o processo com menor tempo restante de processamento
        # (3) Escolhe aleatoriamente entre os processos com menor tempo restante iguais
    @staticmethod
    def breakTieSRTF(candidates, prefer_current):

        if not candidates: # não possui candidatos
            return None
        
        min_remaining = min(p.remaining for p in candidates) # caso 2 pega o com menor tempo
        tied = [p for p in candidates if p.remaining == min_remaining] # pega os candidatos com o menor tempo iguais
        
        # caso 1 caso o processo atual esteja entre os com menor tempo
        if prefer_current and prefer_current in tied: 
            return prefer_current 

        # caso 3 retorna um aleatório caso tenha mais de um, se não retorna fixo o com menor tempo(lista de tamanho 1)
        return random.choice(tied) 

    # Selecionar entre os candidatos (desempatar)
    # candidates: lista de processos
    # prefer_current: processo que está atualmente em execução ou nenhum
    # Ordem de preferencia: 
        # (1) o processo que está em execução não importa se está entre os com menor tempo restante
        # (2) o processo com menor tempo restante de processamento
        # (3) Escolhe aleatoriamente entre os processos com menor tempo restante iguais
    @staticmethod
    def breakTie(candidates, prefer_current):

        if not candidates: # não possui candidatos
            return None
        
        if prefer_current and prefer_current in candidates: # caso 1 caso o processo atual esteja entre os candidatos
            return prefer_current

        min_remaining = min(p.remaining for p in candidates) # caso 2 pega o com menor tempo
        tied = [p for p in candidates if p.remaining == min_remaining] # pega os candidatos com o menor tempo iguais
        
        # caso 3 retorna um aleatório caso tenha mais de um, se não retorna fixo o com menor tempo(lista de tamanho 1)
        return random.choice(tied) 