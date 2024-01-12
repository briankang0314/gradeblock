import React, { useState } from 'react';

const OwnershipTransfer = ({ tezos, contractAddress }) => {
  const [newOwnerAddress, setNewOwnerAddress] = useState('');
  const [loading, setLoading] = useState(false);

  const transferOwnership = async () => {
    setLoading(true);
    try {
      const contract = await tezos.wallet.at(contractAddress);
      const operation = await contract.methods.changeOwnership(newOwnerAddress).send();
      await operation.confirmation();
      alert('Ownership transfer initiated successfully!');
    } catch (error) {
      console.error('Failed to transfer ownership:', error);
      alert('Failed to transfer ownership.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>Transfer Ownership</h3>
      <input
        type="text"
        value={newOwnerAddress}
        onChange={(e) => setNewOwnerAddress(e.target.value)}
        placeholder="Enter new owner address"
      />
      <button onClick={transferOwnership} disabled={loading}>
        {loading ? 'Transferring...' : 'Transfer Ownership'}
      </button>
    </div>
  );
};

export default OwnershipTransfer;
