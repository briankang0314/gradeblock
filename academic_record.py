import smartpy as sp

@sp.module
def main():
    class AcademicRecord(sp.Contract):
        # Constructor for initializing the AcademicRecord contract
        def __init__(self, student_identifier, record_details, owner_address, required_approvals):
            # Initialize the contract's storage
            self.init(
                # Unique identifier for the student (e.g., student ID or hash)
                student_identifier=student_identifier,
                # Detailed academic record (e.g., courses, grades)
                record_details=record_details,
                # Timestamp of record creation
                creation_timestamp=sp.timestamp_from_utc_now(),
                # Timestamp for the last update, initialized as None
                last_updated_timestamp=sp.none,
                # Hash of the record for integrity verification
                record_hash=self.generate_hash(record_details),
                # Address of the record's owner (e.g., educational institution)
                owner=owner_address,
                # Mapping of proposal IDs to their details for multisig functionality
                proposals=sp.map(tkey=sp.TNat, tvalue=sp.TRecord(approvals=sp.TSet(sp.TAddress), proposed_changes=sp.TBytes)),
                # Number of approvals required for a proposal to pass
                required_approvals=required_approvals
            )

        # Entry point for updating the academic record
        @sp.entry_point
        def update_record(self, params):
            # Validate the new details and check multisig approval before updating
            self.validate_input(params.new_details)
            self.verify_multisig(params.proposal_id)

            # Update the record details, timestamps, and hash
            self.data.record_details = params.new_details
            self.update_timestamps()
            new_hash = self.generate_hash(params.new_details)
            sp.verify(new_hash != self.data.record_hash, "No changes detected.")
            self.data.record_hash = new_hash

        # Entry point for retrieving the academic record
        @sp.entry_point
        def retrieve_record(self, params):
            # Check if the requestor is authorized (owner or an approved signatory)
            sp.verify(sp.sender == self.data.owner or sp.sender in self.data.proposals[params.proposal_id].approvals, "Access Denied.")
            # Return the record details
            sp.result(self.data.record_details)

        # Entry point for verifying the integrity of the academic record
        @sp.entry_point
        def verify_record(self, params):
            # Compute the hash of the record details and compare with the stored hash
            computed_hash = self.generate_hash(self.data.record_details)
            sp.verify(computed_hash == self.data.record_hash, "Record integrity check failed.")
        
        # Entry point for changing the ownership of the academic record
        @sp.entry_point
        def change_ownership(self, new_owner_address, proposal_id):
            # Validate the new owner address and verify multisig approval
            self.validate_input(new_owner_address)
            self.verify_multisig(proposal_id)

            # Change the ownership and update timestamps
            sp.verify(new_owner_address != sp.none, "Invalid new owner address.")
            self.data.owner = new_owner_address
            self.update_timestamps(update_creation=True)

        # Utility function to generate a hash of the record details
        def generate_hash(self, details):
            return sp.blake2b(sp.pack(details))

        # Entry point to propose an update to the academic record
        @sp.entry_point
        def propose_update(self, proposal_details, proposal_id):
            # Verify the sender's authorization and create a new proposal
            sp.verify(sp.sender == self.data.owner, "Unauthorized: Only the owner can propose updates.")
            self.data.proposals[proposal_id] = sp.record(approvals=sp.set(), proposed_changes=proposal_details)

        # Entry point for signatories to approve a proposed update
        @sp.entry_point
        def approve_update(self, proposal_id):
            # Verify the existence of the proposal and add the sender's approval
            sp.verify(self.data.proposals.contains(proposal_id), "Proposal not found.")
            self.data.proposals[proposal_id].approvals.add(sp.sender)

        # Entry point to execute an update to the academic record upon proposal approval
        @sp.entry_point
        def execute_update(self, proposal_id):
            # Verify the proposal's approval and apply the changes to the record
            self.verify_multisig(proposal_id)
            new_details = self.data.proposals[proposal_id].proposed_changes
            self.data.record_details = new_details
            self.data.last_updated_timestamp = sp.timestamp_from_utc_now()
            self.data.record_hash = self.generate_hash(new_details)
            # Optionally, remove the executed proposal
            del self.data.proposals[proposal_id]

        # Utility function to validate input data
        def validate_input(self, input_data):
            sp.verify(input_data is not None, "Input data is empty.")

        # Utility function to update timestamps
        def update_timestamps(self, update_creation=False):
            # Update creation timestamp only if specified
            if update_creation:
                self.data.creation_timestamp = sp.timestamp_from_utc_now()
            # Always update the last updated timestamp
            self.data.last_updated_timestamp = sp.timestamp_from_utc_now()

        # Utility function to verify multisig approval for a proposal
        def verify_multisig(self, proposal_id):
            # Check the proposal's existence and if it has the required number of approvals
            sp.verify(self.data.proposals.contains(proposal_id), "Proposal not found.")
            proposal = self.data.proposals[proposal_id]
            sp.verify(sp.len(proposal.approvals) >= self.data.required_approvals, "Insufficient approvals for the proposal.")


@sp.add_test(name="Academic Record Test")
def test_academic_record():
    scenario = sp.test_scenario()
    scenario.h1("Academic Record Contract Test")

    # Initialize test accounts
    admin = sp.test_account("Administrator")
    student = sp.test_account("Student")

    # Instantiate the contract
    academic_record_contract = AcademicRecord(student_identifier="123456", record_details={"courses": []}, owner_address=admin.address)
    scenario += academic_record_contract

    # Test updating academic records (this should succeed)
    new_record_details = {"courses": [{"name": "Math", "grade": "A"}]}
    academic_record_contract.update_record(new_details=new_record_details).run(sender=admin)

    # Test updating academic records (this should fail due to wrong sender)
    academic_record_contract.update_record(new_details=new_record_details).run(sender=student, valid=False)

    # Test retrieving the academic record
    academic_record_contract.retrieve_record().run(sender=admin)

    # Test changing ownership (this should succeed)
    academic_record_contract.change_ownership(new_owner_address=student.address).run(sender=admin)

    # Test changing ownership (this should fail due to wrong sender)
    academic_record_contract.change_ownership(new_owner_address=admin.address).run(sender=student, valid=False)
