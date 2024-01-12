import React, { useState } from 'react';

const RecordUpdateProposal = ({ tezos, contractAddress }) => {
  const [newDetails, setNewDetails] = useState('');
  const [loading, setLoading] = useState(false);

  const submitProposal = async () => {
    setLoading(true);
    try {
      const contract = await tezos.wallet.at(contractAddress);
      const operation = await contract.methods.proposeUpdate(newDetails).send();
      await operation.confirmation();
      alert('Proposal submitted successfully!');
    } catch (error) {
      console.error('Failed to submit the proposal:', error);
      alert('Failed to submit the proposal.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>Propose Record Update</h3>
      <textarea
        value={newDetails}
        onChange={(e) => setNewDetails(e.target.value)}
        placeholder="Enter new record details"
      />
      <button onClick={submitProposal} disabled={loading}>
        {loading ? 'Submitting...' : 'Submit Proposal'}
      </button>
    </div>
  );
};

export default RecordUpdateProposal;
