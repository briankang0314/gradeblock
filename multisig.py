import smartpy as sp

@sp.module
def main():
    class Multisig(sp.Contract):
        def __init__(self, signatories, threshold):
            # Initialize the Multisig contract with signatories and the proposal approval threshold
            self.init(
                # List of addresses that are authorized to propose and vote on changes
                signatories=signatories,
                # Minimum number of votes required for a proposal to be approved
                threshold=threshold,
                # Mapping of proposal IDs to their respective details and votes
                proposals=sp.map(tkey=sp.TNat, tvalue=sp.TRecord(votes=sp.TSet(sp.TAddress), details=sp.TBytes))
            )

        @sp.entry_point
        def propose_change(self, proposal_details):
            # Allows a signatory to propose a change
            # Verifies that the sender is an authorized signatory
            sp.verify(sp.sender in self.data.signatories, "Unauthorized: Sender is not a signatory.")
            # Generates a new proposal ID and records the proposal details
            proposal_id = sp.len(self.data.proposals)
            self.data.proposals[proposal_id] = sp.record(votes=sp.set(), details=proposal_details)

        @sp.entry_point
        def vote_on_change(self, proposal_id):
            # Allows signatories to vote on an existing proposal
            # Checks if the sender is a signatory and if the proposal exists
            sp.verify(sp.sender in self.data.signatories, "Unauthorized: Sender is not a signatory.")
            sp.verify(self.data.proposals.contains(proposal_id), "Proposal not found.")
            # Adds the sender's vote to the proposal
            self.data.proposals[proposal_id].votes.add(sp.sender)

        @sp.entry_point
        def execute_change(self, proposal_id):
            # Executes a proposal if it has reached the required number of votes
            # Verifies the existence of the proposal and that it has enough votes
            sp.verify(self.data.proposals.contains(proposal_id), "Proposal not found.")
            proposal = self.data.proposals[proposal_id]
            sp.verify(sp.len(proposal.votes) >= self.data.threshold, "Not enough votes to execute the proposal.")
            # Execute the proposed change (implementation depends on the specific use case)
            # Example: call update_record function of the AcademicRecord contract
            # Once executed, the proposal is removed from the proposals mapping
            del self.data.proposals[proposal_id]

        @sp.entry_point
        def execute_change(self, proposal_id, academic_record_contract):
            # Additional implementation of execute_change with an external contract reference
            sp.verify(self.data.proposals.contains(proposal_id), "Proposal not found.")
            proposal = self.data.proposals[proposal_id]
            sp.verify(sp.len(proposal.votes) >= self.data.threshold, "Not enough votes.")
            # Executes the proposed change in the AcademicRecord contract
            sp.transfer(proposal.details, sp.mutez(0), sp.contract(sp.TBytes, academic_record_contract, entry_point="update_record").open_some())
            # Remove the proposal post-execution
            del self.data.proposals[proposal_id]

        @sp.entry_point
        def add_signatory(self, signatory):
            # Allows existing signatories to add a new signatory
            sp.verify(sp.sender in self.data.signatories, "Unauthorized: Only signatories can add others.")
            # Add the new signatory to the list of signatories
            self.data.signatories.add(signatory)

        @sp.entry_point
        def remove_signatory(self, signatory):
            # Allows existing signatories to remove a signatory
            sp.verify(sp.sender in self.data.signatories, "Unauthorized: Only signatories can remove others.")
            # Remove the specified signatory from the list
            self.data.signatories.remove(signatory)

        @sp.entry_point
        def change_threshold(self, new_threshold):
            # Allows signatories to change the threshold of votes required to approve a proposal
            sp.verify(sp.sender in self.data.signatories, "Unauthorized: Only signatories can change the threshold.")
            # Validate the new threshold and update it
            sp.verify(new_threshold > 0 and new_threshold <= sp.len(self.data.signatories), "Invalid threshold.")
            self.data.threshold = new_threshold


@sp.add_test(name="Multisig Contract Test")
def test_multisig():
    scenario = sp.test_scenario()
    scenario.h1("Multisig Contract Test")

    # Initialize test accounts
    admin = sp.test_account("Administrator")
    signatory1 = sp.test_account("Signatory1")
    signatory2 = sp.test_account("Signatory2")

    # Instantiate the contract
    multisig_contract = Multisig(signatories=[admin.address, signatory1.address], threshold=2)
    scenario += multisig_contract

    # Test proposing a change
    multisig_contract.propose_change(proposal_details=sp.pack("Change 1")).run(sender=admin)

    # Test voting on the proposed change
    multisig_contract.vote_on_change(proposal_id=0).run(sender=signatory1)

    # Test executing the change (this should fail due to insufficient votes)
    multisig_contract.execute_change(proposal_id=0).run(sender=admin, valid=False)

    # Add another vote
    multisig_contract.vote_on_change(proposal_id=0).run(sender=signatory2)

    # Test executing the change (this should succeed)
    multisig_contract.execute_change(proposal_id=0).run(sender=admin)
