import hashlib


def mine_proof(data: str, difficulty: int = 3, max_nonce: int = 10_000_000) -> tuple[int, str]:
    """
    Simple Proof of Work (PoW) example with 3 conditions:
      1. data must be a non-empty string
      2. difficulty must be a positive integer
      3. the hash must start with '0' * difficulty
    """
    # Condition 1: data must not be empty
    if not isinstance(data, str) or not data.strip():
        raise ValueError("Data must be a non-empty string.")

    # Condition 2: difficulty must be valid
    if not isinstance(difficulty, int) or difficulty <= 0:
        raise ValueError("Difficulty must be a positive integer.")

    target_prefix = "0" * difficulty
    nonce = 0

    while nonce < max_nonce:
        block = f"{data}:{nonce}".encode()
        hash_value = hashlib.sha256(block).hexdigest()

        # Condition 3: hash must satisfy the PoW requirement
        if hash_value.startswith(target_prefix):
            return nonce, hash_value

        nonce += 1

    raise RuntimeError("PoW failed within the given nonce range.")


def is_valid_proof(data: str, nonce: int, hash_value: str, difficulty: int = 3) -> bool:
    """Validate whether the given nonce and hash satisfy the PoW conditions."""
    if not isinstance(data, str) or not data.strip():
        return False
    if not isinstance(nonce, int) or nonce < 0:
        return False
    if not isinstance(difficulty, int) or difficulty <= 0:
        return False

    computed_hash = hashlib.sha256(f"{data}:{nonce}".encode()).hexdigest()
''
''
''
    return computed_hash == hash_value and computed_hash.startswith("0" * difficulty)


if __name__ == "__main__":
    data = "Hello, PoW!"
    nonce, hash_value = mine_proof(data, difficulty=3)
    print(f"Data: {data}")
    print(f"Nonce: {nonce}")
    print(f"Hash: {hash_value}")
    print(f"Valid: {is_valid_proof(data, nonce, hash_value, difficulty=3)}")
