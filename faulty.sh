# Title:     UserData script for running rr with a Faulty enabled Firefox build
# Version:   v1.0
# Supported: Ubuntu 16.04 (tested)
# Reference: https://github.com/mozilla/rr/wiki/Building-And-Installing

sudo apt-get --yes --quiet update
sudo apt-get --yes --quiet build-dep firefox

# Dependencies: general
sudo apt-get --yes --quiet install ack-grep xz-utils subversion zip unzip python-dev python-pip python-setuptools

# Dependencies: rr
sudo apt-get --yes --quiet install clang git ninja-build ccache cmake g++-multilib gdb pkg-config libz-dev realpath python-pexpect manpages-dev zlib1g-dev

# Download rr source
mkdir rr
cd rr
git clone https://github.com/mozilla/rr.git
cd rr
# Version: 4.2.0
#git reset --hard 32eef050b19dbfd13ac0962f66806a2d0444d83e
cd -
mkdir obj
cd obj

# Compile
CC=clang CXX=clang++ cmake -G Ninja ../rr
ninja
sudo ninja install

# System configuration for rr
sudo echo 1 > /proc/sys/kernel/perf_event_paranoid

cd

# Download a Faulty enabled mozilla-inbound build
wget https://build.fuzzing.mozilla.org/builds/faulty.tar.bz2
tar xjf faulty.tar.bz2

wget https://build.fuzzing.mozilla.org/builds/faulty.fuzzmanager.conf
mv faulty.fuzzmanager.conf firefox/

# Create custom profile for Firefox
ff_profile_path=$(xvfb-run ./firefox/firefox -CreateProfile faulty-fuzzer | ack "Success: .* at '(.*)/prefs.js'" --output='$1')

# Download and copy custom preferences for Firefox
wget https://raw.githubusercontent.com/mozillasecurity/faulty/master/faulty.js
cp faulty.js $(ff_profile_path)/user.js

# Download launcher for Faulty
wget https://raw.githubusercontent.com/MozillaSecurity/faulty/master/faulty-rr.py
chmod a+x faulty-rr.py

screen -t faulty -dmS faulty rr ./faulty-rr.py "https://www.youtube.com/watch?v=N3UIUZ1EXgs"
