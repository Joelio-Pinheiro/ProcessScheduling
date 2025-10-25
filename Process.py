
# Estrutura de dados para um processo
class Process:
    def __init__(self, pid, arrival, burst, priority):
        self.pid = pid              # Processo P1, P2, ...
        self.arrival = arrival      # Tempo de chegada em segundos
        self.burst = burst          # Tempo de execução em segundos
        self.priority = priority    # Prioridade estática do processo
        self.reset()
        
    def reset(self):
        self.remaining = self.burst             # Tempo restante para execução
        self.start_time = None                  # Tempo de início da execução
        self.finish_time = None                 # Tempo de conclusão da execução
        self.waiting_time = 0                   # Tempo de espera do processo
        self.turnaround_time = None             # Tempo de resposta do processo
        self.dynamic_priority = self.priority   # Prioridade dinâmica (pode mudar)
        
    def get_info(self):
        return f"PID: {self.pid}, Arrival: {self.arrival}, Burst: {self.burst}, Priority: {self.priority}"


