# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# @author Pierre Verkest <pierreverkest84@gmail.com>
# @author Matthias Barkat <matthias.barkat@foodles.co>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from datetime import datetime, timedelta
from typing import Dict, List, Optional

from odoo import _, api, models
from odoo.exceptions import ValidationError

from .weekday import WeekdaysEnum


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def add_working_days_to_date(
        self,
        date: datetime,
        working_days: int,
        include_given_date: bool,
    ) -> datetime:
        """
        Apply a delta to a date based on the working days calendar including global
        leaves. The returned date will be delta working days later (or before if
        delta is negative) at the same time as the input date.

        :param date: The date to apply the delta to.
        :param working_days: The number of working days to add (or subtract) to the
                             date.
        :param include_given_date: Whether to include the given date in the
                                   calculation.
        :return: The date delta working days later (or before)
        """
        self.ensure_one()
        if working_days == 0:
            # No need to do anything
            return date

        # If we are going forward in time and want to include the given date, we need to
        # set the time to the start of the day to account for intervals in this day.
        # When going backward in time and not wanting to include the given date, we need
        # to set the time to the start of the day as well, to avoid accounting for any
        # interval in this day.
        if (working_days > 0) == include_given_date:
            planned_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        # If we are going backwards in time and want to include the given date, we need
        # to set the time to the end of the day to account for intervals in this day.
        # When going forwards in time and not wanting to include the given date, we need
        # to set the time to the end of the day as well, to avoid accounting for any
        # interval in this day.
        else:
            planned_date = date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

        planned_date = self.plan_days(working_days, planned_date, compute_leaves=True)
        return planned_date.replace(hour=date.hour, minute=date.minute)

    @api.model
    def is_a_working_day(self, date: datetime) -> bool:
        """
        Check if the given date is a working day.

        If the date is a working day, then adding a working day to the date while
        including the given date will result in no changes.

        :param date: The date to check.
        :return: True if the date is a working day, False otherwise.
        """
        return self.add_working_days_to_date(date, 1, include_given_date=True) == date

    @api.model
    def compute_transfer_dates_from_target_sent_date(
        self,
        target_sent_date: datetime,
        lead_time: int,
        sender_calendar=None,
        receiver_calendar=None,
    ) -> Dict[str, datetime]:
        """
        Computes the actual sent date and the expected received date of a transfer given
        the lead time (in number of working days), and the working days
        calendar of both the sender and the receiver.
        Calculation is made from the target sent date in forward planning.

        The actual sent date is the next working day defined in the sender calendar
        following the target sent date.
        Then we add the lead time to the actual sent date based on the working days of
        the sender.
        Finally, the expected received date is the next working day defined in the
        receiver calendar.

        Example of how this method works:

        Working week days: Mo Tu We Th Fr Sa Su
          sender_calendar:  x  x     x  x  x  x
        receiver_calendar:  x  x  x  x  x     x

        Considering that we want to do a transfer from Wednesday and the lead time is
        2 days:
            1. The actual sent date is the next working day of the sender, which is
               Thursday.
            2. The target received date will be 3 working days of the sender later,
               which is Saturday.
            3. The expected received date is the next working day of the receiver, which
               is Sunday.
        Then, the actual sent date will be on Thursday and the expected received date
        will be on Sunday.

        Note: If either the sender or receiver calendar isn't specified, we consider the
              concerned location to work on every day of the week.

        :param target_sent_date: The date we want to send the transfer.
        :param lead_time: The lead time of the transfer.
        :param sender_calendar: The sender's working days calendar.
        :param receiver_calendar: The receiver's working days calendar.
        :return: {"actual_sent_date": datetime, "expected_received_date": datetime}
        """
        if lead_time < 0:
            raise ValidationError(_("The lead time must be a positive number."))
        day_delta = timedelta(days=1)

        actual_sent_date = target_sent_date
        if sender_calendar:
            actual_sent_date = sender_calendar.add_working_days_to_date(
                target_sent_date, 1, include_given_date=True
            )

        target_received_date = actual_sent_date + lead_time * day_delta
        if sender_calendar:
            target_received_date = sender_calendar.add_working_days_to_date(
                actual_sent_date, lead_time, include_given_date=False
            )

        expected_received_date = target_received_date
        if receiver_calendar:
            expected_received_date = receiver_calendar.add_working_days_to_date(
                target_received_date, 1, include_given_date=True
            )

        return {
            "actual_sent_date": actual_sent_date,
            "expected_received_date": expected_received_date,
        }

    @api.model
    def compute_transfer_dates_from_target_received_date(
        self,
        target_received_date: datetime,
        lead_time: int,
        sender_calendar=None,
        receiver_calendar=None,
    ) -> Dict[str, datetime]:
        """
        Computes the actual sent date and the expected received date of a transfer given
        the lead time (in number of working days), and the working days
        calendar of both the sender and the receiver.
        Calculation is made from the target received date in backward planning.

        The actual received date is the previous working day defined in the receiver
        calendar before the target received date.
        Finally, we subtract the lead time from the actual received date based on the
        working days of the receiver.

        Example of how this method works:

        Working week days: Mo Tu We Th Fr Sa Su
          sender_calendar:  x  x     x  x  x  x
        receiver_calendar:  x  x  x  x  x     x

        Considering that we want to receive the transfer by Saturday and the lead time
        is 2 days:
            1. The expected received date is the previous working day of the receiver,
               which is Friday.
            2. The actual sent date will be 2 working days of the receiver before,
               which is Tuesday.
        Then, the actual sent date will be on Tuesday and the expected received date
        will be on Friday.

        Note: If either the sender or receiver calendar isn't specified, we consider the
              concerned location to work on every day of the week.

        :param target_received_date: The date we want to receive the transfer.
        :param lead_time: The lead time of the transfer.
        :param sender_calendar: The sender's working days calendar.
        :param receiver_calendar: The receiver's working days calendar.
        :return: {"actual_sent_date": datetime, "expected_received_date": datetime}
        """
        if lead_time < 0:
            raise ValidationError(_("The lead time must be a positive number."))
        day_delta = timedelta(days=1)

        actual_received_date = target_received_date
        if receiver_calendar:
            actual_received_date = receiver_calendar.add_working_days_to_date(
                actual_received_date, -1, include_given_date=True
            )

        actual_sent_date = actual_received_date - lead_time * day_delta
        if sender_calendar:
            actual_sent_date = sender_calendar.add_working_days_to_date(
                actual_received_date, -lead_time, include_given_date=False
            )

        return {
            "actual_sent_date": actual_sent_date,
            "expected_received_date": actual_received_date,
        }

    @api.model
    def _compute_inverted_lead_times_by_day(
        self,
        lead_times_by_day: Dict[
            WeekdaysEnum,
            List[int],
        ],
    ) -> Dict[WeekdaysEnum, List[int]]:
        """
        Converts the reception lead times by weekday to order lead times by weekday.

        Example:

                         Week days: Mo Tu We Th Fr Sa Su
                 lead_times_by_day:     1  2     3
                                        2  3     4
        inverted_lead_times_by_day:  3  4  1  2  2  3

        :param lead_times_by_day: The number of days from the order weekday to the
                                  reception date
        :return: The number of days from the reception weekday to the order date
        """
        inverted_lead_times_by_day = {day: set() for day in WeekdaysEnum}
        for order_day, lead_times in lead_times_by_day.items():
            for lead_time in lead_times:
                received_day = WeekdaysEnum.from_weekday(
                    order_day.weekday() + lead_time
                )
                inverted_lead_times_by_day[received_day].add(lead_time)
        return {
            day: sorted(lead_times)
            for day, lead_times in inverted_lead_times_by_day.items()
        }

    @api.model
    def _compute_possible_order_dates_from_target_received_date(
        self,
        lead_times_by_day: Dict[
            WeekdaysEnum,
            List[int],
        ],
        target_received_date: datetime,
        supplier_calendar=None,
    ) -> List[datetime]:
        """
        Using the target received date,lead times by weekday, and supplier calendar.
        To return possible order dates.

        Example:

        We wish to receive the order on a Saturday and the lead times are:

                         Week days: Mo Tu We Th Fr Sa Su
                 Supplier calendar:  x  x     x  x  x  x
                 lead_times_by_day:  3  3  3  3  3  3  3
              possible_order_dates:                Tu

        :param lead_times_by_day: The number of days from the order weekday to the
                                    reception date
        :param target_received_date: The date we want to receive the order.
        :param supplier_calendar: The supplier's working days calendar.

        """
        possible_order_dates = set()
        if not supplier_calendar:
            inverted_lead_times_by_day = self._compute_inverted_lead_times_by_day(
                lead_times_by_day
            )
            inverted_lead_times = inverted_lead_times_by_day.get(
                WeekdaysEnum.from_weekday(target_received_date.weekday()), []
            )
            return sorted(
                {
                    target_received_date - timedelta(days=inverted_lead_time)
                    for inverted_lead_time in inverted_lead_times
                }
            )

        for day, lead_times in lead_times_by_day.items():
            for lead_time in lead_times:
                target_order_date = supplier_calendar.add_working_days_to_date(
                    target_received_date, -lead_time, include_given_date=False
                )
                if target_order_date.weekday() == day.weekday():
                    possible_order_dates.add(target_order_date)
        return sorted(possible_order_dates)

    @api.model
    def compute_order_dates_from_target_received_date(
        self,
        target_received_date: datetime,
        lower_acceptable_received_date: datetime,
        lead_times_by_day: Dict[
            WeekdaysEnum,
            List[int],
        ],
        supplier_calendar=None,
        destination_calendar=None,
    ) -> Optional[Dict[str, datetime]]:
        """
        Computes the actual order date and the expected delivery date of an order given
        the lead times (in number of days) by day of the week, and the working days
        calendar of both the supplier and the destination.
        Calculation is made from the target received date in backward planning.

        We are looking for the actual order date and the expected delivery day such
        that:
            - The actual order date is a working day of the supplier.
            - The actual order date is a day that is allowed for ordering to the
              supplier.
            - The expected delivery date is a working day of the destination.
            - The expected delivery date is not before the lower acceptable received
              date.
            - The expected delivery date is as close as possible to the target received
              date.

        Example of how this method works:

           Working week days: Mo Tu We Th Fr Sa Su
           supplier_calendar:  x  x     x  x  x  x
         supplier_order_days:        x     x
         supplier_lead_times:     1  2     3
                                  2  3     4
        destination_calendar:  x  x  x     x     x

        Considering that we want to receive the order by Saturday:
            0. We compute the inverted lead times by day of the week.
            1. The expected received date is the previous working day of the
               destination, which is Friday.
            2. The inverted lead time on Friday is 2, so the actual order date will be 2
               days before, which is Wednesday.
            3. Wednesday is not a working day of the supplier, so we set the expected
               received date to the destination working day prior to Friday, which is
               Thursday.
            4. The inverted lead time on Thursday is 2, so the actual order date will be
                2 days before, which is Tuesday.
            5. Tuesday is a working day of the supplier, so the actual order date will
               be Tuesday and the expected delivery date will be Thursday.

        Note: If either the supplier or destination calendar isn't specified, we
              consider the concerned location to work on every day of the week.

        :param target_received_date: The date we want to receive the order.
        :param lower_acceptable_received_date: The lower acceptable date for the
            received date.
        :param lead_times_by_day: The lead times by day of the week.
        :param supplier_calendar: The supplier's working days calendar.
        :param destination_calendar: The destination's working days calendar.
        :return: {"actual_order_date": datetime, "expected_delivery_date": datetime} or
                 None if no valid order date is found.
        """
        inverted_lead_times_by_day = self._compute_inverted_lead_times_by_day(
            lead_times_by_day
        )

        expected_received_date = target_received_date
        if destination_calendar:
            expected_received_date = destination_calendar.add_working_days_to_date(
                expected_received_date, -1, include_given_date=True
            )
        actual_order_date: Optional[datetime] = None
        while expected_received_date >= lower_acceptable_received_date:
            expected_received_weekday = WeekdaysEnum.from_weekday(
                expected_received_date.weekday()
            )
            inverted_lead_times = inverted_lead_times_by_day[expected_received_weekday]
            for lead_time in inverted_lead_times:
                target_order_date = expected_received_date - timedelta(days=lead_time)
                if not supplier_calendar or supplier_calendar.is_a_working_day(
                    target_order_date
                ):
                    actual_order_date = target_order_date
                    break
            if actual_order_date:
                break
            if destination_calendar:
                expected_received_date = destination_calendar.add_working_days_to_date(
                    expected_received_date, -1, include_given_date=False
                )
            else:
                expected_received_date -= timedelta(days=1)
        if not actual_order_date:
            return None

        return {
            "actual_order_date": actual_order_date,
            "expected_delivery_date": expected_received_date,
        }

    @api.model
    def compute_order_dates_from_target_received_date_working_days(
        self,
        target_received_date: datetime,
        lower_acceptable_received_date: datetime,
        lead_times_by_day: Dict[
            WeekdaysEnum,
            List[int],
        ],
        supplier_calendar=None,
        destination_calendar=None,
    ) -> Optional[Dict[str, datetime]]:
        """
        Computes the actual order date and the expected delivery date of an order given
        the lead times (in number of working days) by day of the week, and the working days
        calendar of both the supplier and the destination.
        ! Calculation is made from the target received date in backward planning.

        We are looking for the actual order date and the expected delivery day such
        that:
            - The actual order date is a working day of the supplier.
            - The actual order date is a day that is allowed for ordering to the
              supplier.
            - The expected delivery date is a working day of the destination.
            - The expected delivery date is not before the lower acceptable received
              date.
            - The expected delivery date is as close as possible to the target received
              date.

        Example of how this method works:

           Working week days: Mo Tu We Th Fr Sa Su
           supplier_calendar:  x  x     x  x  x
         supplier_order_days:  x  x     x  x
         supplier_lead_times:  2  2  2  2  2

        Considering that we want to receive the order by Saturday:
            1. We first find a possible delivery date for the warehouse
            2. We compute the possible order dates for this possible delivery date
               using the supplier calendar and the lead times by day
            3. We select the latest possible order date

        """
        actual_order_date = None
        expected_received_date = target_received_date
        while expected_received_date.date() >= lower_acceptable_received_date.date():
            if destination_calendar and not destination_calendar.is_a_working_day(
                expected_received_date
            ):
                expected_received_date -= timedelta(days=1)
                continue

            possible_order_dates = (
                self._compute_possible_order_dates_from_target_received_date(
                    lead_times_by_day, expected_received_date, supplier_calendar
                )
            )
            if not possible_order_dates:
                expected_received_date -= timedelta(days=1)
                continue

            actual_order_date = possible_order_dates[-1]
            break

        if not actual_order_date:
            return None

        return {
            "actual_order_date": actual_order_date,
            "expected_delivery_date": expected_received_date,
        }
