### Sweeper installation 

Installation from artifactory:

    python -m pip install --extra-index-url https://artifactory.f5net.com/artifactory/api/pypi/f5-pypi-internal/simple ucs_sweeper


UCS Sweeper is a script created with the purpose of removal of any private data (i.e. keys, passwords, certificates and other related things) that might be contained in the ucs file taken from an external source.

Swept ucs needs to be loaded with a parameter reset-trust (tmsh load sys ucs <name> reset-trust)

This tool is not foolproof. Customer ucs files are usually incredibly complex and unpredictable in their structure and the configuration file format makes it very difficult to parse, so the performed changes are rudimentary. To ensure compliancy with privacy standards, after using this tool the swept ucs should be manually scoured for any private data within.

A swept ucs should be loaded manually at least once - in case of a failure it might be necessary to modify certain fields in the config by hand. If you happen on a problem like that, please report a task on our Journeys team's to include the fix in a future release.

    Most of the time you would like to also run ucs_modifier on the UCS file after it was processed by ucs_sweeper, more:
    https://gitswarm.f5net.com/cxt/journeys/f5-bigip-ucs-modifier/-/blob/master/README.md


Running the sweeper
The sweeper script is stored under cxt/journeys/f5-bigip-ucs-sweeper/ucs_sweeper/calypso_ucs_sweeper.py

To run sweeper as a standalone tool, you can install it as per 3rd line of this readme file and use the executable:

    root@3fedbeca02e2:/sweeper# ucs-sweeper --help
    usage: ucs-sweeper [-h] -u UCS [-o OUTPUT] [-d]

    Sweeps the specified ucs file, removing any sensitive data

    optional arguments:
    -h, --help            show this help message and exit
    -u UCS, --ucs UCS     Ucs file to sweep
    -o OUTPUT, --output OUTPUT
                            Target output file name
    -d, --debug           Enable debug logging

### Sweeper functions

Currently sweeper process ucs file and introduce following changes to the files in archive:

- Remove config difference files present in some of the newer BIG-IP versions
- Try to remove any config backups user might have added to their ucs - currently remove any files ending with .conf and some extra characters, e.g. config/wa.pvsystem.conf.11.5.1 or config/bigip.conf.old
- Remove any info about non-default users from bigip_user.conf, /etc/shadow, /etc/passwd (delete all user entries except root, admin and f5hubblelcdadmin)
- Reset default user passwords to their default values in both bigip_user.conf and /etc/shadow: 'admin' for 'admin', 'default' for 'root'
- Remove all files from user home directories: clean /root/, /home/admin, remove any other directories in /home/
- Remove any files from the restjavad storage
- Remove traps and users sections from snmp configuration
- Remove any certificates and keys found in the ucs file. Additionally, files matching any of the following patterns are also removed: (*.deer, *pem, *.pfx, *.p12, EM_certs.txt, EM_DB.txt, ssh_host_dsa_key, ssh_host_rsa,key, ssh_host_key)
    - Removal of device certificates forces you to load the ucs with the parameter reset-trust
    - Sweeper creates a new dummy certificate, key and revocation list under the names ssl.crt/default.crt, ssl.key/default.key and ssl.crl/sample.crl
    - Any config entries mentioning the removed files is replaced with one of the new dummy files, depending on their extension
    - Some extra fields are modified to ensure compatibility with the replaced self-signed certificates
    - A new rndc key is generated and put in the rndc.key file
- A number of fields in .conf files containing either 'bigip' or 'zebos' in their names are modified - either replacing their values with 'none' or 'calypso', or removing the lines altogether:
    - access-key
    - accessgate-encrypted-password
    - accessgate-password   
    - access-key
    - account-password
    - admin-encrypted-password
    - admin-dn
    - admin-password
    - admin-pw
    - administrator-password
    - auth-key
    - auth-key-encrypted
    - aws-access-key
    - aws-secret-key
    - basic-auth-password
    - basic-auth-username
    - bind-pw
    - bind-db
    - caller-password
    - certmap-base
    - challenge-password
    - client-id
    - client-secret
    - cookie-encryption-passphrase
    - ecm-auth
    - encrypt-cookie-secret
    - encrypt-key
    - encrypted-password
    - encryption-key
    - factory-rule
    - form-username
    - form-password
    - fwdp-ca-passphrase
    - global-access-protocol-passphrase
    - group-base
    - insert-cookie-passphrase
    - java-sign-key-passphrase
    - machine-account-password
    - md5-signature-passphrase
    - mdm-token
    - my-cert-key-passphrase
    - opaque-token 
    - passphrase
    - password
    - pem-encoding
    - preshared-key
    - preshared-key-encrypted
    - private-key
    - private-text
    - proxy-ca-passphrase
    - public-key
    - resource-server-id
    - resource-server-secret
    - script-signature
    - secret
    - set ihealthpassword
    - shared-secret
    - signer-key-passphrase
    - sign-key-passphrase
    - site-ket
    - sym-unit-key
    - user
    - username
    - tmpl-checksum
    - tmpl-signature
- Any file modified during the process has it's entry removed from the SPEC-Files and SPEC-Manifest file in the root of the ucs

### Bug reporting

Let us know if something went wrong. By reporting issues, you support development of this project and get a chance of having it fixed soon.
Please use bug template available [here](https://gitswarm.f5net.com/cxt/journeys/f5-bigip-ucs-sweeper/-/issues/new?assignees=&labels=&template=bug.md&title=%5BBUG%5D)