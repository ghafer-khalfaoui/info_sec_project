class SDES:
    def __init__(self, key="1010000010"):
        self.key = key
        self.P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
        self.P8 = [6, 3, 7, 4, 8, 5, 10, 9]
        self.IP = [2, 6, 3, 1, 4, 8, 5, 7]
        self.IP_INV = [4, 1, 3, 5, 7, 2, 8, 6]
        self.EP = [4, 1, 2, 3, 2, 3, 4, 1]
        self.P4 = [2, 4, 3, 1]
        self.S0 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]]
        self.S1 = [[0, 1, 2, 3], [2, 0, 1, 3], [3, 0, 1, 0], [2, 1, 0, 3]]
        self.k1, self.k2 = self.generate_keys(self.key)

    def encrypt_caesar(self, text, shift=3):
        encrypted = ""
        for char in text:
            encrypted += chr((ord(char) + shift) % 1114112)
        return ''.join(format(ord(c), '08b') for c in encrypted)

    def decrypt_caesar(self, binary_str, shift=3):
        chars = [chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8)]
        text = "".join(chars)
        decrypted = ""
        for char in text:
            decrypted += chr((ord(char) - shift) % 1114112)
        return decrypted

    def permute(self, bits, mapping):
        return "".join([bits[i - 1] for i in mapping])

    def left_shift(self, bits, shifts):
        return bits[shifts:] + bits[:shifts]

    def xor(self, bits1, bits2):
        return "".join(['1' if b1 != b2 else '0' for b1, b2 in zip(bits1, bits2)])

    def sbox_lookup(self, bits, sbox):
        row = int(bits[0] + bits[3], 2)
        col = int(bits[1] + bits[2], 2)
        return format(sbox[row][col], '02b')

    def generate_keys(self, key):
        p10_key = self.permute(key, self.P10)
        left, right = p10_key[:5], p10_key[5:]
        left1, right1 = self.left_shift(left, 1), self.left_shift(right, 1)
        k1 = self.permute(left1 + right1, self.P8)
        left2, right2 = self.left_shift(left1, 2), self.left_shift(right1, 2)
        k2 = self.permute(left2 + right2, self.P8)
        return k1, k2

    def fk(self, bits, key):
        left, right = bits[:4], bits[4:]
        ep_right = self.permute(right, self.EP)
        xor_res = self.xor(ep_right, key)
        s0_res = self.sbox_lookup(xor_res[:4], self.S0)
        s1_res = self.sbox_lookup(xor_res[4:], self.S1)
        p4_res = self.permute(s0_res + s1_res, self.P4)
        return self.xor(left, p4_res) + right

    def encrypt_block(self, block):
        ip_bits = self.permute(block, self.IP)
        fk1_res = self.fk(ip_bits, self.k1)
        swapped = fk1_res[4:] + fk1_res[:4]
        fk2_res = self.fk(swapped, self.k2)
        return self.permute(fk2_res, self.IP_INV)

    def decrypt_block(self, block):
        ip_bits = self.permute(block, self.IP)
        fk1_res = self.fk(ip_bits, self.k2)
        swapped = fk1_res[4:] + fk1_res[:4]
        fk2_res = self.fk(swapped, self.k1)
        return self.permute(fk2_res, self.IP_INV)

    def encrypt_text(self, text):
        binary = ''.join(format(ord(c), '08b') for c in text)
        blocks = [binary[i:i+8] for i in range(0, len(binary), 8)]
        return ''.join([self.encrypt_block(b) for b in blocks])

    def decrypt_text(self, encrypted_binary):
        blocks = [encrypted_binary[i:i+8] for i in range(0, len(encrypted_binary), 8)]
        chars = [chr(int(self.decrypt_block(b), 2)) for b in blocks]
        return ''.join(chars)
