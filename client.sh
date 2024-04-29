# Request recovery of the certificate
#curl -X POST -d 'identite=Nguyen Minh Luan' -d 'intitule_certif=SecuTIC' http://localhost:8080/creation

# Request verification of the certificate
curl -v -F image=@tmp/attestation.png http://localhost:8080/verification

# Request to get the image
# curl -v -o mon_image.png http://localhost:8080/fond