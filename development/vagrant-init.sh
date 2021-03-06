#!/bin/bash

# set up our environment
locale-gen en_US.UTF-8
locale-gen de_DE.UTF-8

export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

echo "127.0.1.1 preorderdev" >>/etc/hosts
hostname preorderdev

# update repository cache
apt-get -q -y update

# basic packages
apt-get install -q -y build-essential python python-dev python-setuptools python-pip git zsh screen tmux vim

# certain module dependencies
apt-get install -q -y libjpeg62-dev zlib1g-dev libfreetype6-dev liblcms1-dev libncurses5-dev libfreetype6 libpng-dev python-m2crypto

# ghettofix for PIL
ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib
ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib
ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib

# mysql
export DEBIAN_FRONTEND=noninteractive
apt-get install -q -y mysql-server mysql-client python-mysqldb
mysqladmin create c4sh_preorder

# virtualenv global setup
if ! command -v pip; then
    easy_install -U pip
fi
if [[ ! -f /usr/local/bin/virtualenv ]]; then
    pip install virtualenv virtualenvwrapper virtualenv-clone
fi

# install our Python dependencies
pip install -r /vagrant/deployment/requirements.txt

# symlink our source code to vagrant homedir
ln -s /vagrant/c4sh_preorder /home/vagrant/

# copy misc. files
cp /vagrant/development/files/motd /etc/motd.tail

export HOME=/home/vagrant # this is now neccessary here
sudo -u vagrant git clone https://github.com/CCCO/c4sh /home/vagrant/c4sh

echo
echo
echo "Your c4sh_preorder development instance is ready, use 'vagrant ssh' to connect."
