To configure this module, you need to:

#. Go to *Inventory > Configuration > Warehouse Management > Operations Types*
#. Open the operation type for which you want late picking activities
   to be generated.
#. Check 'Create Late Picking Activity' checkbox, select the user who
   will be responsible for the generated activity and save the form.
#. From time to time, your system will check if exist late pickings
   ('scheduled date' is before current date) and will create an
   activity for them, with the user selected in the corresponding
   operation type as responsible.

This module generates a 'scheduled action' to create the late picking
activities when is needed. To adjust the parameters for that:

#. Go to * Settings > Technical > Automation > Scheduled Actions *
#. Finds the 'scheduled action' named 'Picking: activities for late pickings'
#. Edit it and adjust the parameters if you need and save the form.

The late picking activities created will be associated with a new
'activity type'. If you want to adjust the parameters of that:

#. Go to * Settings> Technical> Email> Activity Types *
#. Find the 'activity type' named 'Late picking'
#. Edit it and adjust the parameters if you need and save the form.

Note: The summary and note of the created activities will be the same
defined as summary in the 'activity type' named 'Late picking'.

