Python interface for TK5000 gps tracker
#######################################

`Device Manual (german)`_

.. _`Device Manual`: http://www.gpsvision.de/downloads/15_02_2012_ANLEITUNG_TK5000_url.pdf


First steps to connect device:

- poweron, wait 5 seconds

- connect

- ``ls -l /dev/serial/by-id/``
  returned ``ttyACM3`` in my case

- ``sudo chmod 777 /dev/ttyACM3``

- ``minicom -l -b 115200 -D /dev/ttyACM3 -R 'ascii'``


Known commands and return values
================================
::
        $WP+VER=0000
        $OK:VER=TK5000T 5.000rev15,V10

More commands in the manual.
