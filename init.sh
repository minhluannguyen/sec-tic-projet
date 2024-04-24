
# CA private key
openssl ecparam -out ecc.ca.key.pem -name prime256v1 -genkey
# CA certificate
openssl req -config <(printf "[req]\ndistinguished_name=dn\n[dn]\n[ext]\nbasicConstraints=CA:TRUE") -new -nodes -subj "/C=FR/L=Limoges/O=CRYPTIS/OU=SecuTIC/CN=ACSECUTIC" -x509 -extensions ext -sha256 -key ecc.ca.key.pem -text -out ecc.ca.cert.pem

# Server private key
openssl ecparam -out ecc.key.pem -name prime256v1 -genkey
# Server's Certificate Signing Request
openssl req -config <(printf "[req]\ndistinguished_name=dn\n[dn]\n[ext]\nbasicConstraints=CA:FALSE") -new -subj "/C=FR/L=Limoges/O=CRYPTIS/OU=SecuTIC/CN=serveur" -reqexts ext -sha256 -key ecc.key.pem -text -out ecc.csr.pem
# Sign the CSR with the CA
openssl x509 -req -days 3650 -CA ecc.ca.cert.pem -CAkey ecc.ca.key.pem -CAcreateserial -extfile <(printf "basicConstraints=critical,CA:FALSE") -in ecc.csr.pem -text -out ecc.serveur.pem

# CA public key
openssl ec -in ecc.ca.key.pem -pubout -out ecc.ca.pub.pem