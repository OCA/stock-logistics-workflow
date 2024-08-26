To configure notification rules:

* Go to `"Inventory -> Configuration -> Warehouse Management -> New Picking Notifications"` and create a new notification
* Put the following data in the notification form:
  * `Priority`. Defines the order in which notification rules are checked. The lower is the number the higher is the priority. Default is `10`
  * `Operation Types`, required. Specifies the operation types for which this notification will be triggered
  * `Notified Users`, required. List of users to be notified
  * `Source Document Pattern`, optional. Notification will be sent if source document name matches the specified regex pattern. Leave blank to match any source
  * `Custom Message`, optional. Custom message to be used instead of the default one. Leave blank to use the default message
  * `Notification Sound`, optional. Custom sound to be used with notification. Leave blank to use notification without sound
  * `Draft` - optional. If enabled, notifications will be sent when a picking is in the "Draft" state
  * `Waiting Another Operation` - optional.  If enabled, notifications will be sent when a picking is in the "Waiting Another Operation" state
  * `Waiting` - optional. If enabled, notifications will be sent when a picking is in the "Waiting" state
  * `Ready` - optional. If enabled, notifications will be sent when a picking is in the "Ready" state.
  * `Done` - optional. If enabled, notifications will be sent when a picking is in the "Done" state.
  * `Cancel` - optional. If enabled, notifications will be sent when a picking is in the "Cancelled" state
