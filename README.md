# haproxy-rpmbuild

This module contains scripts to build haproxy packages. I run this code on my centos6 and centos7 build boxes, and the generated RPM files are published on https://haproxy.hongens.nl, along with an explanation, signing keys, etc.

If you don't want to use the ready-built packages but you want to start building your own haproxy RPM's, feel free to re-use these scripts and files. If you have some great ideas or you see me do stupid stuff, let me know!

### Install rpmbuild tools

First of all, on your buildboxes, make sure all the required packages are installed:

    sudo yum install rpm-build rpmdevtools rpm-sign gcc pcre-devel expect

### GPG keys

In order to be able to sign the RPM packages (optional, but improves security), we need to set up GPG key signing.


##### generate keys

 Run the following command:

    gpg --gen-key

You can answer the standard questions. If it takes too long to get entropy (mostly on vm's), open a second ssh session and run commands that do a lot of io like `md5sum /dev/sda` or `ls -R /` or something to speed up stuff.

The following example shows an example output:

    gpg: checking the trustdb
    gpg: 3 marginal(s) needed, 1 complete(s) needed, PGP trust model
    gpg: depth: 0  valid:   1  signed:   0  trust: 0-, 0q, 0n, 0m, 0f, 1u
    gpg: next trustdb check due at 2020-12-20
    pub   2048R/1A4782E5 2017-12-21 [expires: 2020-12-20]
          Key fingerprint = 1A2E B2B8 A12C 1F23 D2D7  D31E 79F4 B0B5 1A47 82E5
    uid                  Hongens Release Key <angelo@hongens.nl>
    sub   2048R/7CF67F6F 2017-12-21 [expires: 2020-12-20]

In the above example '1A4782E5' is the key id. Take note of it, as well as the name, in my case 'Hongens Release Key', and the password you just made up. We need it later.

##### back up your keys
Run the following commands to back up your keys. Store this stuff in a safe place. (Replace the key id with your own one.)

    gpg -a --export 1A4782E5 > public-gpg.key
    gpg -a --export-secret-keys 1A4782E5 > secret-gpg.key
    gpg --export-ownertrust > ownertrust-gpg.txt

##### import keys
On your other build boxes, restore the keys using these commands. Or keep these in mind if you ever need to restore a key from backup.

    gpg --import secret-gpg.key
    gpg --import-ownertrust ownertrust-gpg.txt

##### use the key for rpm

We already exported the private key, but let's export it using a nice name, and import it using the rpm command. You can put this file on a public web server, and use it in a yum repo file, or distribute it across your nodes for use in Spacewalk.


    gpg --export -a 1A4782E5 > RPM-GPG-KEY-hongens
    sudo rpm --import RPM-GPG-KEY-hongens


##### configure your keys for signing

Copy the config.json.sample to config.json, and edit it's contents to show the correct values. For example, using the above values:

    {
      "gpg_key_name": "Hongens Release Key",
      "gpg_key_id": "1A4782E5",
      "gpg_key_pass" : "secure"
    }

### Build the packages!

You should now be all set!

Run the buildpackages.py script in the directory its in:

    python buildpackages.py

The first time you run it, it might fail because the ~/rpmbuild folder structure is not done yet, but upon a second run it will work fine.

***

Angelo Hongens (angelo@hongens.nl), 2017
