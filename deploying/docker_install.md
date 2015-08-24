# Installation and configuration of Docker
## Ubuntu 15.04:
1. Verify current kernel version by typing:
```bash
uname -r
```
At the time of this writing, the current kernel version is 3.19.0-27

2. Ensure that required and optional packages are installed:
```bash
sudo apt-get install linux-image-3.19.0-27-generic linux-image-extra-3.19.0-27-generic
```
Note that the kernel versions identified in these two packages should match your system kernel version.

3. Reboot your system prior to proceeding with Docker installation
```bash
sudo reboot
```
4. Verify that you have curl installed
```bash
which curl
```
If curl is installed, this command will return the path to your curl installation.
  4. If curl isn't installed, then install it after updating your system
    ```bash
    sudo apt-get update
    sudo apt-get install curl
    ```
5. Obtain the latest Docker package
```bash
curl -SSL https://get.docker.com/ | sh
```
  5. Note: If you are installing behind the BNL firewall, and are using the BNL proxies:
    You need to explicitly add the key directly
    ```bash
    sudo sh -c "wget -qO- https://get.docker.com/gpg | apt-key add -"
    ```
    Then add the docker repository to your aptitude sources list
    ```bash
    sudo sh -c "echo deb http://get.docker.com/ubuntu docker main > /etc/apt/sources.list.d/docker.list"
    ```
    Now, update your aptitude repository list
    ```bash
    sudo apt-get update
    ```
6. Download and install Docker
```bash
sudo apt-get install -y lxc-docker
```
7. Finally, verify that Docker is installed correctly
```bash
sudo docker run hello-world
```

8. Enable forwarding with UFW, if the firewall is enabled:
  8. In order to function properly, Docker needs forwarding traffic to be accepted by Ubuntu's Uncomplicated Firewall (UFW). In order to change the default setting we will edit the configuration file with a text editor (VIM in this case):
  ```bash
  sudo vim /etc/default/ufw
  ```
  Find the line beginning with DEFAULT_FORWARD_POLICY
  Replace the line:
  ```
  DEFAULT_FORWARD_POLICY="DROP"
  ```
  With:
  ```
  DEFAULT_FORWARD_POLICY="ACCEPT"
  ```
  Reload UFW:
  ```bash
  sudo ufw reload
  ```
