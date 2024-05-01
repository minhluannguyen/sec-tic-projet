#!/bin/bash

if [[ $1 == "create" ]]; then
    identite=$2
    intitule_certif=$3

    # Request recovery of the certificate
    curl -v -X POST -d "identite=$identite" -d "intitule_certif=$intitule_certif" --cacert CA/ecc.ca.cert.pem https://localhost:9000/creation
elif [[ $1 == "verify" ]]; then
    image_path=$2
    # Request verification of the certificate
    curl -v -F "image=@$image_path" --cacert CA/ecc.ca.cert.pem https://localhost:9000/verification
elif [[ $1 == "get" ]]; then
    image_path=$2
    # Request recovery of the certificate
    curl -v -o $image_path --cacert CA/ecc.ca.cert.pem https://localhost:9000/fond
elif [[ $1 == "help" ]]; then
    echo "Usage: $0 [create|verify|get] [arguments]"
    echo "Options:"
    echo "  create <identite> <intitule_certif>   Create a certificate"
    echo "  verify <image_path>                   Verify a certificate"
    echo "  get <image_path>                      Retrieve the certificate"
    echo "  help                                  Display this help"
else
    echo "Run '$0 help' for instructions"
fi