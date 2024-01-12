import React, { useState } from 'react';

const RecordIntegrityVerification = ({ tezos, contractAddress }) => {
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const verifyRecordIntegrity = async () => {
    setLoading(true);
    try {
      const contract = await tezos.wallet.at(contractAddress);
      const storage = await contract.storage();
      // Assuming 'verifyRecord' is a method in your contract for integrity check
      const result = await storage.verifyRecord(); // Adjust method and parameters as needed
      setVerificationResult(result);
    } catch (error) {
      console.error('Failed to verify the record:', error);
      setVerificationResult('Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>Verify Record Integrity</h3>
      <button onClick={verifyRecordIntegrity} disabled={loading}>
        {loading ? 'Verifying...' : 'Verify Integrity'}
      </button>
      {verificationResult && <p>Verification Result: {verificationResult}</p>}
    </div>
  );
};

export default RecordIntegrityVerification;
