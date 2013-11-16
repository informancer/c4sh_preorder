# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "raring64"
  config.vm.box_url = "http://cloud-images.ubuntu.com/raring/current/raring-server-cloudimg-vagrant-amd64-disk1.box"

  config.vm.network "private_network", ip: "192.168.50.2"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.provision "shell", path: "development/vagrant-init.sh"
end
