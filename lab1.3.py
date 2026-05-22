alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
alphabet_len = 36

encrypted_text = "fw668i12ts00t3amwezr"
keys = ["235e", "5eud"]

for base in range(alphabet_len):
    decoded_text = ""   

    for i in range(len(encrypted_text)):
        char = encrypted_text[i].lower()

        if char in alphabet:
            char_index = alphabet.index(char)
            shift = (base + i) % alphabet_len
            new_index = (char_index - shift) % alphabet_len
            decoded_text += alphabet[new_index]
        else:
            decoded_text += char

    key_positions = []
    all_keys_found = True

    
    for key in keys:
        clean_key = key.strip().lower()
        key_freq = {}
        for char in clean_key:
            key_freq[char] = key_freq.get(char, 0) + 1

        found_index = -1

        for start_pos in range(len(decoded_text) - len(clean_key) + 1):
            substring = decoded_text[start_pos:start_pos + len(clean_key)]

            window_freq = {}
            for char in substring:
                window_freq[char] = window_freq.get(char, 0) + 1

            if window_freq == key_freq:
                found_index = start_pos
                break

        if found_index != -1:
            key_positions.append(found_index)
        else:
            all_keys_found = False
            break

    if all_keys_found and key_positions:
        print(f"Base: {base}")
        print(f"Text: {decoded_text}")
        print(f"Indexes: {key_positions}")