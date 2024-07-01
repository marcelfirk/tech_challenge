# Exercício do Bichinho Virtual
import random
class bichinhoVirtual:
    def __init__(self,nome):
        self.nome = nome
        self._idade = 0
        self._felicidade = 100
        self._saude = 100
        self._alimentacao = 100
    def brincar(self):
        self._felicidade += 10
        if self._felicidade > 100:
            self._felicidade = 100
        print(f"\n{self.nome} brincou e sua felicidade agora é {self._felicidade}.")
    def comer(self):
        self._alimentacao += 10
        if self._alimentacao > 100:
            self._alimentacao = 100
        print(f"\n{self.nome} comeu e sua alimentacao agora é {self._alimentacao}.")
    def exercitar(self):
        self._saude += 10
        if self._saude > 100:
            self._saude = 100
        print(f"\n{self.nome} se exercitou e sua saude agora é {self._saude}.")
    def dormir(self):
        self._idade += 1
        self._felicidade -= random.randint(5,20)
        self._saude -= random.randint(5, 20)
        self._alimentacao -= random.randint(5, 20)
        print(f"\n{self.nome} dormiu e agora sua idade é {self._idade}.")
nome_bichinho = input("Olá! Digite o nome do seu bichinho virtual: ")
bichinho = bichinhoVirtual(nome_bichinho)
status = 0
while status == 0:
    opcao = input("\nO que você deseja fazer? B - Brincar; C - Comer; E - Exercitar; D - Dormir ")
    if opcao == "B":
        bichinho.brincar()
    elif opcao == "C":
        bichinho.comer()
    elif opcao == "E":
        bichinho.exercitar()
    elif opcao == "D":
        bichinho.dormir()
    else:
        print("\n Desculpe, não consegui identificar a ação. ")
    features = [bichinho._saude, bichinho._alimentacao, bichinho._felicidade]
    print(f"\n Status do {bichinho.nome}: \n Saúde: {bichinho._saude} \n Alimentacao: {bichinho._alimentacao} \n Felicidade: {bichinho._felicidade} \n")
    if bichinho._idade >= 10:
        print(f"O {bichinho.nome} se tornou um adulto e foi viver sua própria vida feliz, por você ter sido um bom dono com ele.")
        status = 1
    if min(features) <= 0:
        print(f"O {bichinho.nome} fugiu em busca de um dono mais responsável.")
        status = 1
print("\n Fim de jogo")