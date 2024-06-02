from Crypto.PublicKey import RSA

rsa_key = RSA.generate(2048)
rsa_key = rsa_key.public_key()
print(rsa_key)
