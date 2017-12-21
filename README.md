# haproxy-rpmbuild

### install rpmbuild tools

  sudo yum install rpm-build rpmdevtools rpm-sign gcc pcre-devel


### set up your gpg-keys

  gpg --gen-key
  gpg --export -a 'Name' > RPM-GPG-KEY-foo
  sudo rpm --import RPM-GPG-KEY-foo

### run the stuff

  python buildpackages.py
