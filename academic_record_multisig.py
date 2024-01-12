import smartpy as sp

@sp.module
def main():
    class AcademicRecordWithMultisig(sp.Contract):
        # Constructor for initializing the AcademicRecordWithMultisig contract
        def __init__(self, student_identifier, record_details, owner_address, signatories, threshold):
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
                # Reference to the associated Multisig contract for managing approvals
                multisig_contract=Multisig(signatories, threshold)
            )

        @sp.entry_point
        def propose_update_record(self, proposal_details, proposal_id):
            # Validate the proposal details
            self.validate_input(proposal_details)
            # Create a proposal in the Multisig contract for updating the academic record
            self.data.multisig_contract.propose_change(proposal_details, proposal_id)

        @sp.entry_point
        def execute_approved_update(self, proposal_id):
            # Verify that the proposal has the required approvals in the Multisig contract
            self.verify_multisig(proposal_id)
            # Apply the approved changes to the academic record
            new_details = self.data.multisig_contract.get_proposal_details(proposal_id)
            
            # Validate the new details and update the record
            self.validate_input(new_details)
            self.data.record_details = new_details
            self.update_timestamps()
            self.data.record_hash = self.generate_hash(new_details)

            # Optionally, remove the executed proposal from the Multisig contract
            self.data.multisig_contract.remove_proposal(proposal_id)

        # Utility function to generate a hash of the record details
        def generate_hash(self, details):
            # Generate a hash for integrity verification of the record
            return sp.blake2b(sp.pack(details))

        # Utility function to validate input data
        def validate_input(self, input_data):
            # Ensure that the input data is not empty or null
            sp.verify(input_data is not None, "Input data cannot be empty.")

        # Utility function to update timestamps
        def update_timestamps(self, update_creation=False):
            # Update creation timestamp if specified
            if update_creation:
                self.data.creation_timestamp = sp.timestamp_from_utc_now()
            # Always update the last updated timestamp
            self.data.last_updated_timestamp = sp.timestamp_from_utc_now()

        # Utility function to verify multisig approval for a proposal
        def verify_multisig(self, proposal_id):
            # Check if the proposal is approved in the Multisig contract
            sp.verify(self.data.multisig_contract.is_proposal_approved(proposal_id), "Proposal not yet approved.")


@sp.add_test(name="Academic Record With Multisig Test")
def test_academic_record_with_multisig():
    scenario = sp.test_scenario()
    scenario.h1("Academic Record With Multisig Contract Test")

    # Initialize test accounts
    admin = sp.test_account("Administrator")
    signatory1 = sp.test_account("Signatory1")
    signatory2 = sp.test_account("Signatory2")
    student = sp.test_account("Student")

    # Instantiate the contracts
    multisig_contract = Multisig(signatories=[admin.address, signatory1.address, signatory2.address], threshold=2)
    scenario += multisig_contract

    academic_record_multisig_contract = AcademicRecordWithMultisig(student_identifier="123456", record_details={"courses": []}, owner_address=admin.address, signatories=[admin.address, signatory1.address, signatory2.address], threshold=2)
    scenario += academic_record_multisig_contract

    # Test proposing and approving a record update
    new_record_details = {"courses": [{"name": "Physics", "grade": "B"}]}
    academic_record_multisig_contract.propose_update_record(proposal_details=sp.pack(new_record_details), proposal_id=0).run(sender=admin)
    multisig_contract.vote_on_change(proposal_id=0).run(sender=signatory1)
    multisig_contract.vote_on_change(proposal_id=0).run(sender=signatory2)

    # Test executing the approved record update
    academic_record_multisig_contract.execute_approved_update(proposal_id=0).run(sender=admin)
