from collections import defaultdict, deque
from utils import Utils
from Process import Process

class Scheduling:
    def __init__(self, quantum=2, aging=0):
        self.processes = []
        self.quantum = quantum
        self.aging = aging

    def run_all_algorithms(self):
        algorithms = [
            ("First Come, First Served", self.FCFS),
            ("Shortest Job First", self.SJF),
            ("Shortest Remaining Time First", self.SRTF),
            ("Priority Sem Preempção", self.PriorityNonPreemptive),
            ("Priority com preempção", self.PriorityPreemptive),
            ("Round Robin", self.RoundRobin),
            ("Round Robin com Prioridade e Envelhecimento", self.RoundRobinPriorityAging)
        ]

        for name, func in algorithms:
            print("=" * 80)
            print(f"Executando: {name}\n")
            print("=" * 80)

            # Reseta os processos antes de cada simulação
            procs = self.get_processes()
            for p in procs:
                p.reset()

            # Executa o algoritmo
            try:
                timeline, cs = func()
                # Recalcula métricas e imprime
                self.compute_metrics(procs, timeline, cs)
            except Exception as e:
                print(f"Erro ao executar {name}: {e}")
            print("\n" + "-" * 80 + "\n")

    
    def compute_metrics(self, processes, timeline, cs):
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
        self.print_timeline(processes, timeline)

    def add_process(self, process):
        self.processes.append(process)
    def get_processes(self):
        return self.processes
    
    def print_timeline(self, processes, timeline):
        header = 'tempo '
        pids = [p.pid for p in sorted(processes, key=lambda x: int(x.pid[1:]))]
        header += ' '.join(pids)
        print(header)

        # Imprime a linha do tempo
        for t, (start, end, running) in enumerate(((i[0], i[1], i[2]) for i in timeline)):
            # mostra como '0- 1' ou '9-10'
            start_s = int(start)
            end_s = int(end)
            time_label = f"{start_s}-{end_s}"
            row = [time_label]
            for pid in pids:
                row.append('##' if running == pid else '--')
            print(' '.join(r.ljust(4) for r in row))

    # FCFS (First Come, First Served)
    def FCFS(self):
        procs = self.get_processes()
        for p in procs:
            p.reset()
        time = 0 # Tempo atual
        timeline = [] # Lista de tuplas (tempo_inicio, tempo_fim, pid)
        ready = deque() # Fila de prontos
        process_by_arrival = sorted(procs, key=lambda p: p.arrival) # Ordena por tempo de chegada
        idx = 0 # Indice para processos ordenados por chegada
        current_process = None # Processo em execução
        cs = 0 # Contador de trocas de contexto

        while True:
            # Adiciona processos que chegaram ao tempo atual na fila de prontos
            while idx < len(process_by_arrival) and process_by_arrival[idx].arrival <= time:
                ready.append(process_by_arrival[idx])
                idx += 1
            
            # Se não há processo em execução, pega o próximo da fila
            if current_process is None and ready:
                next_p = ready.popleft()
                # Faz a troca de contexto se necessario
                if timeline and timeline[-1][2] is not None and timeline[-1][2] != next_p.pid:
                    cs += 1
                current_process = next_p
                # Marca o tempo de início caso ainda não tenha sido marcado(sempre será o caso aqui)
                if current_process.start_time is None:
                    current_process.start_time = time
                
            if current_process:
                # Executa o processo atual
                timeline.append((time, time + 1, current_process.pid))
                current_process.remaining -= 1
                if current_process.remaining == 0: # Processo terminou
                    current_process.finish_time = time + 1
                    current_process = None
            else:
                timeline.append((time, time + 1, None)) # CPU ociosa
                
            time += 1 # Incrementa o tempo
            if current_process is None and idx >= len(process_by_arrival) and not ready:
                break # Sai se não há mais processos para executar
        # Retorna uma lista de tuplas representando a timeline(tempo_inicio, tempo_fim, pid) e o número de trocas de contexto
        return timeline, cs

    # Shortest Job First (SJF) - Não preemptivo
    def SJF(self):
        procs = self.get_processes()
        for p in procs:
            p.reset()
        time = 0 # Tempo atual
        timeline = [] # Lista de tuplas (tempo_inicio, tempo_fim, pid)
        ready = deque() # Fila de prontos
        process_by_arrival = sorted(procs, key=lambda p: p.arrival) # Ordena por tempo de chegada
        idx = 0 # Indice para processos ordenados por chegada
        current_process = None # Processo em execução
        cs = 0 # Contador de trocas de contexto
        
        while True: # percorre o tempo
            
            # Adiciona processos que chegaram ao tempo atual na fila de prontos
            while idx < len(process_by_arrival) and process_by_arrival[idx].arrival <= time:
                ready.append(process_by_arrival[idx])
                idx += 1
                
            if current_process is None and ready:
                # Seleciona o processo com o menor tempo de execução
                
                candidates = sorted(ready, key=lambda p: (p.burst, int(p.pid[1:])))
                next_p = candidates[0]
                ready.remove(next_p)
                # Faz a troca de contexto se necessario
                if timeline and timeline[-1][2] is not None and timeline[-1][2] != next_p.pid:
                    cs += 1
                current_process = next_p
                # Marca o tempo de início caso ainda não tenha sido marcado
                if current_process.start_time is None:
                    current_process.start_time = time
            if current_process:
                # Executa o processo atual
                timeline.append((time, time + 1, current_process.pid))
                current_process.remaining -= 1
                if current_process.remaining == 0: # Processo terminou
                    current_process.finish_time = time + 1
                    current_process = None
            else:
                timeline.append((time, time + 1, None)) # CPU ociosa
            time += 1
            if current_process is None and idx >= len(process_by_arrival) and not ready:
                # Sai se não há mais processos para executar
                break
        return timeline, cs
    
    # Shortest Remaning Time First - Shortest Job First Preemptivo
    def SRTF(self):
        procs = self.get_processes()
        for p in procs:
            p.reset()
        time = 0 # Tempo atual
        timeline = [] # Lista de tuplas (tempo_inicio, tempo_fim, pid)
        ready = deque() # Fila de prontos
        process_by_arrival = sorted(procs, key=lambda p: p.arrival) # Ordena por tempo de chegada
        idx = 0 # Indice para processos ordenados por chegada
        current_process = None # Processo em execução
        cs = 0 # Contador de trocas de contexto
        old_process = None # guarda o processo que estava em execução no ciclo anterior
        
        while True: # percorre o tempo
            
            # Adiciona processos que chegaram ao tempo atual na fila de prontos
            while idx < len(process_by_arrival) and process_by_arrival[idx].arrival <= time:
                ready.append(process_by_arrival[idx])
                idx += 1
                
            if current_process or ready:
                # Seleciona o processo com o menor tempo de execução
                
                candidates = ready.copy()
                if current_process:
                    candidates.append(current_process)

                next_p = Utils.break_tie(candidates, current_process) # desempata
                
                if old_process and next_p and old_process.pid != next_p.pid: # o proximo processo é diferente do atual
                    if old_process.remaining > 0:
                        ready.append(old_process)
                    cs+=1 # troca de contexto
                    
                # se trocou de contexto tirar o proximo processo da lista de prontos
                if next_p in ready:
                    ready.remove(next_p)
                current_process = next_p
                if current_process and current_process.start_time is None:
                    current_process.start_time = time

            if current_process:
                # Executa o processo atual
                timeline.append((time, time + 1, current_process.pid))
                old_process = current_process # guarda o processo atual antes de possivelmente ficar nulo
                current_process.remaining -= 1
                if current_process.remaining == 0: # Processo terminou
                    current_process.finish_time = time + 1
                    current_process = None
            else:
                timeline.append((time, time + 1, None)) # CPU ociosa
            time += 1
            if current_process is None and idx >= len(process_by_arrival) and not ready:
                # Sai se não há mais processos para executar
                break
        return timeline, cs

    # Por Prioridade (PS) - Cooperativo - Sem Preempção
    def PriorityNonPreemptive(self):
        procs = self.get_processes()
        for p in procs:
            p.reset()
        time = 0 # Tempo atual
        timeline = [] # Lista de tuplas (tempo_inicio, tempo_fim, pid)
        ready = deque() # Fila de prontos
        process_by_arrival = sorted(procs, key=lambda p: p.arrival) # Ordena por tempo de chegada
        idx = 0 # Indice para processos ordenados por chegada
        current_process = None # Processo em execução
        cs = 0 # Contador de trocas de contexto
        
        while True:
            # Adiciona processos que chegaram ao tempo atual na fila de prontos
            while idx < len(process_by_arrival) and process_by_arrival[idx].arrival <= time:
                ready.append(process_by_arrival[idx])
                idx += 1
            
            # Se não há processo em execução, pega o próximo da fila
            if current_process is None and ready:
                # Seleciona o processo com a maior prioridade (maior valor numérico)
                candidates = sorted(ready, key=lambda p: (-p.priority, int(p.pid[1:])))
                next_p = candidates[0]
                ready.remove(next_p)
                
                # Faz a troca de contexto se necessario
                if timeline and timeline[-1][2] is not None and timeline[-1][2] != next_p.pid:
                    cs += 1
                    
                current_process = next_p
                # Marca o tempo de início caso ainda não tenha sido marcado(sempre será o caso aqui)
                if current_process.start_time is None:
                    current_process.start_time = time
                
            if current_process:
                
                # Executa o processo atual
                timeline.append((time, time + 1, current_process.pid))
                current_process.remaining -= 1
                if current_process.remaining == 0: # Processo terminou
                    current_process.finish_time = time + 1
                    current_process = None
            else:
                timeline.append((time, time + 1, None)) # CPU ociosa
                
            time += 1 # Incrementa o tempo
            if current_process is None and idx >= len(process_by_arrival) and not ready:
                break # Sai se não há mais processos para executar
        # Retorna uma lista de tuplas representando a timeline(tempo_inicio, tempo_fim, pid) e o número de trocas de contexto
        return timeline, cs
            
    
    # Por Prioridade (PS) - Preemptivo
    def PriorityPreemptive(self):
        procs = self.get_processes()
        for p in procs:
            p.reset()
        time = 0 # Tempo atual
        timeline = [] # Lista de tuplas (tempo_inicio, tempo_fim, pid)
        ready = deque() # Fila de prontos
        process_by_arrival = sorted(procs, key=lambda p: p.arrival) # Ordena por tempo de chegada
        idx = 0 # Indice para processos ordenados por chegada
        current_process = None # Processo em execução
        cs = 0 # Contador de trocas de contexto
        old_process = None # guarda o processo que estava em execução no ciclo anterior
        
        while True: # percorre o tempo
            
            # Adiciona processos que chegaram ao tempo atual na fila de prontos
            while idx < len(process_by_arrival) and process_by_arrival[idx].arrival <= time:
                ready.append(process_by_arrival[idx])
                idx += 1
                
            if current_process or ready:
                candidates = ready.copy()
                
                if current_process:
                    candidates.append(current_process)

                highest_priority = max(p.priority for p in candidates) # maior valor de prioridade
                tied = [p for p in candidates if p.priority == highest_priority] # processos com a maior prioridade se só tiver um já é o escolhido
                
                if len(tied) == 1: # apenas um processo, para evitar chamada desnecessária do break_tie
                    next_p = tied[0]
                else:
                    next_p = Utils.break_tie_rr(tied, current_process) # desempata caso tenha mais de um com a mesma prioridade


                if old_process and next_p and old_process.pid != next_p.pid: # o proximo processo é diferente do atual
                    if old_process.remaining > 0:
                        ready.append(old_process)
                    cs+=1 # troca de contexto
                    
                # se trocou de contexto tirar o proximo processo da lista de prontos
                if next_p in ready:
                    ready.remove(next_p)
                current_process = next_p
                if current_process and current_process.start_time is None:
                    current_process.start_time = time

            if current_process:
                # Executa o processo atual
                timeline.append((time, time + 1, current_process.pid))
                old_process = current_process # guarda o processo atual antes de possivelmente ficar nulo
                current_process.remaining -= 1
                if current_process.remaining == 0: # Processo terminou
                    current_process.finish_time = time + 1
                    current_process = None
            else:
                timeline.append((time, time + 1, None)) # CPU ociosa
            time += 1
            if current_process is None and idx >= len(process_by_arrival) and not ready:
                # Sai se não há mais processos para executar
                break
        return timeline, cs
    
    # Round Robin (RR) - Preemptivo com Quantum e sem Prioridade
    def RoundRobin(self):
        procs = self.get_processes()
        for p in procs:
            p.reset()
        time = 0 # Tempo atual
        timeline = [] # Lista de tuplas (tempo_inicio, tempo_fim, pid)
        ready = deque() # Fila de prontos
        process_by_arrival = sorted(procs, key=lambda p: p.arrival) # Ordena por tempo de chegada
        idx = 0 # Indice para processos ordenados por chegada
        current_process = None # Processo em execução
        cs = 0 # Contador de trocas de contexto
        
        timeslice = 0 # Contador do tempo do quantum para o processo atual
        
        
        while True: # percorre o tempo
            
            # Adiciona processos que chegaram ao tempo atual na fila de prontos
            while idx < len(process_by_arrival) and process_by_arrival[idx].arrival <= time:
                ready.append(process_by_arrival[idx])
                idx += 1
                
            if current_process is None and ready:
                current_process = ready.popleft()
                timeslice = min(self.quantum, current_process.remaining) # reinicia o tempo do quantum
                
                if current_process.start_time is None: # se ainda não foi marcado o tempo de início
                    current_process.start_time = time

                if timeline and timeline[-1][2] is not None and timeline[-1][2] != current_process.pid:
                    cs += 1 # troca de contexto

            if current_process:
                # Executa o processo atual
                timeline.append((time, time + 1, current_process.pid))
                current_process.remaining -= 1
                timeslice -= 1
                if current_process.remaining == 0: # Processo terminou
                    current_process.finish_time = time + 1
                    current_process = None
                    timeslice = 0
                elif timeslice == 0: # Quantum esgotado, preempção
                    ready.append(current_process) # coloca o atual de volta no final da fila
                    current_process = None
                    # cs += 1 # troca de contexto
            else:
                timeline.append((time, time + 1, None)) # CPU ociosa
            time += 1
            if current_process is None and idx >= len(process_by_arrival) and not ready:
                # Sai se não há mais processos para executar
                break
        return timeline, cs   
    
    
    # Round Robin (RR) - Com prioridade e envelhecimento
    def RoundRobinPriorityAging(self):
        procs = self.get_processes()
        for p in procs:
            p.reset()
        time = 0 # Tempo atual
        timeline = [] # Lista de tuplas (tempo_inicio, tempo_fim, pid)
        process_by_arrival = sorted(procs, key=lambda p: p.arrival) # Ordena por tempo de chegada
        idx = 0 # Indice para processos ordenados por chegada
        current_process = None # Processo em execução
        cs = 0 # Contador de trocas de contexto
        
        timeslice = 0 # Contador do tempo do quantum para o processo atual
        prio_levels = defaultdict(deque) # filas de prontos por nível de prioridade
        old_process = None # guarda o processo que estava em execução no ciclo anterior
        
        
        while True: # percorre o tempo
            # Adiciona processos que chegaram ao tempo atual na fila
            while idx < len(process_by_arrival) and process_by_arrival[idx].arrival <= time:
                p = process_by_arrival[idx]
                prio_levels[p.dynamic_priority].append(p)
                idx += 1

            prefer_candidate = None # candidato preferencial para desempate

            # apenas troca quando o quantum é esgotado ou não tem processo em execução
            if current_process is None or timeslice == 0: # segue a regra de não ter preempção por prioridade

                if timeslice == 0 and current_process and current_process.remaining > 0: # apenas se o processo atual não terminou
                    
                    # envelhece os processos na fila de prontos antes de re-enfileirar o processo atual
                    if self.aging > 0:
                        all_ready_procs = []
                        for prio in list(prio_levels.keys()):
                            all_ready_procs.extend(prio_levels.pop(prio))
                            
                        for p in all_ready_procs:
                            p.dynamic_priority = max(1, p.dynamic_priority - self.aging)
                            prio_levels[p.dynamic_priority].append(p)

                    # o processo atual volta para a fila de prontos
                    prio_levels[current_process.dynamic_priority].append(current_process)
                    prefer_candidate = current_process 
                    current_process = None # CPU fica livre para a re-seleção

                # Se a CPU está livre ou o quantum esgotou, escolhe o próximo processo a executar
                next_p = self.choose_next(prio_levels, prefer_candidate)

                if next_p: 
                    if old_process is not None and old_process.pid != next_p.pid: 
                        cs += 1 # troca de contexto

                    current_process = next_p
                    timeslice = min(self.quantum, current_process.remaining) # reinicia o tempo do quantum
                    
                    if current_process.start_time is None: # se ainda não foi marcado o tempo de início
                        current_process.start_time = time
                
            if current_process:
                # Executa o processo atual
                timeline.append((time, time + 1, current_process.pid))
                current_process.remaining -= 1
                timeslice -= 1
                old_process = current_process # guarda o processo atual antes de possivelmente ficar nulo

                if current_process.remaining == 0:
                    current_process.finish_time = time + 1
                    current_process = None
                    timeslice = 0
            else:
                timeline.append((time, time + 1, None))
                # Aplica envelhecimento aos processos em espera
                if self.aging > 0:
                    all_ready_procs = []
                    for prio in list(prio_levels.keys()):
                        all_ready_procs.extend(prio_levels.pop(prio))
                        
                    for p in all_ready_procs:
                        p.dynamic_priority = max(1, p.dynamic_priority - self.aging)
                        prio_levels[p.dynamic_priority].append(p)
            time += 1
            if current_process is None and idx >= len(process_by_arrival) and not any(len(q) for q in prio_levels.values()):
                break
        return timeline, cs
    
    def choose_next(self, prio_levels, prefer_current_candidate=None):
    
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
        next = Utils.break_tie_rr(candidates, prefer_current_candidate)

        if next:
            # remove o processo escolhido da fila de prontos
            prio_levels[next.dynamic_priority].remove(next)
            return next

        return None