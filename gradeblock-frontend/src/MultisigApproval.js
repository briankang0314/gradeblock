import React, { useState, useEffect } from 'react';

const MultisigApproval = ({ tezos, contractAddress }) => {
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProposals();
  }, []);

  const fetchProposals = async () => {
    setLoading(true);
    try {
      const contract = await tezos.wallet.at(contractAddress);
      const storage = await contract.storage();
      const proposalsData = await storage.proposals.getEntries(); // Adjust based on contract storage structure
      setProposals(proposalsData);
    } catch (error) {
      console.error('Failed to fetch proposals:', error);
    } finally {
      setLoading(false);
    }
  };

  const voteOnProposal = async (proposalId, approve) => {
    setLoading(true);
    try {
      const contract = await tezos.wallet.at(contractAddress);
      const operation = approve
        ? await contract.methods.approveProposal(proposalId).send()
        : await contract.methods.rejectProposal(proposalId).send();
      await operation.confirmation();
      alert('Vote submitted successfully!');
      fetchProposals(); // Refresh the proposals list
    } catch (error) {
      console.error('Failed to submit the vote:', error);
      alert('Failed to submit the vote.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>Pending Proposals</h3>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul>
          {proposals.map((proposal, index) => (
            <li key={index}>
              Proposal ID: {proposal.id}
              <button onClick={() => voteOnProposal(proposal.id, true)}>Approve</button>
              <button onClick={() => voteOnProposal(proposal.id, false)}>Reject</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default MultisigApproval;
