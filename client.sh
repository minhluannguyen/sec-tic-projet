#!/bin/bash

if [[ $1 == "create" ]]; then
    # Request recovery of the certificate
    curl -X POST -d 'identite=Tran Xuan Bach' -d 'intitule_certif=SecuTIC' http://localhost:8080/creation
elif [[ $1 == "verify" ]]; then
    # Request verification of the certificate
    curl -v -F image=@my_certificate.png http://localhost:8080/verification
elif [[ $1 == "get" ]]; then
    # Request to get the image
    curl -v -o my_certificate.png http://localhost:8080/fond
else
    echo "Invalid argument. Please specify 'create', 'verify', or 'get'."
fi