
# Download Faulty
wget https://gist.githubusercontent.com/posidron/802f519bd54a05cc50bb51fbc0563448/raw/451062c31537635622b9ba14615e608718da256e/faulty.v14.diff

# Download mozilla build configs
git clone --depth=1 https://github.com/posidron/mozilla-build-configs configs

# Apply Faulty to mozilla-inbound
git apply --ignore-space-change --ignore-whitespace faulty.v14.diff

# Compile Firefox
sed -ie 's:../configs/:configs/:' configs/mozconfig.mi-asan-ipc-fuzzer
export MOZCONFIG=configs/mozconfig.mi-asan-ipc-fuzzer
./mach build

# Create FuzzManager configuration
cat << EOF > obj-ff64-asan-opt/dist/bin/firefox.fuzzmanager.conf
[Main]
platform = x86-64
product = mozilla-inbound
product_version = $MERCURIAL_REVISION
os = linux

[Metadata]
pathPrefix = $MC
buildFlags = --enable-ipc-fuzzer --enable-address-sanitizer
EOF

# Run package routines for Firefox
./mach package

cp obj-ff64-asan-opt/dist/firefox*.tar.bz2 /srv/builds/faulty.tar.bz2
cp obj-ff64-asan-opt/dist/bin/firefox.fuzzmanager.conf /srv/builds/faulty.fuzzmanager.conf
