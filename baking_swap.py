import smartpy as sp


@sp.module
def main():
    class BakingSwap(sp.Contract):
        """A contract that takes tez deposits and pays interest.

        The deposited funds cannot leave the contract, but the administrator can
        delegate them for baking.

        In more detail:

        - The administrator funds the contract with collateral.

        - The administrator publishes an offer: a rate (in basis points) and a
        duration (in days).

        - For each deposit the amount to be paid out and the due date are recorded.
        The corresponding amount of collateral is locked up.

        - At maturity the deposit plus interest can be withdrawn.
        """

        def __init__(self, admin, initialRate, initialDuration):
            """Constructor

            Args:
                admin (sp.address): admin of the contract.
                initialRate (sp.nat): Basis points to compute the interest.
                initialDuration (sp.nat): Number of days before a deposit can be
                    withdrawn.
            """
            self.data.admin = admin
            self.data.collateral = sp.mutez(0)
            self.data.ledger = {}
            self.data.rate = initialRate
            self.data.duration = initialDuration

        # Admin-only entrypoints

        @sp.entrypoint
        def delegate(self, public_key_hash):
            """Admin-only. Delegate the contract's balance to the admin.

            Args:
                public_key_hash (sp.key_hash): public key hash of the admin.
            """
            assert sp.sender == self.data.admin
            assert sp.amount == sp.mutez(0)
            assert sp.sender == sp.to_address(sp.implicit_account(public_key_hash))
            sp.set_delegate(sp.Some(public_key_hash))

        @sp.entrypoint
        def collateralize(self):
            """Admin-only. Provide tez as collateral for interest to be paid."""
            assert sp.sender == self.data.admin
            self.data.collateral += sp.amount

        @sp.entrypoint
        def uncollateralize(self, amount, receiver):
            """Admin-only. Withdraw collateral.

            Transfer `amount` mutez to admin if it doesn't exceed collateral.

            Args:

                amount (sp.mutez): Amount to be removed from the collateral.
            """
            assert sp.sender == self.data.admin
            # Explicitly fails for insufficient collateral.
            assert amount <= self.data.collateral, "insufficient collateral"
            self.data.collateral -= amount
            sp.send(receiver, amount)

        @sp.entrypoint
        def set_offer(self, rate, duration):
            """Admin-only. Set the current offer: interest rate (in basis points)
            and duration.

            Args:
                rate (sp.nat): Basis points to compute the interest.
                duration (sp.nat): Number of days before a deposit can be withdrawn.
            """
            assert sp.sender == self.data.admin
            assert sp.amount == sp.mutez(0)
            self.data.rate = rate
            self.data.duration = duration

        # Permissionless entrypoints

        @sp.entrypoint
        def deposit(self, rate, duration):
            """Deposit tez. The current offer has to be repeated in the parameters.

            Args:
                rate (sp.nat): Basis points to compute the interest.
                duration (sp.nat): Number of days before a deposit can be withdrawn.
            """
            assert self.data.rate >= rate
            assert self.data.duration <= duration
            assert not self.data.ledger.contains(sp.sender)

            # Compute interest to be paid.
            interest = sp.split_tokens(sp.amount, self.data.rate, 10_000)
            self.data.collateral -= interest

            # Record the payment to be made.
            self.data.ledger[sp.sender] = sp.record(
                amount=sp.amount + interest,
                due=sp.add_days(sp.now, self.data.duration),
            )

        @sp.entrypoint
        def withdraw(self, receiver):
            """Withdraw tez at maturity."""
            assert sp.amount == sp.mutez(0)
            entry = self.data.ledger.get(sp.sender, error="NoDeposit")
            assert sp.now >= entry.due
            sp.send(receiver, entry.amount)
            del self.data.ledger[sp.sender]


@sp.module
def testing():
    class Receiver(sp.Contract):
        @sp.entrypoint
        def default(self):
            pass


if "templates" not in __name__:
    admin = sp.test_account("Admin")
    non_admin = sp.test_account("non_admin")
    voting_powers = {
        admin.public_key_hash: 0,
    }

    @sp.add_test(name="Baking swap basic scenario", is_default=True)
    def basic_scenario():
        scenario = sp.test_scenario(main)
        scenario.h1("Baking Swap")
        c = main.BakingSwap(admin.address, 700, 365)
        scenario += c

        c.delegate(admin.public_key_hash).run(sender=admin, voting_powers=voting_powers)

    @sp.add_test(name="Full")
    def test():
        sc = sp.test_scenario([main, testing])
        sc.h1("Full test")
        sc.h2("Origination")
        c = main.BakingSwap(admin.address, 0, 10000)
        sc += c
        sc.h2("Delegator")
        delegator = testing.Receiver()
        sc += delegator
        sc.h2("Admin receiver")
        admin_receiver = testing.Receiver()
        sc += admin_receiver

        sc.h2("delegate")
        c.delegate(admin.public_key_hash).run(sender=admin, voting_powers=voting_powers)
        sc.verify(c.baker == sp.some(admin.public_key_hash))
        sc.h3("Failures")
        c.delegate(admin.public_key_hash).run(
            sender=non_admin,
            voting_powers=voting_powers,
            valid=False,
            exception="WrongCondition: sp.sender == self.data.admin",
        )
        c.delegate(admin.public_key_hash).run(
            sender=admin,
            amount=sp.mutez(1),
            voting_powers=voting_powers,
            valid=False,
            exception="WrongCondition: sp.amount == sp.tez(0)",
        )
        c.delegate(non_admin.public_key_hash).run(
            sender=admin,
            voting_powers=voting_powers,
            valid=False,
            exception="WrongCondition: sp.sender == sp.to_address(sp.implicit_account(params))",
        )

        sc.h2("collateralize")
        c.collateralize().run(sender=admin, amount=sp.tez(500))
        sc.verify(c.data.collateral == sp.tez(500))
        sc.h3("Failures")
        c.collateralize().run(
            sender=non_admin,
            amount=sp.tez(500),
            valid=False,
            exception="WrongCondition: sp.sender == self.data.admin",
        )

        sc.h2("set_offer")
        c.set_offer(rate=1000, duration=365).run(sender=admin)
        sc.h3("Failures")
        c.set_offer(rate=1000, duration=365).run(
            sender=non_admin,
            valid=False,
            exception="WrongCondition: sp.sender == self.data.admin",
        )
        c.set_offer(rate=1000, duration=365).run(
            sender=admin,
            amount=sp.mutez(1),
            valid=False,
            exception="WrongCondition: sp.amount == sp.tez(0)",
        )

        sc.h2("deposit")
        c.deposit(rate=1000, duration=365).run(
            sender=delegator.address, amount=sp.tez(100)
        )
        sc.verify(c.data.collateral == sp.tez(490))
        sc.verify(
            c.data.ledger[delegator.address]
            == sp.record(amount=sp.tez(110), due=sp.timestamp(365 * 24 * 3600))
        )
        sc.h3("Failures")
        c.deposit(rate=1001, duration=365).run(
            sender=delegator.address,
            amount=sp.tez(100),
            valid=False,
            exception="WrongCondition: self.data.rate >= params.rate",
        )
        c.deposit(rate=1000, duration=364).run(
            sender=delegator.address,
            amount=sp.tez(100),
            valid=False,
            exception="WrongCondition: self.data.duration <= params.duration",
        )
        c.deposit(rate=1000, duration=365).run(
            sender=delegator.address,
            amount=sp.tez(100),
            valid=False,
            exception="WrongCondition: not (self.data.ledger.contains(sp.sender))",
        )

        sc.h2("uncollateralize")
        sc.h3("Failures")
        c.uncollateralize(amount=sp.tez(500), receiver=admin_receiver.address).run(
            sender=admin, valid=False, exception="insufficient collateral"
        )
        c.uncollateralize(amount=sp.tez(490), receiver=admin_receiver.address).run(
            sender=non_admin,
            valid=False,
            exception="WrongCondition: sp.sender == self.data.admin",
        )
        sc.h3("Valid")
        c.uncollateralize(amount=sp.tez(490), receiver=admin_receiver.address).run(
            sender=admin
        )
        sc.verify(c.data.collateral == sp.tez(0))
        sc.verify(admin_receiver.balance == sp.tez(490))

        sc.h2("withdraw")
        sc.h3("Failures")
        c.withdraw(delegator.address).run(
            sender=delegator.address,
            amount=sp.mutez(1),
            now=sp.timestamp(365 * 24 * 3600),
            valid=False,
            exception="WrongCondition: sp.amount == sp.tez(0)",
        )
        c.withdraw(delegator.address).run(
            sender=delegator.address,
            now=sp.timestamp(365 * 24 * 3600 - 1),
            valid=False,
            exception="WrongCondition: sp.now >= entry.due",
        )
        sc.h3("Valid")
        c.withdraw(delegator.address).run(
            sender=delegator.address, now=sp.timestamp(365 * 24 * 3600)
        )
        sc.verify(delegator.balance == sp.tez(110))
        sc.verify(~c.data.ledger.contains(delegator.address))
        sc.h3("Failures")
        c.withdraw(delegator.address).run(
            sender=delegator.address,
            valid=False,
            now=sp.timestamp(365 * 24 * 3600),
            exception="NoDeposit",
        )

    # @sp.add_test(name="Mutation", is_default=False)
    # def test():
    #     s = sp.test_scenario()
    #     with s.mutation_test() as mt:
    #         mt.add_scenario("Full")
