This module adds hook points in stock_move._action_done() in order
to add more flexibility.

* Adds a method to influence the criteria to determine if the application
  should create a backorder from the existing picking.
