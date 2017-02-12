
# PREPARE an environment for running b2safe scripts
# for automatic metadata extraction

apt-get update
apt-get install python-pip
pip2 install pyxb==1.2.4 nested_lookup

cd /tmp
git clone https://github.com/EUDAT-B2SAFE/B2SAFE-core.git b2safe
mv b2safe/scripts/metadata .

mkdir /tmp/metadata/log
mkdir /tmp/testing
touch /tmp/testing/pippo

cd metadata
python2.7 mets_factory.py \
    -dbg -d --filesystem /tmp/testing conf/mets_factory.conf \
    > manifest.xml
