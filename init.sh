# Create directories
if [[ ! -d "img" ]]
then
	mkdir img
fi

if [[ ! -d "CA" ]]
then
	mkdir CA 
fi

if [[ ! -d "tmp" ]]
then
	mkdir tmp 
fi

# Get TSA certificates
if [[ ! -f "CA/tsa.crt" ]]
then
	wget https://freetsa.org/files/tsa.crt -P CA
fi

if [[ ! -f "CA/cacert.pem" ]]
then
	wget https://freetsa.org/files/cacert.pem -P CA
fi

# CA private key
openssl ecparam -out CA/ecc.ca.private.pem -name prime256v1 -genkey
# CA certificate
openssl req -config <(printf "[req]\ndistinguished_name=dn\n[dn]\n[ext]\nbasicConstraints=CA:TRUE") -new -nodes -subj "/C=FR/L=Limoges/O=CRYPTIS/OU=SecuTIC/CN=ACSECUTIC" -x509 -extensions ext -sha256 -key CA/ecc.ca.private.pem -text -out CA/ecc.ca.cert.pem

# Server private key
openssl ecparam -out CA/ecc.server.private.pem -name prime256v1 -genkey
# Server's Certificate Signing Request
openssl req -config <(printf "[req]\ndistinguished_name=dn\n[dn]\n[ext]\nbasicConstraints=CA:FALSE") -new -subj "/C=FR/L=Limoges/O=CRYPTIS/OU=SecuTIC/CN=localhost" -reqexts ext -sha256 -key CA/ecc.server.private.pem -text -out CA/ecc.server.csr.pem
# Sign the CSR with the CA
openssl x509 -req -days 3650 -CA CA/ecc.ca.cert.pem -CAkey CA/ecc.ca.private.pem -CAcreateserial -extfile <(printf "basicConstraints=critical,CA:FALSE") -in CA/ecc.server.csr.pem -text -out CA/ecc.server.cert.pem

# CA public key
openssl ec -in CA/ecc.ca.private.pem -pubout -out CA/ecc.ca.public.pem

# Bundle server
cat CA/ecc.server.private.pem CA/ecc.server.cert.pem > CA/ecc.server.bundle.pem