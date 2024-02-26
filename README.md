# passman
An offline password manager with focus on security and reliability. It is written in microPython and tested on Raspberry pie pico and ESP32 boards.

Security is ensured by a multi-pass AES encryption method, the key to decrypt this password is provided by the user, after logging into the device all of the saved data gets decrypted with the password, and becomes available to the user.

Reliability is ensured by RAID 1 and series of checksums using SHA256, user data is stored in a few microSD cards that are acccessed via RAID1 to ensure reliability with an option to create an external backup. 

## Dev setup


### TODO
[ ] fix encrypt_loop for data with more than 32 letters
[ ] password right now can be reset by removing a file on the sd card
