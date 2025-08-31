from collections import Counter
import math


class VigenereCipher():
    def __init__(self, key: str, alphabet: str = "abcdefghijklmnopqrstuvwxyz"):
        self.key = key.lower()
        self.alphabet = alphabet.lower()

    def encode(self, text: str) -> str:
        encoded_chars = []
        for i, char in enumerate(text):
            if char in self.alphabet:
                # Aqui usa módulo para gerar o keystream.
                # Quando i excede o tamanho da chave retorna para o inicio da chave
                # e assim por diante independente do tamanho da mensagem.
                # Ignora espaços vazios nesse caso.
                key_char = self.key[i % len(self.key)]

                # Usa uma lógica parecida com o key_char.
                # A cifra se baseia em somar os indices da letra da mensagem e da letra da chave e deslocar pelo alfabeto;
                # Por exemplo: se a letra da mensagem for 'n' (indice 13) e a letra da chave for 'y' (indice 24), o resultado será 'h' (indice 11), pois dá a volta no alfabeto informado.
                # Deslocando o número de posições do indice da chave.
                # Somando os indices: 13 + 24 = 37 % 26 = 11
                # A tabela é apenas uma referência para entender como a cifra funciona.

                encoded_index = (self.alphabet.index(char) + self.alphabet.index(key_char)) % len(self.alphabet)
                # print("Divisão: " + str(self.alphabet.index(char)) + " + " + str(self.alphabet.index(key_char)) + " % " + str(len(self.alphabet)) + " = " + str(encoded_index))
                # print("LETRA = " + self.alphabet[encoded_index])
                encoded_chars.append(self.alphabet[encoded_index])
        return ''.join(encoded_chars)
    
    def decode(self, text: str) -> str:
        decoded_chars = []
        for i, char in enumerate(text):
            if char in self.alphabet:
                # Exata mesma lógica para keystream
                key_char = self.key[i % len(self.key)]

                # Essa lógica é o inverso da de encode, só volta no deslocamento. Ao subtrair chega-se na letra original
                decoded_index = (self.alphabet.index(char) - self.alphabet.index(key_char)) % len(self.alphabet)
                decoded_chars.append(self.alphabet[decoded_index])
        return ''.join(decoded_chars)

class BreakCypher():
    def __init__(self, language, method="Kasiski", limit=20):
        self.language = language
        self.freq = {}
        self.load_frequency_table(language)

    def load_frequency_table(self, language):
        if language == "pt":
            self.freq = dict(sorted({
                'a': 0.1463, 'b': 0.0104, 'c': 0.0388, 'd': 0.0499, 'e': 0.1257,
                'f': 0.0102, 'g': 0.0130, 'h': 0.0128, 'i': 0.0618, 'j': 0.0040,
                'k': 0.0002, 'l': 0.0278, 'm': 0.0474, 'n': 0.0505, 'o': 0.1073,
                'p': 0.0252, 'q': 0.0120, 'r': 0.0653, 's': 0.0781, 't': 0.0434,
                'u': 0.0463, 'v': 0.0167, 'w': 0.0001, 'x': 0.0021, 'y': 0.0001,
                'z': 0.0047
            }.items(), key=lambda item: item[1], reverse=True))
        elif language == "en":
            self.freq = dict(sorted({
                'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253, 'e': 0.12702,
                'f': 0.02228, 'g': 0.02015, 'h': 0.06094, 'i': 0.06966, 'j': 0.00153,
                'k': 0.00772, 'l': 0.04025, 'm': 0.02406, 'n': 0.06749, 'o': 0.07507,
                'p': 0.01929, 'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
                'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150, 'y': 0.01974,
                'z': 0.00074
            }.items(), key=lambda item: item[1], reverse=True))
        else:
            print("Língua não suportada. Use 'pt' para português ou 'en' para inglês.")
            raise ValueError("Língua não suportada")
        
    def frequency_analysis(self, text):
        text = text.lower()
        freq_count = {char: 0 for char in self.freq.keys()} # Inicia o dicionário com cada letra do texto zerada
        for char in text:
            if char in freq_count:
                freq_count[char] += 1
        for char, freq in freq_count.items():
            freq = freq / len(text)
            self.freq[char] = freq
            print(f"Frequência de '{char}': {freq:.4f}")

        self.freq = dict(sorted(self.freq.items(), key=lambda item: item[1], reverse=True))

    def kasiski_key_size(self, text, seq_length=3, limit=20, exclude=[]):
        all_distances = self._find_sequences_distances(text, seq_length)
        possible_key_sizes = self._most_common_factors(all_distances, limit)
    
    def _find_sequences_distances(self, text, seq_length=3):
        text = text.lower()
        # Encontra sequências e guarda sua posição
        sequences = {}
        for i in range(len(text) - seq_length):
            seq = text[i:i+seq_length]
            if seq.isalpha():
                if seq not in sequences:
                    sequences[seq] = []
                sequences[seq].append(i)

        # Calcula as distâncias entre as ocorrências de cada sequência
        all_distances = []
        for seq, positions in sequences.items():
            if len(positions) > 1:
                for i in range(len(positions) - 1):
                    distance = positions[i+1] - positions[i]
                    all_distances.append(distance)
        
        if not all_distances:
            print("Nenhuma sequência repetida encontrada para análise de Kasiski.")
            return None

        print(f"\nDistâncias encontradas entre sequências repetidas: {all_distances}")


    def _get_factors(self, number):
        """Função auxiliar para encontrar todos os fatores de um número."""
        factors = set()
        for i in range(1, int(math.sqrt(number)) + 1):
            if number % i == 0:
                factors.add(i)
                factors.add(number//i)
        return list(factors)

    def most_common_factors(self, numbers, limit=20):
        print("\n--- Iniciando Análise de Divisores Comuns ---")
        
        all_factors = []
        for num in numbers:
            factors = self._get_factors(num)
            # Filtra os fatores de acordo com as regras ( > 2 e <= limit). (todos vão ter 1 como fator)
            # Também filtra ten
            valid_factors = [f for f in factors if 2 <= f <= limit]
            all_factors.extend(valid_factors)
            if valid_factors:
                print(f"Divisores válidos para a distância {num} (entre 2 e {limit}): {sorted(valid_factors)}")

        if not all_factors:
            print("Nenhum divisor comum válido encontrado dentro do limite especificado.")
            return None

        # Conta a frequência de cada divisor
        factor_counts = Counter(all_factors)
        print(f"\nContagem de todos os divisores encontrados: {factor_counts}")

        # Encontra o divisor mais comum
        most_common_factors_sorted = [x[0] for x in factor_counts.most_common()]

        print(f"--- Fim da Análise ---")
        print(f"O tamanho de chave da mais provável para menos provável: {most_common_factors_sorted}")

        return most_common_factors_sorted


if __name__ == "__main__":
    abroba = VigenereCipher(key="lemon")
    abroba.encode("attack")