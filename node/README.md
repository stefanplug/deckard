deckard
=======

Manual install
======
To manually install by hand:
```
git clone https://github.com/stefanplug/deckard.git
cd deckard/node/

sudo mkdir /usr/local/lib/python3.2/dist-packages/deckardnode/
sudo cp deckardnode.py /usr/local/lib/python3.2/dist-packages/deckardnode/
sudo cp __init__.py /usr/local/lib/python3.2/dist-packages/deckardnode/
sudo cp scripts/deckard-node /usr/local/bin/deckard-node

sudo cp etc/init.d/deckard-node /etc/init.d/deckard-node
sudo mkdir -p /etc/deckardnode/scripts/
sudo cp etc/scripts/ping.sh /etc/deckardnode/scripts/

sudo chown root. /usr/local/bin/deckard-node
sudo chown -R root. /usr/local/lib/python3.2/dist-packages/deckardnode/
sudo chown -R root. /etc/deckardnode/scripts/
sudo chown root. /etc/init.d/deckard-node
```

Pip install
======

To manually install using setuptools:
```
python3 setup.py install
```
