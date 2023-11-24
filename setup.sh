#!/bin/sh

installed() {

    local failed=0
    if [ -z "$2" ]; then
        if ! [ -x "$(command -v $1)" ]; then
            failed=1
        fi
    else
        local ret=0
        $@ &> /dev/null || ret=$?
        if [ "$ret" -ne 0 ]; then
            failed=1
        fi
    fi

    if [ $failed -ne 0 ]; then
        echo "$@ is not available. Please install it first."
        exit 1
    fi

}

installed curl
installed docker
installed docker compose


# Build the Docker services
sudo docker-compose -f docker-compose-project.yml build

# Start the Docker services in detached mode
sudo docker-compose -f docker-compose-project.yml up -d

# Read password for admin user and store it in a variable
read -s -p "Password for admin user: " password
if [ -n "$password" ]; then
    # Change password for admin user
    docker compose -f ./docker-compose-project.yml \
        exec -u gvmd gvmd gvmd --user=admin --new-password=$password
    echo "Password for admin user is '$password'"
else 
    echo "Password for admin user is 'admin'"
fi