Provisioning a new site
=======================

## Required Packages:

* nginx
* Python 3.*
* virtualenv + pip
* Git

e.g. on Ubuntu:

    sudo apt update
    sudo apt install nginx git python3.10 python3.10-venv

## Nginx Virtual Hosting config

* see nginx.template.conf
* replace DOMAIN with, e.g. staging.my-domain.com

* cat ./deploy_tools/nginx.template.conf | sed "s/DOMAIN/{sitename}/g" | sudo tee /etc/nginx/sites-available/{sitename}

* sudo ln -s /etc/nginx/sites-available/{sitename} /etc/nginx/sites-enabled/{sitename}

## Systemd service

* see gunicorn-systemd.template.service
* replace DOMAIN with, e.g. staging.my-domain.com

* cat ./deploy_tools/gunicorn-systemd.template.service | sed "s/DOMAIN/{sitename here}/g" | sudo tee /etc/systemd/system/gunicorn-{sitename here}.service

* sudo systemctl daemon-reload
* sudo systemctl reload nginx
* sudo systemctl enable gunicorn-{sitename}
* sudo systemctl start gunicorn-{sitename}

## folder structure:

Assume we have user account at home/username

/home/username
|___ sites
    |___ DOMAIN1
    |      |___ .env
    |      |___ db.sqlite3
    |      |___ manage.py etc
    |      |___ static
    |      |___ virtualenv
    |
    |___ DOMAIN2
          |___ .env
          |___ db.sqlite3
          |___ etc


=============================================

Deploy new site or update deployment (automated)

## Required tools

 * Ansible

## Files needed

* inventory.yaml
* playbook.yaml

## Commands

* ansible-playbook -i inventory.yaml playbook.yaml
* ansible-playbook -i inventory.yaml --extra-vars='{"user":"chon", "sitename":"domain name"}' playbook.yaml --ask-become-pass


==============================================

Git Release tags

## Create tag for deployment

* git tag LIVE
* export TAG=$(date +DEPLOYED-%F/%H%M)
* echo $TAG
* git tag $TAG
* git push origin LIVE $TAG

## Show the logs for the deployment

* git log --graph --oneline --decorate
