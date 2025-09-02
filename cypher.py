from collections import Counter
import math


class VigenereCypher():
    def __init__(self, key: str, alphabet: str = "abcdefghijklmnopqrstuvwxyz"):
        self.key = key.lower()
        self.alphabet = alphabet.lower()

    def encode(self, text: str) -> str:
        encoded_chars = []
        key_index = 0
        for char in text:
            if char in self.alphabet:
                # Aqui usa módulo para gerar o keystream.
                # Quando i excede o tamanho da chave retorna para o inicio da chave
                # e assim por diante independente do tamanho da mensagem.
                # Ignora espaços vazios nesse caso.
                key_char = self.key[key_index % len(self.key)]

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

                key_index += 1
            else:
                encoded_chars.append(char)
        return ''.join(encoded_chars)
    
    def decode(self, text: str) -> str:
        decoded_chars = []
        key_index = 0
        for char in text:
            if char in self.alphabet:
                # Exata mesma lógica para keystream
                key_char = self.key[key_index % len(self.key)]

                # Essa lógica é o inverso da de encode, só volta no deslocamento. Ao subtrair chega-se na letra original
                decoded_index = (self.alphabet.index(char) - self.alphabet.index(key_char)) % len(self.alphabet)
                decoded_chars.append(self.alphabet[decoded_index])

                key_index += 1
            else:
                decoded_chars.append(char)
        return ''.join(decoded_chars)

class BreakCypher():
    # Para que essa quebra pelo método de kasiski de análise de frequência por kasiski funcione o texto de entrada deve ter tamanho considerável. (100x o tamanho da chave a ser encontrada)

    def __init__(self, language, method="kasiski", limit=20, alphabet="abcdefghijklmnopqrstuvwxyz"):
        self.language = language
        self.alphabet = alphabet
        self.method = method
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

    def kasiski_method_possible_key_sizes(self, text, seq_length=3, limit=20, exclude=[]):
        all_distances = self._find_sequences_distances(text, seq_length)
        return self.most_common_factors(all_distances, limit)


    
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
        return all_distances


    def _get_factors(self, number):
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
    
    def _chi_squared_test(self, text):
        # Calcula a frequência das letras no texto fornecido
        observed_counts = Counter(c for c in text if c in self.alphabet)
        text_len = len(text)

        # Se o texto for vazio, retorna um valor alto para descartá-lo
        if text_len == 0:
            return float('inf')

        # Calcula o valor de Qui-Quadrado
        chi_squared = 0.0
        for letter in self.alphabet:
            # Frequência esperada da letra no idioma escolhido
            expected_count = self.freq.get(letter, 0.0) * text_len
            
            # Contagem observada da letra no texto
            observed_count = observed_counts.get(letter, 0)
            
            # A fórmula de Qui-Quadrado
            difference = observed_count - expected_count
            chi_squared += (difference * difference) / (expected_count + 1) # +1 para evitar divisão por zero

        return chi_squared

    def _find_key_for_column(self, column):
        best_chi = float('inf')
        best_key_char = ''

        # Testa cada letra do alfabeto como uma possível chave de Cifra de César
        for key_char in self.alphabet:
            # "Decifra" a coluna usando a letra da chave atual (key_char)
            # Isso é o mesmo que a função de decode, mas para uma única letra
            shift = self.alphabet.index(key_char)
            decrypted_column = ""
            for char in column:
                if char in self.alphabet:
                    decrypted_index = (self.alphabet.index(char) - shift) % len(self.alphabet)
                    decrypted_column += self.alphabet[decrypted_index]
            
            # Calcula o Qui-Quadrado para a coluna decifrada
            chi = self._chi_squared_test(decrypted_column)
            
            # Se o resultado for o menor até agora, guarda essa letra da chave
            if chi < best_chi:
                best_chi = chi
                best_key_char = key_char
        
        return best_key_char

    def break_cypher(self, text):
        print("\n--- Iniciando Quebra da Cifra de Vigenère ---")
        
        # Usa o método escolhido para encontrar o tamanho mais provável da chave
        if self.method == "kasiski":
            possible_sizes = self.kasiski_method_possible_key_sizes(text)
            if not possible_sizes:
                print("Não foi possível determinar o tamanho da chave.")
                return ""
        else:
            print("Não implementado")

        for key_length in possible_sizes:
            print(f"\nTamanho de chave mais provável sendo testado: {key_length}")

            # Divide o texto cifrado em colunas com base no tamanho da chave
            columns = [''] * key_length

            key_index = 0 # Contador que só avança para caracteres do alfabeto
            for char in text:
                if char in self.alphabet:
                    columns[key_index % key_length] += char
                    key_index += 1 # Incrementa o contador apenas quando um caractere válido é processado
            # print(f"Colunas formadas para análise: {columns}")
            
            found_key = ""

            # Para cada coluna, encontra a letra da chave correspondente.
            # Testa as 26 posições possíveis do alfabeto para cada coluna
            for i, column in enumerate(columns):
                # print(f"\nAnalisando coluna {i+1}/{key_length}...")

                # Utiliza o teste do Qui-Quadrado para encontrar a letra da chave
                # A letra da chave é aquela que minimiza a estatística de Qui-Quadrado
                key_char = self._find_key_for_column(column)
                # print(f"Letra da chave encontrada para a coluna {i+1}: '{key_char}'")
                found_key += key_char
                
            print("\n--- Quebra da Cifra Finalizada ---")
            print(f"Chave encontrada: {found_key}")
            print(f"Texto cifrado: {text}")
            cifrador = VigenereCypher(key=found_key, alphabet=self.alphabet)
            print(f"Texto decifrado: {cifrador.decode(text)}")
            user_input = input("A mensagem está consistente? (S/N)")

            if user_input.strip().upper() == 'S':
                print("Mensagem consistente.")
                return found_key
            else:
                print("Mensagem inconsistente. Testando próximo tamanho")
                continue

if __name__ == "__main__":
    plaintext = "a gloria que se nao prova aos outros nao e gloria para nos e vaidade e pode ser ate remorso talvez nao me explico bem mas creio que me entende uma noite destas ha de ser o que me disse um secretario de estado que nao me conhecia e com quem travei conhecimento em casa do comendador pereira da silva foi uma noite de julho de chovia a potes e o comendador que e muito meu amigo convidou me para ficar e dormir ali eu resisti mas ele tanto instou que aceitei o convite e fiquei"
    plaintext= "texto bem menor"
    abroba = VigenereCypher(key="abroba")
    encrypted = abroba.encode(plaintext)

    attack = BreakCypher(language="pt", method="kasiski")
    key = attack.break_cypher(encrypted)