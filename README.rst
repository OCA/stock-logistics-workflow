.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================================
Stock Scanner : WorkFlow engine for scanner hardware
====================================================

This module allows managing barcode readers with simple scenarios:

- You can define a workfow for each object (stock picking, inventory, sale, etc)
- Works with all scanner hardware model (just SSH client required)

Some demo/tutorial scenarios are available in the "demo" directory of the module.
These scenarios, are automatically imported when installing a new database with demo data.

Installation
============


The "sentinel.py" specific ncurses client is available in the "hardware" directory.
If you plan to use the specific "sentinel.py", you will need the "openobject-library" Python module, available from pip:

    $ sudo pip install "openobject-library<2"

.. note::

   You must use openobject-library earlier than 2.0 with Odoo.
   The version 2.0 of openobject-library only implements the Net-RPC protocol, which was removed from v7.

To test the module, some demo scenarii are available in the `demo` directory of the module.

Configuration
=============

In Odoo
-------

Declare hardware
^^^^^^^^^^^^^^^^

You have to declare some hardware scanners in Odoo.

Go to "Warehouse > Configuration > Scanner Hardware" and create a new record.

The "step type code" sent by the "sentinel.py" client at start-up is the IP address of the hardware, if connected through SSH.

If needed enable Login/Logout
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The module come with 2 predifined scenarii for Login and Logout. The functionality is disabled by default and the user to use in
Odoo must be specified in the .oerp_sentinelrc file used by sentinel and can be overriden on the Scanner Hardware definition
in Odoo. 

If the Login/logout functionality is enabled, when a user start a session with sentinel, only the Login scenario is displayed on the
screen. The scenario will prompt the user for its login and pwd. If the authentication succeed, each interaction with Odoo will be done
using the uid of the connected user. Once connected, a Logout scenario is displayed in the list of available scenarii and the Login
scenario no more appear. 

The Login/logout functionality enable you to specify on the scenario a list of users and/or a list of groups with access to the scenario.

To enable the Login/logout functionality:
    * Go to "Settings > Warehouse" and check the checkbox Login/logout scenarii enabled.
    * Create a *Technical User* 'sentinel' **without roles in Human Resources** and with 'Sentinel: technical users' checked.
    * Use this user to launch your sentinel session.

Be careful, the role *Sentinel: technical users* is a technical role and should only be used by sentinel.

The timeout of sessions is managed by a dedicated cron that reset the inactive sessions. The timeout can be configured on 
settings. "Settings > Warehouse"

For the sentinel.py client
--------------------------

The sentinel.py client uses a config file named `.oerpsentinelrc`, using the standard `ini` format.

This file simply contains information for server connection (hostname, port, username, password and database).

    [openerp]
    host = localhost
    password = admin
    database = demo

Writing scenarii
----------------

Creation
^^^^^^^^

The preferred way to start the creation of a scenario is to create steps and transitions in diagram view.

Once your steps are created, you can write python code directly from Odoo, or you can export the scenario to write the python code with your preferred code editor.

In the python code of each step, some variables are available :
    - cr : Cursor to the database
    - uid : ID of the user executing the step (user used to log in with the sentinel, or user configured on the hardware, if any)
    - pool : Pooler to the database
    - env : Environment used to execute the scenario (new API)
    - model : Pooler on the model configured on the scenario
    - custom : Pooler on the custom values model
    - term : Recordset on the current scenario
    - context : Context used on the step
    - m or message : Last message sent by the hardware
    - t or terminal : Browse record on the hardware executing the step
    - tracer : Value of the tracer of the used transition to access this step
    - wkf or workflow : Workflow service
    - scenario : Recordset on the current scenario for the hardware
    - _ : The translation function provided by Odoo (useable like in any other python file)

Some of these variables are also available on transition conditions execution.

As stated previously, the step must always return:

- A step type code, in the `act` variable
- A message to display on the hardware screen, in the `res` variable
- Optionally, a default value, in the `val` variable

Step types
^^^^^^^^^^

The step types are mostly managed by the client.

The standard step types are :

- M : Simple message
- F : Final step, like M, but ends the scenario
- T : Text input
- N : Number input (integer)
- Q : Quantity input (float)
- L : List
- E : Error message, like M, but displayed with different colors
- C : Confirm input
- A : Automatic step. This type is used to automatically execute the next step

.. note::

   The automatic step often needs to define a value in `val`, corresponding to the value the user must send.
   This step type is generally used as replacement of another type, at the end of the step code, by redefining the `act` variable in some cases, for example when a single value is available for a list step.

Import
^^^^^^

Scenarios are automatically imported on a module update, like any other data.
You just have to add the path to your `Scenario_Name.scenario` files in the `data` or `demo` sections in the `__openerp__.py` file.

Export
^^^^^^

The export script is in the `script` directory of the module

A scenario is exported as a set of files, containing :
    - Scenario_Name.scenario : Global description of the scenario (name, warehouses, steps, transitions, etc.)
    - A .py file per step : The name of the file is the XML ID of the step

Using a test file
^^^^^^^^^^^^^^^^^

When developing scenarios, you will often have the same steps to run.
The sentinel.py client allows you to supply a file, which contains the keys pressed during the scenario.

You can define the file to use in the configuration file, on the "test_file" key.
This file will be read instead of calling the curses methods when the scenario is waiting for a user input (including line feed characters).
When the file has been fully read, the client exits.

A sample test file can be found in the "Step Types" demo scenario.

*Special keys* :
For special keys (arrows, delete, etc.), you must write a line containing ':', followed by the curses key code.

Valid key codes are :
    - KEY_DOWN : Down arrow
    - KEY_UP : Up arrow
    - KEY_LEFT : Left arrow
    - KEY_RIGHT : Right arrow
    - KEY_BACKSPACE : Backspace
    - KEY_DC : Delete

Usage
=====

On start-up, the client lists available scenarii.
When the user selects a scenario, the current scenario and step are stored on the hardware configuration's entry in Odoo.

When the client sends a message to the server, the next step is selected depending on the current step and the message sent.
Then, the server returns the result of the step, which contains its type code and the text to display on the hardware screen.
Unlike the standard Odoo Workflow, each step needs to find a valid transition, because a step needs to be displayed on the hardware screen at all times.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/stock-logistics-workflow/issues/new?body=module:%20stock_scanner%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------
* Alexandre Fayolle <afayolle.ml@free.fr>
* Christophe CHAUVET <christophe.chauvet@syleam.fr>
* Damien Crier <damien@crier.me>
* Laetitia Gangloff <laetitia.gangloff@acsone.eu>
* Laurent Mignon <laurent.mignon@acsone.eu>
* Olivier Dony <odo@openerp.com>
* Sebastien LANGE <sebastien.lange@syleam.fr>
* Sylvain Garancher <sylvain.garancher@syleam.fr>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
