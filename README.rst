transport-protocol
==================

|Build Status| |Test Coverage| |Code Climate| |Issue Count|

|Stories in Ready|

Android Debug Bridge (ADB) Transport Protocol

Status
------

This project is actively maintained and under development.

Installation
------------

To install transport-protocol from
`pip <https://pypi.python.org/pypi/pip>`__:

.. code:: bash

        $ pip install adbtp

To install transport-protocol from source:

.. code:: bash

        $ git clone git@github.com:adbpy/transport-protocol.git
        $ cd transport-protocol && python setup.py install

Goals/Scope
-----------

A standalone library that can be used for providing multiple
communication transports within the context of ADB. The transport
protocol should care about:

-  Merging communication
   `transports <https://github.com/adbpy/transports>`__ with the
   `wire-protocol <https://github.com/adbpy/wire-protocol>`__
-  Providing transport agnostic protocol interface

The transport protocol should not care about:

-  Byte layout on the wire
-  Communication transports (UDP, TCP, USB, etc.)
-  High level constructs such as connection "handshakes"
-  Cryptography required to verify endpoints
-  Anything else not explicitly mentioned above...

Contributing
------------

If you would like to contribute, simply fork the repository, push your
changes and send a pull request. Pull requests will be brought into the
``master`` branch via a rebase and fast-forward merge with the goal of
having a linear branch history with no merge commits.

License
-------

`Apache 2.0 <LICENSE>`__

.. |Build Status| image:: https://travis-ci.org/adbpy/transport-protocol.svg?branch=master
   :target: https://travis-ci.org/adbpy/transport-protocol
.. |Test Coverage| image:: https://codeclimate.com/github/adbpy/transport-protocol/badges/coverage.svg
   :target: https://codeclimate.com/github/adbpy/transport-protocol/coverage
.. |Code Climate| image:: https://codeclimate.com/github/adbpy/transport-protocol/badges/gpa.svg
   :target: https://codeclimate.com/github/adbpy/transport-protocol
.. |Issue Count| image:: https://codeclimate.com/github/adbpy/transport-protocol/badges/issue_count.svg
   :target: https://codeclimate.com/github/adbpy/transport-protocol
.. |Stories in Ready| image:: https://badge.waffle.io/adbpy/transport-protocol.svg?label=ready&title=Ready
   :target: http://waffle.io/adbpy/transport-protocol
