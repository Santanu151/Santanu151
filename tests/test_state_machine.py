import unittest

from app.state_machine import CallContext, CallStage, CallStateMachine


class TestCallStateMachine(unittest.TestCase):
    def test_happy_path_booking(self) -> None:
        sm = CallStateMachine()
        ctx = CallContext(lead_name="Sam", company="Acme")

        r1 = sm.next(ctx, "")
        self.assertEqual(r1.stage, CallStage.QUALIFY)

        r2 = sm.next(ctx, "yes")
        self.assertEqual(r2.stage, CallStage.BOOKING)

        r3 = sm.next(ctx, "schedule it")
        self.assertEqual(r3.stage, CallStage.END)
        self.assertTrue(r3.should_hangup)
        self.assertTrue(ctx.meeting_booked)

    def test_opt_out(self) -> None:
        sm = CallStateMachine()
        ctx = CallContext()
        r = sm.next(ctx, "remove me from your list")
        self.assertEqual(r.stage, CallStage.END)
        self.assertTrue(ctx.do_not_call)


if __name__ == "__main__":
    unittest.main()
