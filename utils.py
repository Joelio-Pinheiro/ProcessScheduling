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

    # Selecionar entre os candidatos (desempatar)
    # candidates: lista de processos
    # prefer_current: processo que está atualmente em execução ou nenhum
    # Ordem de preferencia: 
        # (1) o processo ques está em execução 
        # (2) o processo com menor tempo restante de processamento
        # (3) Escolhe aleatoriamente entre os processos com menor tempo restante iguais
    @staticmethod
    def break_tie(candidates, prefer_current):

        if not candidates: # não possui candidatos
            return None
        
        # if prefer_current and prefer_current in candidates: 
            # return prefer_current

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
        # (1) o processo ques está em execução 
        # (2) o processo com menor tempo restante de processamento
        # (3) Escolhe aleatoriamente entre os processos com menor tempo restante iguais
    @staticmethod
    def break_tie_rr(candidates, prefer_current):

        if not candidates: # não possui candidatos
            return None
        
        if prefer_current and prefer_current in candidates: # caso 1 caso o processo atual esteja entre os candidatos
            return prefer_current

        min_remaining = min(p.remaining for p in candidates) # caso 2 pega o com menor tempo
        tied = [p for p in candidates if p.remaining == min_remaining] # pega os candidatos com o menor tempo iguais
        
        # caso 3 retorna um aleatório caso tenha mais de um, se não retorna fixo o com menor tempo(lista de tamanho 1)
        return random.choice(tied) 