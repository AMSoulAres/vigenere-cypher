class VigenereCipher():
    def __init__(self, key: str, alphabet: str = "abcdefghijklmnopqrstuvwxyz1234567890.!?"):
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
                # Por exemplo: se a letra da mensagem for 'n' (indice 13) e a letra da chave for 'y' (indice 24), o resultado será 'h' (indice 7), pois dá a volta no alfabeto informado.
                # Deslocando o número de posições do indice da chave.
                # Somando os indices: 13 + 24 = 37 % 30 = 7
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

if __name__ == "__main__":
    abroba = VigenereCipher(key="lemon")
    abroba.encode("attack")